import csv
import hashlib
import json
import logging
import os
import tempfile
import uuid
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack
from datetime import datetime, timezone
from io import StringIO
from math import ceil
from pathlib import Path
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

BODY_COLUMNS = ["BodyId", "Name", "Description"]

SERIES_COLUMNS = ["SeriesId", "BodyId", "Name", "Description"]

CONSIGNMENT_COLUMNS = [
    "ConsignmentId",
    "BodyId",
    "SeriesId",
    "ConsignmentReference",
    "ConsignmentType",
    "IncludeTopLevelFolder",
    "ContactName",
    "ContactEmail",
    "TransferStartDatetime",
    "TransferCompleteDatetime",
    "ExportDatetime",
    "CreatedDatetime",
]

FILE_COLUMNS = [
    "FileId",
    "ConsignmentId",
    "FileType",
    "FileName",
    "FilePath",
    "FileReference",
    "CiteableReference",
    "ParentReference",
    "OriginalFilePath",
    "Checksum",
    "CreatedDatetime",
]

FILE_METADATA_COLUMNS = [
    "MetadataId",
    "FileId",
    "PropertyName",
    "Value",
    "CreatedDatetime",
]

AV_METADATA_COLUMNS = [
    "FileId",
    "Filepath",
    "AV_Software",
]

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

CHECKSUM_CSV_NAME = "AYR-manifest.csv"
CHECKSUM_TEXT_NAME = "AYR-manifest.csv.sha256"
CHECKSUM_COLUMNS = ["file_name", "checksum_sha256"]

BODY_CSV_NAME = "AYR-body-metadata.csv"
SERIES_CSV_NAME = "AYR-series-metadata.csv"
CONSIGNMENT_CSV_NAME = "AYR-consignment-metadata.csv"
SHARED_STAGING_DIRECTORY = "shared"
REQUIRED_SINGLE_ROW_CSV_NAMES = (
    BODY_CSV_NAME,
    SERIES_CSV_NAME,
    CONSIGNMENT_CSV_NAME,
)

CSV_DEFINITIONS = {
    BODY_CSV_NAME: {
        "columns": BODY_COLUMNS,
        "required_column": "Name",
    },
    SERIES_CSV_NAME: {
        "columns": SERIES_COLUMNS,
        "required_column": "Name",
    },
    CONSIGNMENT_CSV_NAME: {
        "columns": CONSIGNMENT_COLUMNS,
        "required_column": "ConsignmentReference",
    },
    "AYR-file.csv": {
        "columns": FILE_COLUMNS,
        "required_column": "FileId",
    },
    "AYR-file-metadata.csv": {
        "columns": FILE_METADATA_COLUMNS,
        "required_column": "MetadataId",
    },
    "AYR-ffid-metadata.csv": {
        "columns": FFID_METADATA_COLUMNS,
        "required_column": "FileId",
    },
    "AYR-av-metadata.csv": {
        "columns": AV_METADATA_COLUMNS,
        "required_column": "FileId",
    },
}

READY_TO_FINALISE = "READY_TO_FINALISE"
FINALISING = "FINALISING"
SENT_TO_DDT = "SENT_TO_DDT"


logger = logging.getLogger()
logger.setLevel(logging.INFO)


S3_READ_WORKERS = 30
S3_READ_BATCH_SIZE = 300

s3 = boto3.client(
    "s3",
    config=Config(
        connect_timeout=5,
        read_timeout=30,
        retries={"max_attempts": 10, "mode": "standard"},
        max_pool_connections=S3_READ_WORKERS,
    ),
)
sns = boto3.client("sns")
dynamodb = boto3.client("dynamodb")

DDT_TEMP_CSV_BUCKET = os.environ["DDT_TEMP_CSV_BUCKET"]
DDT_TEMP_DATA_BUCKET = os.environ["DDT_TEMP_DATA_BUCKET"]
DA_EVENTBUS_TOPIC_ARN = os.environ["DA_EVENTBUS_TOPIC_ARN"]
TRACKING_TABLE_NAME = os.environ["TRACKING_TABLE_NAME"]

OUTPUT_PREFIX = os.getenv("OUTPUT_PREFIX", "ayr-mds-csv")
STAGING_PREFIX = os.getenv("STAGING_PREFIX", "ayr-mds-staging")
FUNCTION_NAME = "dri-to-ayr-data-migration-lambda"


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Finalise consignments from an SQS batch or a direct invocation.

    Expected message/direct event:
    {
      "runId": "LEV-2-...",
      "series": "LEV 2",
      "consignmentReference": "TDR-2026-7333"
    }
    """
    if "Records" not in event:
        process_message(event, context)
        return {"batchItemFailures": []}

    batch_item_failures: list[dict[str, str]] = []

    for record in event["Records"]:
        try:
            message = json.loads(record["body"])
            process_message(message, context)
        except Exception:
            logger.exception("Failed to process finaliser SQS message")
            batch_item_failures.append({"itemIdentifier": record["messageId"]})

    return {"batchItemFailures": batch_item_failures}


def process_message(message: dict[str, Any], context: Any) -> None:
    run_id = require_text(message, "runId")
    series = require_text(message, "series")
    consignment_reference = require_text(message, "consignmentReference")

    should_finalise = start_finalising_or_skip(
        run_id=run_id,
        consignment_reference=consignment_reference,
    )

    if not should_finalise:
        logger.info(
            "Skipping finaliser because DDT message has already been sent. "
            "run_id=%s consignment=%s",
            run_id,
            consignment_reference,
        )
        return

    try:
        ddt_message, final_output_prefix = (
            prepare_final_package_from_staged_csvs(
                run_id=run_id,
                series=series,
                consignment_reference=consignment_reference,
                context=context,
            )
        )
    except Exception:
        handle_pre_publish_failure(run_id, consignment_reference)
        raise

    # Do not reset FINALISING after publication starts. SNS may have accepted
    # the message even if this invocation does not receive a response.
    ddt_sns_message_id = publish_ddt_message(ddt_message)

    mark_consignment_sent_to_ddt(
        run_id=run_id,
        consignment_reference=consignment_reference,
        ddt_sns_message_id=ddt_sns_message_id,
    )

    logger.info(
        "Finished finaliser run_id=%s series=%s consignment=%s "
        "final_output_prefix=s3://%s/%s ddt_sns_message_id=%s",
        run_id,
        series,
        consignment_reference,
        DDT_TEMP_CSV_BUCKET,
        final_output_prefix,
        ddt_sns_message_id,
    )


def handle_pre_publish_failure(
    run_id: str,
    consignment_reference: str,
) -> None:
    """Release the finaliser lock after work fails before SNS publication."""
    logger.warning(
        "Finaliser failed before publishing the DDT message. "
        "Resetting the consignment so SQS can retry it. "
        "run_id=%s consignment=%s",
        run_id,
        consignment_reference,
    )

    try:
        reset_consignment_for_retry(run_id, consignment_reference)
    except Exception:
        logger.exception(
            "Could not reset consignment to READY_TO_FINALISE. "
            "run_id=%s consignment=%s",
            run_id,
            consignment_reference,
        )


def prepare_final_package_from_staged_csvs(
    run_id: str,
    series: str,
    consignment_reference: str,
    context: Any,
) -> tuple[dict[str, Any], str]:
    """Build the final metadata package from staged CSV files.

    Combines the shared Body and Series CSVs with the consignment-specific
    staged CSVs, validates the required metadata, creates and uploads the
    merged CSV/checksum package, and returns the DDT message and final output
    prefix.
    """
    shared_staging_prefix = join_s3_key(
        series,
        STAGING_PREFIX,
        SHARED_STAGING_DIRECTORY,
    )
    consignment_staging_prefix = join_s3_key(
        series,
        STAGING_PREFIX,
        consignment_reference,
    )
    final_output_prefix = join_s3_key(
        series, OUTPUT_PREFIX, consignment_reference
    )

    logger.info(
        "Finalising run_id=%s series=%s consignment=%s "
        "shared_staging_prefix=%s consignment_staging_prefix=%s "
        "final_output_prefix=%s",
        run_id,
        series,
        consignment_reference,
        shared_staging_prefix,
        consignment_staging_prefix,
        final_output_prefix,
    )

    consignment_csv_keys = list_staged_csv_keys(consignment_staging_prefix)

    if not consignment_csv_keys:
        raise ValueError(
            "No staged CSV files found under "
            f"s3://{DDT_TEMP_CSV_BUCKET}/{consignment_staging_prefix}"
        )

    ensure_single_consignment_csv(
        keys=consignment_csv_keys,
        staging_prefix=consignment_staging_prefix,
    )

    staged_csv_keys = [
        join_s3_key(shared_staging_prefix, BODY_CSV_NAME),
        join_s3_key(shared_staging_prefix, SERIES_CSV_NAME),
        *consignment_csv_keys,
    ]

    create_and_upload_final_metadata(
        staged_csv_keys=staged_csv_keys,
        final_output_prefix=final_output_prefix,
    )

    ddt_message = build_ddt_prepared_message(
        series=series,
        consignment_reference=consignment_reference,
        context=context,
    )

    return ddt_message, final_output_prefix


def ensure_single_consignment_csv(
    keys: list[str],
    staging_prefix: str,
) -> None:
    """Require exactly one staged Consignment CSV for this consignment."""
    consignment_csv_count = sum(
        Path(key).name == CONSIGNMENT_CSV_NAME for key in keys
    )

    if consignment_csv_count != 1:
        raise ValueError(
            f"Expected exactly one {CONSIGNMENT_CSV_NAME} under "
            f"s3://{DDT_TEMP_CSV_BUCKET}/{staging_prefix}; "
            f"found {consignment_csv_count}"
        )


def create_and_upload_final_metadata(
    staged_csv_keys: list[str],
    final_output_prefix: str,
) -> None:
    """Create the final CSV package and upload it to its output prefix."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)

        merge_counts = merge_staged_csvs(
            staged_csv_keys=staged_csv_keys,
            output_dir=output_dir,
        )
        logger.info("Merged final CSV row counts: %s", merge_counts)
        ensure_required_single_rows(merge_counts)

        create_checksum_files(output_dir)

        upload_metadata_files(
            local_dir=output_dir,
            prefix=final_output_prefix,
        )


def ensure_required_single_rows(counts: dict[str, int]) -> None:
    """Require one Body, Series, and Consignment row in the final package."""
    invalid_counts = {
        file_name: counts.get(file_name, 0)
        for file_name in REQUIRED_SINGLE_ROW_CSV_NAMES
        if counts.get(file_name, 0) != 1
    }

    if invalid_counts:
        details = ", ".join(
            f"{file_name}={count}"
            for file_name, count in invalid_counts.items()
        )
        raise ValueError(
            "Expected exactly one row in each shared/consignment CSV; "
            f"found {details}"
        )


def list_staged_csv_keys(staging_prefix: str) -> list[str]:
    prefix = ensure_trailing_slash(staging_prefix)
    keys: list[str] = []
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=DDT_TEMP_CSV_BUCKET, Prefix=prefix):
        for item in page.get("Contents", []):
            key = item["Key"]
            if should_merge_staged_csv(key):
                keys.append(key)

    logger.info(
        "Found %s staged CSV file(s) under s3://%s/%s",
        len(keys),
        DDT_TEMP_CSV_BUCKET,
        prefix,
    )

    return keys


def should_merge_staged_csv(key: str) -> bool:
    """Return whether a staged S3 object belongs in the final package."""
    file_name = Path(key).name

    if file_name in {CHECKSUM_CSV_NAME, CHECKSUM_TEXT_NAME}:
        logger.debug(
            "Skipping staged manifest/checksum file: s3://%s/%s",
            DDT_TEMP_CSV_BUCKET,
            key,
        )
        return False

    if file_name not in CSV_DEFINITIONS:
        logger.warning(
            "Ignoring unexpected staged file: s3://%s/%s",
            DDT_TEMP_CSV_BUCKET,
            key,
        )
        return False

    return True


def merge_staged_csvs(
    staged_csv_keys: list[str],
    output_dir: Path,
) -> dict[str, int]:
    """
    Merge worker-staged CSVs into the final consignment package.

    S3 objects are fetched concurrently in bounded batches, but rows are
    merged in sorted key order so output remains deterministic. Rows are
    written directly to disk to keep memory bounded.
    """
    keys = sorted(staged_csv_keys)
    total = len(keys)
    counts: dict[str, int] = {file_name: 0 for file_name in CSV_DEFINITIONS}
    progress_interval = max(1, ceil(total / 5))
    next_progress = progress_interval

    logger.info(
        "Reading and merging %s staged CSV object(s) using %s worker(s) "
        "and batches of %s",
        total,
        S3_READ_WORKERS,
        S3_READ_BATCH_SIZE,
    )

    with ExitStack() as stack:
        writers_by_file = open_output_csv_writers(output_dir, stack)

        for processed, (key, rows) in enumerate(
            get_staged_csv_rows(keys),
            start=1,
        ):
            file_name = Path(key).name
            definition = CSV_DEFINITIONS[file_name]
            required_column = definition["required_column"]

            for row in rows:
                if not row.get(required_column):
                    raise ValueError(
                        f"Missing {required_column} value in {file_name} row from "
                        f"s3://{DDT_TEMP_CSV_BUCKET}/{key}"
                    )

                writers_by_file[file_name].writerow(row)
                counts[file_name] += 1

            if processed >= next_progress or processed == total:
                log_merge_progress(processed, total)
                next_progress += progress_interval

    return counts


def open_output_csv_writers(
    output_dir: Path,
    stack: ExitStack,
) -> dict[str, Any]:
    """Open every final CSV and write its header."""
    writers: dict[str, Any] = {}

    for file_name, definition in CSV_DEFINITIONS.items():
        handle = stack.enter_context(
            (output_dir / file_name).open(
                "w",
                newline="",
                encoding="utf-8",
            )
        )
        writer = csv.DictWriter(
            handle,
            fieldnames=definition["columns"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writers[file_name] = writer

    return writers


def get_staged_csv_rows(keys: list[str]):
    """Fetch staged CSV objects concurrently and yield them in key order."""
    with ThreadPoolExecutor(max_workers=S3_READ_WORKERS) as executor:
        for start in range(0, len(keys), S3_READ_BATCH_SIZE):
            batch = keys[start : start + S3_READ_BATCH_SIZE]
            rows_iterator = executor.map(read_csv_from_s3_as_list, batch)

            yield from zip(batch, rows_iterator, strict=True)


def log_merge_progress(processed: int, total: int) -> None:
    logger.info(
        "Read and merged %s/%s staged CSV object(s)",
        processed,
        total,
    )


def read_csv_from_s3_as_list(key: str) -> list[dict[str, str]]:
    logger.debug("Reading staged CSV s3://%s/%s", DDT_TEMP_CSV_BUCKET, key)

    response = s3.get_object(Bucket=DDT_TEMP_CSV_BUCKET, Key=key)
    response_body = response["Body"]

    try:
        body = response_body.read().decode("utf-8-sig")
    finally:
        response_body.close()

    if not body.strip():
        return []

    reader = csv.DictReader(StringIO(body))
    return [dict(row) for row in reader]


def create_checksum_files(output_dir: Path) -> None:
    checksum_csv_path = output_dir / CHECKSUM_CSV_NAME
    checksum_text_path = output_dir / CHECKSUM_TEXT_NAME

    csv_files = sorted(
        path
        for path in output_dir.glob("*.csv")
        if path.name != CHECKSUM_CSV_NAME
    )

    with checksum_csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CHECKSUM_COLUMNS)
        writer.writeheader()

        for csv_file in csv_files:
            writer.writerow(
                {
                    "file_name": csv_file.name,
                    "checksum_sha256": sha256_file(csv_file),
                }
            )

    checksum_text_path.write_text(
        f"{sha256_file(checksum_csv_path)}  {CHECKSUM_CSV_NAME}\n",
        encoding="utf-8",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def upload_metadata_files(local_dir: Path, prefix: str) -> None:
    for local_file in sorted(local_dir.iterdir()):
        if not local_file.is_file():
            continue

        destination_key = join_s3_key(prefix, local_file.name)
        s3.upload_file(
            str(local_file),
            DDT_TEMP_CSV_BUCKET,
            destination_key,
        )

        logger.info(
            "Uploaded final metadata file %s to s3://%s/%s",
            local_file.name,
            DDT_TEMP_CSV_BUCKET,
            destination_key,
        )


def build_ddt_prepared_message(
    series: str,
    consignment_reference: str,
    context: Any,
) -> dict[str, Any]:
    execution_id = getattr(context, "aws_request_id", None) or str(uuid.uuid4())

    return {
        "properties": {
            "messageType": "uk.gov.nationalarchives.da.messages.ayrmetadata.prepared",
            "timestamp": utc_now_text(),
            "function": FUNCTION_NAME,
            "producer": "AYR",
            "messageId": str(uuid.uuid4()),
            "parentMessageId": "",
            "executionId": execution_id,
        },
        "parameters": {
            "reference": consignment_reference,
            "consignmentType": "STANDARD",
            "s3ObjectsBucket": DDT_TEMP_DATA_BUCKET,
            "s3ObjectsLocationKey": ensure_trailing_slash(series),
            "s3MetadataBucket": DDT_TEMP_CSV_BUCKET,
            "s3MetadataFileKey": ensure_trailing_slash(
                join_s3_key(series, OUTPUT_PREFIX)
            ),
        },
    }


def publish_ddt_message(message: dict[str, Any]) -> str:
    """Publish the DDT prepared message and return its SNS message ID."""
    response = sns.publish(
        TopicArn=DA_EVENTBUS_TOPIC_ARN,
        Message=json.dumps(message),
        MessageAttributes={
            "messageType": {
                "DataType": "String",
                "StringValue": message["properties"]["messageType"],
            }
        },
    )

    message_id = response["MessageId"]
    logger.info(
        "Published DDT prepared message to SNS. SNS MessageId=%s", message_id
    )

    return message_id


def start_finalising_or_skip(run_id: str, consignment_reference: str) -> bool:
    """
    Take the finaliser lock for a consignment.

    Return True when this invocation acquires the lock, or False when the DDT
    message has already been sent. Raise for any other status so that SQS can
    retry or send the message to its DLQ.
    """
    now = utc_now_text()

    try:
        dynamodb.update_item(
            TableName=TRACKING_TABLE_NAME,
            Key=consignment_key(run_id, consignment_reference),
            UpdateExpression=(
                "SET #status = :finalising, "
                "finalisingStartedAt = :now, "
                "updatedAt = :now"
            ),
            ConditionExpression=(
                "#status = :ready "
                "AND completedFileCount = expectedFileCount "
                "AND failedFileCount = :zero"
            ),
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":ready": {"S": READY_TO_FINALISE},
                ":finalising": {"S": FINALISING},
                ":zero": {"N": "0"},
                ":now": {"S": now},
            },
        )
        return True

    except ClientError as error:
        if not is_conditional_check_failure(error):
            raise

    status = get_consignment_status(run_id, consignment_reference)

    if status == SENT_TO_DDT:
        return False

    if status == FINALISING:
        raise RuntimeError(
            f"Consignment is already FINALISING. Not publishing duplicate DDT message. "
            f"runId={run_id} consignmentReference={consignment_reference}. "
            "Check whether the previous finaliser published the DDT message before "
            "resetting the consignment status to READY_TO_FINALISE."
        )

    raise RuntimeError(
        f"Consignment is not ready to finalise. "
        f"runId={run_id} consignmentReference={consignment_reference} status={status}"
    )


def reset_consignment_for_retry(
    run_id: str,
    consignment_reference: str,
) -> None:
    """Release the finaliser lock after a confirmed pre-publish failure."""
    now = utc_now_text()

    try:
        dynamodb.update_item(
            TableName=TRACKING_TABLE_NAME,
            Key=consignment_key(run_id, consignment_reference),
            UpdateExpression=(
                "SET #status = :ready, finalisingFailedAt = :now, "
                "updatedAt = :now REMOVE finalisingStartedAt"
            ),
            ConditionExpression="#status = :finalising",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":ready": {"S": READY_TO_FINALISE},
                ":finalising": {"S": FINALISING},
                ":now": {"S": now},
            },
        )
    except ClientError as error:
        if not is_conditional_check_failure(error):
            raise

        status = get_consignment_status(run_id, consignment_reference)

        if status in {READY_TO_FINALISE, SENT_TO_DDT}:
            logger.info(
                "Consignment no longer needs resetting. run_id=%s "
                "consignment=%s status=%s",
                run_id,
                consignment_reference,
                status,
            )
            return

        raise RuntimeError(
            "Could not release finaliser lock. "
            f"runId={run_id} consignmentReference={consignment_reference} "
            f"status={status}"
        )

    logger.info(
        "Reset consignment to READY_TO_FINALISE for retry. "
        "run_id=%s consignment=%s",
        run_id,
        consignment_reference,
    )


def get_consignment_status(run_id: str, consignment_reference: str) -> str:
    response = dynamodb.get_item(
        TableName=TRACKING_TABLE_NAME,
        Key=consignment_key(run_id, consignment_reference),
        ConsistentRead=True,
    )

    item = response.get("Item")

    if not item:
        raise ValueError(
            f"Missing consignment tracking item for runId={run_id} "
            f"consignmentReference={consignment_reference}"
        )

    return item.get("status", {}).get("S", "UNKNOWN")


def mark_consignment_sent_to_ddt(
    run_id: str,
    consignment_reference: str,
    ddt_sns_message_id: str,
) -> None:
    now = utc_now_text()

    try:
        dynamodb.update_item(
            TableName=TRACKING_TABLE_NAME,
            Key=consignment_key(run_id, consignment_reference),
            UpdateExpression=(
                "SET #status = :sent, "
                "ddtSnsMessageId = :message_id, "
                "sentToDdtAt = :now, "
                "updatedAt = :now"
            ),
            ConditionExpression="#status = :finalising",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":finalising": {"S": FINALISING},
                ":sent": {"S": SENT_TO_DDT},
                ":message_id": {"S": ddt_sns_message_id},
                ":now": {"S": now},
            },
        )
    except ClientError as error:
        if is_conditional_check_failure(error):
            status = get_consignment_status(run_id, consignment_reference)

            if status == SENT_TO_DDT:
                logger.info(
                    "Consignment already marked SENT_TO_DDT. run_id=%s consignment=%s",
                    run_id,
                    consignment_reference,
                )
                return

        raise


def is_conditional_check_failure(error: ClientError) -> bool:
    return (
        error.response.get("Error", {}).get("Code")
        == "ConditionalCheckFailedException"
    )


def consignment_key(
    run_id: str, consignment_reference: str
) -> dict[str, dict[str, str]]:
    return {
        "PK": {"S": f"RUN#{run_id}"},
        "SK": {"S": f"CONSIGNMENT#{consignment_reference}"},
    }


def ensure_trailing_slash(value: str) -> str:
    value = value.strip()
    return value if value.endswith("/") else f"{value}/"


def join_s3_key(*parts: str) -> str:
    return "/".join(part.strip("/") for part in parts if part)


def require_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing required field: {key}")

    return value.strip().rstrip("/")


def utc_now_text() -> str:
    """Return UTC timestamp in DDT/Talend expected format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
