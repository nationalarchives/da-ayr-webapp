import csv
import json
import logging
import os
import random
import subprocess  # nosec
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
sqs = boto3.client("sqs")
dynamodb = boto3.client("dynamodb")

DROID_COMMAND = os.environ["DROID_COMMAND"]
DROID_VERSION = os.environ["DROID_VERSION"]
DROID_TIMEOUT_SECONDS = int(os.getenv("DROID_TIMEOUT_SECONDS", "120"))
DDT_TEMP_CSV_BUCKET = os.environ["DDT_TEMP_CSV_BUCKET"]
TRACKING_TABLE_NAME = os.environ["TRACKING_TABLE_NAME"]
FINALISER_QUEUE_URL = os.environ["FINALISER_QUEUE_URL"]

STAGING_PREFIX = os.getenv("STAGING_PREFIX", "ayr-mds-staging")

DYNAMODB_TRANSACTION_MAX_ATTEMPTS = 10
DYNAMODB_TRANSACTION_BASE_DELAY_SECONDS = 0.05
DYNAMODB_TRANSACTION_MAX_DELAY_SECONDS = 1.0

FFID_METADATA_COLUMNS = [
    "FileId",
    "Extension",
    "PUID",
    "FormatName",
    "ExtensionMismatch",
    "FFID-Software",
    "FFID-SoftwareVersion",
    "FFID-BinarySignatureFileVersion",
    "FFID-ContainerSignatureFileVersion",
]


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    SQS-triggered DROID processor

    Expected SQS body:
    {
      "runId": "LEV-2-...",
      "series": "LEV 2",
      "consignmentReference": "TDR-2026-7333",
      "bucket": "ddt-temp-data-bucket",
      "key": "LEV 2/TDR-2026-7333/<fileId>",
      "fileId": "<fileId>",
      "extension": "pdf"
    }
    """
    if "Records" not in event:
        return process_message(event)

    batch_item_failures = []

    for record in event["Records"]:
        try:
            message = json.loads(record["body"])
            process_message(message)
        except Exception:
            logger.exception("Failed to process DROID SQS message")
            batch_item_failures.append({"itemIdentifier": record["messageId"]})

    return {"batchItemFailures": batch_item_failures}


def process_message(message: dict[str, Any]) -> dict[str, Any]:
    run_id = require_text(message, "runId")
    series = require_text(message, "series")
    consignment_reference = require_text(message, "consignmentReference")
    bucket = require_text(message, "bucket")
    key = require_text(message, "key")
    file_id = require_text(message, "fileId")
    extension = message.get("extension") or ""

    if is_file_already_complete(
        run_id=run_id,
        consignment_reference=consignment_reference,
        file_id=file_id,
    ):
        finaliser_triggered = trigger_finaliser_if_ready(
            run_id=run_id,
            series=series,
            consignment_reference=consignment_reference,
        )
        logger.info(
            "Skipping DROID because file is already COMPLETE. "
            "run_id=%s consignment=%s file_id=%s",
            run_id,
            consignment_reference,
            file_id,
        )
        return {
            "fileId": file_id,
            "skipped": True,
            "finaliserTriggered": finaliser_triggered,
        }

    ffid_metadata_row = identify_s3_object(
        bucket=bucket,
        key=key,
        file_id=file_id,
        extension=extension,
    )

    ffid_csv_key = upload_ffid_metadata_csv(
        series=series,
        consignment_reference=consignment_reference,
        file_id=file_id,
        row=ffid_metadata_row,
    )

    finaliser_triggered = (
        mark_file_complete_and_trigger_finaliser_if_consignment_ready(
            run_id=run_id,
            series=series,
            consignment_reference=consignment_reference,
            file_id=file_id,
        )
    )

    logger.info(
        "Finished DROID processing. run_id=%s consignment=%s file_id=%s "
        "ffid_csv=s3://%s/%s finaliser_triggered=%s",
        run_id,
        consignment_reference,
        file_id,
        DDT_TEMP_CSV_BUCKET,
        ffid_csv_key,
        finaliser_triggered,
    )

    return {
        "fileId": file_id,
        "ffidMetadataKey": ffid_csv_key,
        "finaliserTriggered": finaliser_triggered,
    }


def identify_s3_object(
    bucket: str,
    key: str,
    file_id: str,
    extension: str,
) -> dict[str, str]:
    local_path = build_local_path(file_id, extension)

    try:
        logger.info("Downloading s3://%s/%s to %s", bucket, key, local_path)
        s3.download_file(bucket, key, str(local_path))

        droid_row = run_droid(local_path)
        return map_droid_row_to_ffid_metadata(file_id, droid_row)
    finally:
        local_path.unlink(missing_ok=True)


def build_local_path(file_id: str, extension: str) -> Path:
    safe_file_id = "".join(
        char for char in file_id if char.isalnum() or char in "-_"
    )
    safe_extension = "".join(
        char for char in str(extension).lower() if char.isalnum()
    )

    if safe_extension:
        return Path("/tmp") / f"{safe_file_id}.{safe_extension}"  # nosec

    return Path("/tmp") / safe_file_id  # nosec


def run_droid(local_path: Path) -> dict[str, str]:
    # Lambda's filesystem is read-only except /tmp. DROID/Java may try to write
    # temp, cache or config files, so force those locations to /tmp.
    env = {
        **os.environ,
        "HOME": "/tmp",  # nosec
        "TMPDIR": "/tmp",  # nosec
        "XDG_CONFIG_HOME": "/tmp",  # nosec
        "XDG_CACHE_HOME": "/tmp",  # nosec
        "JAVA_TOOL_OPTIONS": " ".join(
            part
            for part in [
                os.environ.get("JAVA_TOOL_OPTIONS", ""),
                "-Duser.home=/tmp",
                "-Djava.io.tmpdir=/tmp",
            ]
            if part
        ),
    }

    logger.info("Running DROID command: %s %s", DROID_COMMAND, local_path)

    result = subprocess.run(  # nosec
        [DROID_COMMAND, str(local_path)],
        cwd="/opt/droid",
        env=env,
        capture_output=True,
        text=True,
        timeout=DROID_TIMEOUT_SECONDS,
        check=False,
    )

    logger.info("DROID returncode=%s", result.returncode)

    if result.stderr:
        logger.info("DROID stderr: %s", result.stderr[:4000])

    if result.returncode != 0:
        raise RuntimeError(
            f"DROID failed with return code {result.returncode}. stderr={result.stderr[:4000]}"
        )

    rows = list(csv.DictReader(StringIO(result.stdout)))

    if not rows:
        raise RuntimeError(
            f"DROID produced no CSV rows. stdout={result.stdout[:4000]}"
        )

    return rows[0]


def map_droid_row_to_ffid_metadata(
    file_id: str, droid_row: dict[str, str]
) -> dict[str, str]:
    return {
        "FileId": file_id,
        "Extension": droid_row.get("EXT", ""),
        "PUID": droid_row.get("PUID", ""),
        "FormatName": droid_row.get("FORMAT_NAME", ""),
        "ExtensionMismatch": droid_row.get("EXTENSION_MISMATCH", ""),
        "FFID-Software": "DROID",
        "FFID-SoftwareVersion": DROID_VERSION,
        "FFID-BinarySignatureFileVersion": "",
        "FFID-ContainerSignatureFileVersion": "",
    }


def upload_ffid_metadata_csv(
    series: str,
    consignment_reference: str,
    file_id: str,
    row: dict[str, str],
) -> str:
    output = StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=FFID_METADATA_COLUMNS,
        extrasaction="ignore",
    )
    writer.writeheader()
    writer.writerow(row)

    key = join_s3_key(
        series,
        STAGING_PREFIX,
        consignment_reference,
        file_id,
        "AYR-ffid-metadata.csv",
    )

    s3.put_object(
        Bucket=DDT_TEMP_CSV_BUCKET,
        Key=key,
        Body=output.getvalue().encode("utf-8"),
        ContentType="text/csv",
    )

    logger.info(
        "Uploaded FFID metadata to s3://%s/%s",
        DDT_TEMP_CSV_BUCKET,
        key,
    )

    return key


def is_file_already_complete(
    run_id: str, consignment_reference: str, file_id: str
) -> bool:
    response = dynamodb.get_item(
        TableName=TRACKING_TABLE_NAME,
        Key={
            "PK": {"S": f"RUN#{run_id}#CONSIGNMENT#{consignment_reference}"},
            "SK": {"S": f"FILE#{file_id}"},
        },
        ConsistentRead=True,
    )

    item = response.get("Item")

    if not item:
        return False

    return item.get("status", {}).get("S") == "COMPLETE"


def mark_file_complete_and_trigger_finaliser_if_consignment_ready(
    run_id: str,
    series: str,
    consignment_reference: str,
    file_id: str,
) -> bool:
    """
    Atomically mark the file complete and increment its consignment counter.
    If all expected files are complete, enqueue the finaliser message.
    """
    file_pk = f"RUN#{run_id}#CONSIGNMENT#{consignment_reference}"
    file_sk = f"FILE#{file_id}"
    consignment_pk = f"RUN#{run_id}"
    consignment_sk = f"CONSIGNMENT#{consignment_reference}"
    now = utc_now_text()

    try:
        transact_write_with_retry(
            [
                {
                    "Update": {
                        "TableName": TRACKING_TABLE_NAME,
                        "Key": {
                            "PK": {"S": file_pk},
                            "SK": {"S": file_sk},
                        },
                        "UpdateExpression": (
                            "SET #status = :complete, completedAt = :now, "
                            "updatedAt = :now"
                        ),
                        "ConditionExpression": "#status <> :complete",
                        "ExpressionAttributeNames": {"#status": "status"},
                        "ExpressionAttributeValues": {
                            ":complete": {"S": "COMPLETE"},
                            ":now": {"S": now},
                        },
                    }
                },
                {
                    "Update": {
                        "TableName": TRACKING_TABLE_NAME,
                        "Key": {
                            "PK": {"S": consignment_pk},
                            "SK": {"S": consignment_sk},
                        },
                        "UpdateExpression": (
                            "SET updatedAt = :now ADD completedFileCount :one"
                        ),
                        "ConditionExpression": "#status = :staging",
                        "ExpressionAttributeNames": {"#status": "status"},
                        "ExpressionAttributeValues": {
                            ":staging": {"S": "STAGING"},
                            ":one": {"N": "1"},
                            ":now": {"S": now},
                        },
                    }
                },
            ]
        )
    except ClientError as error:
        if error.response.get("Error", {}).get(
            "Code"
        ) == "TransactionCanceledException" and is_file_already_complete(
            run_id=run_id,
            consignment_reference=consignment_reference,
            file_id=file_id,
        ):
            logger.info(
                "File already marked COMPLETE. Skipping counter increment. "
                "file_id=%s",
                file_id,
            )
            return trigger_finaliser_if_ready(
                run_id=run_id,
                series=series,
                consignment_reference=consignment_reference,
            )
        raise

    return trigger_finaliser_if_ready(
        run_id=run_id,
        series=series,
        consignment_reference=consignment_reference,
    )


def transact_write_with_retry(
    transact_items: list[dict[str, Any]],
) -> None:
    """Retry a cancelled DynamoDB transaction when items are contended."""
    for attempt in range(1, DYNAMODB_TRANSACTION_MAX_ATTEMPTS + 1):
        try:
            dynamodb.transact_write_items(TransactItems=transact_items)
            return
        except ClientError as error:
            if (
                not has_transaction_conflict(error)
                or attempt == DYNAMODB_TRANSACTION_MAX_ATTEMPTS
            ):
                raise

            maximum_delay = min(
                DYNAMODB_TRANSACTION_MAX_DELAY_SECONDS,
                DYNAMODB_TRANSACTION_BASE_DELAY_SECONDS * (2 ** (attempt - 1)),
            )
            delay = random.uniform(0, maximum_delay)  # nosec B311

            logger.warning(
                "DynamoDB transaction conflict. Retrying attempt=%s/%s "
                "after %.3f seconds",
                attempt,
                DYNAMODB_TRANSACTION_MAX_ATTEMPTS,
                delay,
            )
            time.sleep(delay)


def has_transaction_conflict(error: ClientError) -> bool:
    """Return whether DynamoDB cancelled a transaction due to contention."""
    if (
        error.response.get("Error", {}).get("Code")
        != "TransactionCanceledException"
    ):
        return False

    return any(
        reason.get("Code") == "TransactionConflict"
        for reason in error.response.get("CancellationReasons", [])
    )


def trigger_finaliser_if_ready(
    run_id: str,
    series: str,
    consignment_reference: str,
) -> bool:
    consignment_key = {
        "PK": {"S": f"RUN#{run_id}"},
        "SK": {"S": f"CONSIGNMENT#{consignment_reference}"},
    }
    item = get_consignment_tracking_item(consignment_key)
    expected = get_ddb_number(item, "expectedFileCount")
    completed = get_ddb_number(item, "completedFileCount")
    failed = get_ddb_number(item, "failedFileCount")
    status = get_ddb_string(item, "status")

    logger.info(
        "Consignment progress run_id=%s consignment=%s status=%s "
        "completed=%s expected=%s failed=%s",
        run_id,
        consignment_reference,
        status,
        completed,
        expected,
        failed,
    )

    if completed != expected or failed != 0:
        return False

    if status == "STAGING":
        now = utc_now_text()

        try:
            dynamodb.update_item(
                TableName=TRACKING_TABLE_NAME,
                Key=consignment_key,
                UpdateExpression=(
                    "SET #status = :ready, readyAt = :now, updatedAt = :now"
                ),
                ConditionExpression=(
                    "#status = :staging "
                    "AND completedFileCount = expectedFileCount "
                    "AND failedFileCount = :zero"
                ),
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":ready": {"S": "READY_TO_FINALISE"},
                    ":staging": {"S": "STAGING"},
                    ":zero": {"N": "0"},
                    ":now": {"S": now},
                },
            )
            status = "READY_TO_FINALISE"
        except ClientError as error:
            if (
                error.response.get("Error", {}).get("Code")
                != "ConditionalCheckFailedException"
            ):
                raise

            item = get_consignment_tracking_item(consignment_key)
            status = get_ddb_string(item, "status")

    if status != "READY_TO_FINALISE":
        logger.info(
            "Finaliser does not need triggering. run_id=%s consignment=%s "
            "status=%s",
            run_id,
            consignment_reference,
            status,
        )
        return False

    if get_ddb_string(item, "finaliserMessageSentAt"):
        logger.info(
            "Finaliser message already sent. run_id=%s consignment=%s",
            run_id,
            consignment_reference,
        )
        return False

    ensure_required_staged_csvs_exist(
        series=series,
        consignment_reference=consignment_reference,
    )

    message_id = send_finaliser_message(
        run_id=run_id,
        series=series,
        consignment_reference=consignment_reference,
    )

    record_finaliser_message_sent(
        consignment_key=consignment_key,
        message_id=message_id,
    )

    return True


def ensure_required_staged_csvs_exist(
    series: str,
    consignment_reference: str,
) -> None:
    """Require the shared and consignment CSVs before finalising."""
    required_keys = [
        join_s3_key(
            series,
            STAGING_PREFIX,
            "shared",
            "AYR-body-metadata.csv",
        ),
        join_s3_key(
            series,
            STAGING_PREFIX,
            "shared",
            "AYR-series-metadata.csv",
        ),
        join_s3_key(
            series,
            STAGING_PREFIX,
            consignment_reference,
            "AYR-consignment-metadata.csv",
        ),
    ]

    for key in required_keys:
        s3.head_object(Bucket=DDT_TEMP_CSV_BUCKET, Key=key)


def send_finaliser_message(
    run_id: str, series: str, consignment_reference: str
) -> str:
    message = {
        "runId": run_id,
        "series": series,
        "consignmentReference": consignment_reference,
    }

    response = sqs.send_message(
        QueueUrl=FINALISER_QUEUE_URL,
        MessageBody=json.dumps(message),
    )

    logger.info(
        "Sent finaliser message. run_id=%s consignment=%s sqs_message_id=%s",
        run_id,
        consignment_reference,
        response["MessageId"],
    )

    return response["MessageId"]


def record_finaliser_message_sent(
    consignment_key: dict[str, dict[str, str]], message_id: str
) -> None:
    now = utc_now_text()

    try:
        dynamodb.update_item(
            TableName=TRACKING_TABLE_NAME,
            Key=consignment_key,
            UpdateExpression=(
                "SET finaliserMessageSentAt = :now, "
                "finaliserSqsMessageId = :message_id, updatedAt = :now"
            ),
            ConditionExpression="attribute_not_exists(finaliserMessageSentAt)",
            ExpressionAttributeValues={
                ":now": {"S": now},
                ":message_id": {"S": message_id},
            },
        )
    except ClientError as error:
        if (
            error.response.get("Error", {}).get("Code")
            == "ConditionalCheckFailedException"
        ):
            logger.info("Finaliser message was already recorded as sent.")
            return
        raise


def get_consignment_tracking_item(
    key: dict[str, dict[str, str]],
) -> dict[str, Any]:
    response = dynamodb.get_item(
        TableName=TRACKING_TABLE_NAME,
        Key=key,
        ConsistentRead=True,
    )
    item = response.get("Item")

    if not item:
        raise ValueError(f"Missing consignment tracking item: {key}")

    return item


def get_ddb_string(item: dict[str, Any], key: str) -> str | None:
    value = item.get(key, {}).get("S")

    if isinstance(value, str) and value.strip():
        return value.strip()

    return None


def get_ddb_number(item: dict[str, Any], key: str) -> int:
    value = item.get(key, {}).get("N")

    if value is None:
        raise ValueError(f"Missing DynamoDB number attribute: {key}")

    return int(value)


def join_s3_key(*parts: str) -> str:
    return "/".join(str(part).strip("/") for part in parts if part)


def require_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing required field: {key}")

    return value.strip()


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
