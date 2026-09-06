import csv
import hashlib
import json
import logging
import os
import tempfile
import uuid
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any

import boto3
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

CSV_DEFINITIONS = {
    "AYR-body-metadata.csv": {
        "columns": BODY_COLUMNS,
        "dedupe_columns": ["Name"],
    },
    "AYR-series-metadata.csv": {
        "columns": SERIES_COLUMNS,
        "dedupe_columns": ["Name"],
    },
    "AYR-consignment-metadata.csv": {
        "columns": CONSIGNMENT_COLUMNS,
        "dedupe_columns": ["ConsignmentReference"],
    },
    "AYR-file.csv": {
        "columns": FILE_COLUMNS,
        "dedupe_columns": ["FileId"],
    },
    "AYR-file-metadata.csv": {
        "columns": FILE_METADATA_COLUMNS,
        "dedupe_columns": ["MetadataId"],
    },
    "AYR-ffid-metadata.csv": {
        "columns": FFID_METADATA_COLUMNS,
        "dedupe_columns": ["FileId"],
    },
    "AYR-av-metadata.csv": {
        "columns": AV_METADATA_COLUMNS,
        "dedupe_columns": ["FileId", "Filepath", "AV_Software"],
    },
}

READY_TO_FINALISE = "READY_TO_FINALISE"
FINALISING = "FINALISING"
SENT_TO_DDT = "SENT_TO_DDT"


logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
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
    SQS-triggered consignment finaliser.

    Expected SQS body:
    {
      "runId": "LEV-2-...",
      "series": "LEV 2",
      "consignmentReference": "TDR-2026-7333"
    }
    """
    # Allow direct invocation for manually retrying a single consignment.
    if "Records" not in event:
        process_message(event, context)
        return {"batchItemFailures": []}

    batch_item_failures = []

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

    staging_prefix = join_s3_key(series, STAGING_PREFIX, consignment_reference)
    final_output_prefix = join_s3_key(
        series, OUTPUT_PREFIX, consignment_reference
    )

    logger.info(
        "Finalising run_id=%s series=%s consignment=%s staging_prefix=%s final_output_prefix=%s",
        run_id,
        series,
        consignment_reference,
        staging_prefix,
        final_output_prefix,
    )

    staged_csv_keys = list_staged_csv_keys(staging_prefix)

    if not staged_csv_keys:
        raise ValueError(
            f"No staged CSV files found under s3://{DDT_TEMP_CSV_BUCKET}/{staging_prefix}"
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "final-csv-output"
        output_dir.mkdir(parents=True, exist_ok=True)

        merge_counts = merge_staged_csvs(staged_csv_keys, output_dir)
        logger.info("Merged final CSV row counts: %s", merge_counts)

        create_checksum_files(output_dir)

        upload_metadata_files(
            local_dir=output_dir,
            bucket=DDT_TEMP_CSV_BUCKET,
            prefix=final_output_prefix,
        )

    ddt_message = build_ddt_prepared_message(
        reference=consignment_reference,
        s3_objects_bucket=DDT_TEMP_DATA_BUCKET,
        s3_objects_location_key=ensure_trailing_slash(series),
        s3_metadata_bucket=DDT_TEMP_CSV_BUCKET,
        s3_metadata_file_key=ensure_trailing_slash(
            join_s3_key(series, OUTPUT_PREFIX)
        ),
        context=context,
    )

    ddt_sns_message_id = publish_ddt_message(ddt_message)

    mark_consignment_sent_to_ddt(
        run_id=run_id,
        consignment_reference=consignment_reference,
        ddt_sns_message_id=ddt_sns_message_id,
    )

    logger.info(
        "Finished finaliser run_id=%s series=%s consignment=%s final_output_prefix=s3://%s/%s ddt_sns_message_id=%s",
        run_id,
        series,
        consignment_reference,
        DDT_TEMP_CSV_BUCKET,
        final_output_prefix,
        ddt_sns_message_id,
    )


def list_staged_csv_keys(staging_prefix: str) -> list[str]:
    prefix = ensure_trailing_slash(staging_prefix)
    keys: list[str] = []
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=DDT_TEMP_CSV_BUCKET, Prefix=prefix):
        for item in page.get("Contents", []):
            key = item["Key"]
            file_name = Path(key).name

            if not key.endswith(".csv"):
                continue

            if file_name in {CHECKSUM_CSV_NAME, CHECKSUM_TEXT_NAME}:
                continue

            if file_name not in CSV_DEFINITIONS:
                logger.warning(
                    "Ignoring unexpected staged CSV file: s3://%s/%s",
                    DDT_TEMP_CSV_BUCKET,
                    key,
                )
                continue

            keys.append(key)

    return sorted(keys)


def merge_staged_csvs(
    staged_csv_keys: list[str], output_dir: Path
) -> dict[str, int]:
    rows_by_file: dict[str, list[dict[str, str]]] = {
        file_name: [] for file_name in CSV_DEFINITIONS
    }
    seen_by_file: dict[str, set[tuple[str, ...]]] = {
        file_name: set() for file_name in CSV_DEFINITIONS
    }

    for key in staged_csv_keys:
        file_name = Path(key).name
        definition = CSV_DEFINITIONS[file_name]
        dedupe_columns = definition["dedupe_columns"]

        for row in read_csv_from_s3(key):
            dedupe_key = tuple(row.get(column, "") for column in dedupe_columns)

            if dedupe_key in seen_by_file[file_name]:
                continue

            seen_by_file[file_name].add(dedupe_key)
            rows_by_file[file_name].append(row)

    counts: dict[str, int] = {}

    for file_name, definition in CSV_DEFINITIONS.items():
        rows = rows_by_file[file_name]
        write_csv(output_dir / file_name, definition["columns"], rows)
        counts[file_name] = len(rows)

    return counts


def read_csv_from_s3(key: str) -> list[dict[str, str]]:
    logger.info("Reading staged CSV s3://%s/%s", DDT_TEMP_CSV_BUCKET, key)

    response = s3.get_object(Bucket=DDT_TEMP_CSV_BUCKET, Key=key)
    body = response["Body"].read().decode("utf-8-sig")

    if not body.strip():
        return []

    reader = csv.DictReader(StringIO(body))
    return [dict(row) for row in reader]


def write_csv(
    path: Path, columns: list[str], rows: list[dict[str, Any]]
) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=columns, extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(rows)

    logger.info("Wrote %s row(s) to %s", len(rows), path)


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


def upload_metadata_files(local_dir: Path, bucket: str, prefix: str) -> None:
    for local_file in sorted(local_dir.iterdir()):
        if not local_file.is_file():
            continue

        destination_key = join_s3_key(prefix, local_file.name)
        s3.upload_file(str(local_file), bucket, destination_key)

        logger.info(
            "Uploaded final metadata file %s to s3://%s/%s",
            local_file.name,
            bucket,
            destination_key,
        )


def build_ddt_prepared_message(
    reference: str,
    s3_objects_bucket: str,
    s3_objects_location_key: str,
    s3_metadata_bucket: str,
    s3_metadata_file_key: str,
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
            "reference": reference,
            "consignmentType": "STANDARD",
            "s3ObjectsBucket": s3_objects_bucket,
            "s3ObjectsLocationKey": s3_objects_location_key,
            "s3MetadataBucket": s3_metadata_bucket,
            "s3MetadataFileKey": s3_metadata_file_key,
        },
    }


def publish_ddt_message(message: dict[str, Any]) -> str:
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


def start_finalising_or_skip(run_id: str, consignment_reference: str) -> str:
    """
    Take the finaliser lock for a consignment.

    Returns:
      - STARTED when this invocation should continue finalising
      - ALREADY_SENT_TO_DDT when the DDT message was already published

    If another invocation is already finalising, raise an error so the SQS
    message retries/DLQs instead of publishing a duplicate DDT message.
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
        if (
            error.response.get("Error", {}).get("Code")
            != "ConditionalCheckFailedException"
        ):
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
        if (
            error.response.get("Error", {}).get("Code")
            == "ConditionalCheckFailedException"
        ):
            status = get_consignment_status(run_id, consignment_reference)

            if status == SENT_TO_DDT:
                logger.info(
                    "Consignment already marked SENT_TO_DDT. run_id=%s consignment=%s",
                    run_id,
                    consignment_reference,
                )
                return

        raise


def consignment_key(
    run_id: str, consignment_reference: str
) -> dict[str, dict[str, str]]:
    return {
        "PK": {"S": f"RUN#{run_id}"},
        "SK": {"S": f"CONSIGNMENT#{consignment_reference}"},
    }


def ensure_trailing_slash(value: str) -> str:
    value = str(value).strip()
    return value if value.endswith("/") else f"{value}/"


def join_s3_key(*parts: str) -> str:
    return "/".join(str(part).strip("/") for part in parts if part)


def require_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing required field: {key}")

    return value.strip().rstrip("/")


def utc_now_text() -> str:
    """Return UTC timestamp in DDT/Talend expected format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
