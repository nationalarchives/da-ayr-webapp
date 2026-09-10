import csv
import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from worker.dri_to_ayr_csv import convert_record_to_csv, utc_now_text

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
sqs = boto3.client("sqs")
dynamodb = boto3.client("dynamodb")
lambda_client = boto3.client(
    "lambda",
    config=Config(
        connect_timeout=5,
        read_timeout=900,
        retries={"max_attempts": 1},
    ),
)

DRI_JSON_BUCKET = os.environ["DRI_JSON_BUCKET"]
DRI_DATA_BUCKET = os.environ["DRI_DATA_BUCKET"]
DDT_TEMP_CSV_BUCKET = os.environ["DDT_TEMP_CSV_BUCKET"]
DDT_TEMP_DATA_BUCKET = os.environ["DDT_TEMP_DATA_BUCKET"]
DROID_LAMBDA_NAME = os.environ["DROID_LAMBDA_NAME"]
TRACKING_TABLE_NAME = os.environ["TRACKING_TABLE_NAME"]
FINALISER_QUEUE_URL = os.environ["FINALISER_QUEUE_URL"]

JSON_PREFIX = os.getenv("JSON_PREFIX", "live")
DATA_PREFIX = os.getenv("DATA_PREFIX", "v1")
STAGING_PREFIX = os.getenv("STAGING_PREFIX", "ayr-mds-staging")

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


CONSIGNMENT_STATUSES_SKIP_WORKER = {
    "READY_TO_FINALISE",
    "FINALISING",
    "SENT_TO_DDT",
}


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    SQS-triggered per-record worker

    Expected SQS body:
    {
      "runId": "LEV-2-...",
      "series": "LEV 2",
      "reference": "LEV 2/2BD/Z",
      "consignmentReference": "TDR-2026-7333",
      "fileId": "6be8b424-..."
    }
    """
    # Allow direct invocation for manually retrying a single failed file
    if "Records" not in event:
        process_message(event)
        return {"batchItemFailures": []}

    batch_item_failures = []

    for record in event["Records"]:
        try:
            message = json.loads(record["body"])
            process_message(message)
        except Exception:
            logger.exception("Failed to process worker SQS message")
            batch_item_failures.append({"itemIdentifier": record["messageId"]})

    return {"batchItemFailures": batch_item_failures}


def process_message(message: dict[str, Any]) -> None:
    run_id = require_text(message, "runId")
    series = require_text(message, "series")
    reference = require_text(message, "reference")
    consignment_reference = require_text(message, "consignmentReference")
    expected_file_id = require_text(message, "fileId")

    consignment_status = get_consignment_status(
        run_id=run_id,
        consignment_reference=consignment_reference,
    )

    if consignment_status in CONSIGNMENT_STATUSES_SKIP_WORKER:
        logger.info(
            "Skipping worker because consignment is already past worker stage. run_id=%s consignment=%s status=%s file_id=%s",
            run_id,
            consignment_reference,
            consignment_status,
            expected_file_id,
        )
        return

    if is_file_already_complete(
        run_id=run_id,
        consignment_reference=consignment_reference,
        file_id=expected_file_id,
    ):
        logger.info(
            "Skipping worker because file is already COMPLETE. run_id=%s consignment=%s file_id=%s",
            run_id,
            consignment_reference,
            expected_file_id,
        )
        return

    process_file(
        run_id=run_id,
        series=series,
        reference=reference,
        consignment_reference=consignment_reference,
        expected_file_id=expected_file_id,
    )


def process_file(
    run_id: str,
    series: str,
    reference: str,
    consignment_reference: str,
    expected_file_id: str,
) -> None:
    json_key = build_json_key(reference)
    logger.info(
        "Processing run_id=%s series=%s reference=%s consignment_reference=%s file_id=%s",
        run_id,
        series,
        reference,
        consignment_reference,
        expected_file_id,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        local_json_path = temp_path / "dri-record.json"
        csv_output_dir = temp_path / "csv-output"

        s3.download_file(DRI_JSON_BUCKET, json_key, str(local_json_path))
        record = load_record(local_json_path)
        digital_file = get_single_digital_file(record, expected_file_id)

        record_id = require_text(record, "recordId")
        file_id = require_text(digital_file, "fileId")
        extension = get_file_extension(digital_file)

        ffid_row = copy_data_file_and_run_droid(
            record_id=record_id,
            file_id=file_id,
            extension=extension,
            series=series,
            consignment_reference=consignment_reference,
        )

        convert_record_to_csv(
            record=record,
            digital_file=digital_file,
            output_dir=str(csv_output_dir),
            consignment_reference=consignment_reference,
        )

        write_ffid_metadata_csv(
            output_path=csv_output_dir / "AYR-ffid-metadata.csv",
            rows=[ffid_row],
        )

        staging_prefix = build_staging_prefix(
            series=series,
            consignment_reference=consignment_reference,
            file_id=expected_file_id,
        )

        upload_metadata_files(
            local_dir=csv_output_dir,
            bucket=DDT_TEMP_CSV_BUCKET,
            prefix=staging_prefix,
        )

    finaliser_triggered = mark_file_complete_and_maybe_trigger_finaliser(
        run_id=run_id,
        series=series,
        consignment_reference=consignment_reference,
        file_id=expected_file_id,
    )

    logger.info(
        "Finished worker run_id=%s consignment=%s file_id=%s staging_prefix=s3://%s/%s finaliser_triggered=%s",
        run_id,
        consignment_reference,
        expected_file_id,
        DDT_TEMP_CSV_BUCKET,
        staging_prefix,
        finaliser_triggered,
    )


def copy_data_file_and_run_droid(
    record_id: str,
    file_id: str,
    extension: str,
    series: str,
    consignment_reference: str,
) -> dict[str, str]:
    source_key = join_s3_key(DATA_PREFIX, record_id, file_id)
    destination_key = join_s3_key(series, consignment_reference, file_id)

    s3.copy_object(
        Bucket=DDT_TEMP_DATA_BUCKET,
        CopySource={"Bucket": DRI_DATA_BUCKET, "Key": source_key},
        Key=destination_key,
    )

    copied_uri = f"s3://{DDT_TEMP_DATA_BUCKET}/{destination_key}"

    logger.info(
        "Copied s3://%s/%s to %s",
        DRI_DATA_BUCKET,
        source_key,
        copied_uri,
    )

    ffid_metadata_row = invoke_droid_lambda(
        bucket=DDT_TEMP_DATA_BUCKET,
        key=destination_key,
        file_id=file_id,
        extension=extension,
    )

    return ffid_metadata_row


def invoke_droid_lambda(
    bucket: str, key: str, file_id: str, extension: str
) -> dict[str, str]:
    payload = {
        "bucket": bucket,
        "key": key,
        "fileId": file_id,
        "extension": extension,
    }

    logger.info(
        "Invoking DROID lambda %s for s3://%s/%s",
        DROID_LAMBDA_NAME,
        bucket,
        key,
    )

    response = lambda_client.invoke(
        FunctionName=DROID_LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )

    response_payload = json.loads(response["Payload"].read().decode("utf-8"))

    if response.get("FunctionError"):
        raise RuntimeError(
            f"DROID Lambda failed for s3://{bucket}/{key}: {response_payload}"
        )

    ffid_metadata_row = response_payload.get("ffid_metadata_row")

    if not ffid_metadata_row:
        raise RuntimeError(
            f"DROID Lambda did not return ffid_metadata_row for s3://{bucket}/{key}. "
            f"Response: {response_payload}"
        )

    return ffid_metadata_row


def get_consignment_status(
    run_id: str, consignment_reference: str
) -> str | None:
    """Return current consignment status for this run, if the tracking row exists."""
    response = dynamodb.get_item(
        TableName=TRACKING_TABLE_NAME,
        Key={
            "PK": {"S": f"RUN#{run_id}"},
            "SK": {"S": f"CONSIGNMENT#{consignment_reference}"},
        },
        ConsistentRead=True,
    )

    item = response.get("Item")
    if not item:
        return None

    status = item.get("status", {}).get("S")
    if isinstance(status, str) and status.strip():
        return status.strip()

    return None


def is_file_already_complete(
    run_id: str, consignment_reference: str, file_id: str
) -> bool:
    """Return True if this file is already complete for this run/consignment."""
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


def mark_file_complete_and_maybe_trigger_finaliser(
    run_id: str,
    series: str,
    consignment_reference: str,
    file_id: str,
) -> bool:
    """
    Idempotently mark the file as complete. If this was the final expected file
    for the consignment, send one message to the finaliser queue.
    """
    file_pk = f"RUN#{run_id}#CONSIGNMENT#{consignment_reference}"
    file_sk = f"FILE#{file_id}"
    now = utc_now_text()

    try:
        dynamodb.update_item(
            TableName=TRACKING_TABLE_NAME,
            Key={"PK": {"S": file_pk}, "SK": {"S": file_sk}},
            UpdateExpression="SET #status = :complete, completedAt = :now, updatedAt = :now",
            ConditionExpression="attribute_not_exists(#status) OR #status <> :complete",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":complete": {"S": "COMPLETE"},
                ":now": {"S": now},
            },
        )
    except ClientError as error:
        if (
            error.response.get("Error", {}).get("Code")
            == "ConditionalCheckFailedException"
        ):
            logger.info(
                "File already marked COMPLETE. Skipping counter increment. file_id=%s",
                file_id,
            )
            return False
        raise

    consignment_key = {
        "PK": {"S": f"RUN#{run_id}"},
        "SK": {"S": f"CONSIGNMENT#{consignment_reference}"},
    }

    response = dynamodb.update_item(
        TableName=TRACKING_TABLE_NAME,
        Key=consignment_key,
        UpdateExpression="SET updatedAt = :now ADD completedFileCount :one",
        ExpressionAttributeValues={
            ":one": {"N": "1"},
            ":now": {"S": now},
        },
        ReturnValues="ALL_NEW",
    )

    attributes = response["Attributes"]
    expected = int(attributes["expectedFileCount"]["N"])
    completed = int(attributes["completedFileCount"]["N"])
    failed = int(attributes.get("failedFileCount", {"N": "0"})["N"])

    logger.info(
        "Consignment progress run_id=%s consignment=%s completed=%s expected=%s failed=%s",
        run_id,
        consignment_reference,
        completed,
        expected,
        failed,
    )

    if completed != expected or failed != 0:
        return False

    try:
        dynamodb.update_item(
            TableName=TRACKING_TABLE_NAME,
            Key=consignment_key,
            UpdateExpression="SET #status = :ready, readyAt = :now, updatedAt = :now",
            ConditionExpression="#status = :staging AND completedFileCount = expectedFileCount AND failedFileCount = :zero",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":ready": {"S": "READY_TO_FINALISE"},
                ":staging": {"S": "STAGING"},
                ":zero": {"N": "0"},
                ":now": {"S": now},
            },
        )
    except ClientError as error:
        if (
            error.response.get("Error", {}).get("Code")
            == "ConditionalCheckFailedException"
        ):
            logger.info(
                "Finaliser already triggered or consignment is no longer ready."
            )
            return False
        raise

    send_finaliser_message(
        run_id=run_id,
        series=series,
        consignment_reference=consignment_reference,
    )

    return True


def send_finaliser_message(
    run_id: str, series: str, consignment_reference: str
) -> None:
    message = {
        "runId": run_id,
        "series": series,
        "consignmentReference": consignment_reference,
    }

    sqs.send_message(
        QueueUrl=FINALISER_QUEUE_URL,
        MessageBody=json.dumps(message),
    )

    logger.info(
        "Sent finaliser message for run_id=%s consignment=%s",
        run_id,
        consignment_reference,
    )


def write_ffid_metadata_csv(
    output_path: Path, rows: list[dict[str, str]]
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=FFID_METADATA_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def upload_metadata_files(local_dir: Path, bucket: str, prefix: str) -> None:
    for local_file in sorted(local_dir.iterdir()):
        if not local_file.is_file():
            continue

        destination_key = join_s3_key(prefix, local_file.name)
        s3.upload_file(str(local_file), bucket, destination_key)
        uploaded_uri = f"s3://{bucket}/{destination_key}"
        logger.info(
            "Uploaded staged file %s to %s", local_file.name, uploaded_uri
        )


def get_single_digital_file(
    record: dict[str, Any], expected_file_id: str
) -> dict[str, Any]:
    """Return the only digital file for the record.

    This migration round only supports records with exactly one digitalFiles[] item.
    Metadata-only records and records with multiple digital files are rejected.
    """
    digital_files = record.get("digitalFiles")

    if not isinstance(digital_files, list):
        raise ValueError(
            f"digitalFiles is not a list for reference={record.get('reference')}"
        )

    if len(digital_files) != 1:
        raise ValueError(
            f"Expected exactly one digitalFiles[] item for reference={record.get('reference')}, "
            f"got {len(digital_files)}"
        )

    digital_file = digital_files[0]

    if not isinstance(digital_file, dict):
        raise ValueError(
            f"digitalFiles[] must contain JSON objects only for reference={record.get('reference')}"
        )

    actual_file_id = str(digital_file.get("fileId", "")).strip()

    if actual_file_id != expected_file_id:
        raise ValueError(
            f"Expected digitalFiles[0].fileId={expected_file_id} "
            f"for reference={record.get('reference')}, got {actual_file_id or 'missing'}"
        )

    return digital_file


def get_file_extension(digital_file: dict[str, Any]) -> str:
    file_name = require_text(digital_file, "fileName")
    name = file_name.replace("\\", "/").split("/")[-1]

    if "." not in name:
        return ""

    return name.rsplit(".", 1)[1].lower()


def build_json_key(reference: str) -> str:
    reference_file_name = reference.replace("/", "-")

    if not reference_file_name.endswith(".json"):
        reference_file_name = f"{reference_file_name}.json"

    return join_s3_key(JSON_PREFIX, reference_file_name)


def build_staging_prefix(
    series: str, consignment_reference: str, file_id: str
) -> str:
    return join_s3_key(series, STAGING_PREFIX, consignment_reference, file_id)


def load_record(json_path: Path) -> dict[str, Any]:
    data = json.loads(json_path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError(
            "Expected one JSON object representing one DRI record."
        )

    return data


def join_s3_key(*parts: str) -> str:
    return "/".join(str(part).strip("/") for part in parts if part)


def require_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing required field: {key}")

    return value.strip().rstrip("/")
