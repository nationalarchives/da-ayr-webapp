import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
sqs = boto3.client("sqs")
dynamodb = boto3.client("dynamodb")

DRI_JSON_BUCKET = os.environ["DRI_JSON_BUCKET"]
WORKER_QUEUE_URL = os.environ["WORKER_QUEUE_URL"]
TRACKING_TABLE_NAME = os.environ["TRACKING_TABLE_NAME"]

JSON_PREFIX = os.getenv("JSON_PREFIX", "live")
DEFAULT_DUMMY_CONSIGNMENT_PREFIX = f"DRI-TO-AYR-{datetime.today().year}"

MAX_FILES_PER_FAKE_CONSIGNMENT = int(
    os.getenv("MAX_FILES_PER_FAKE_CONSIGNMENT", "1000")
)

if MAX_FILES_PER_FAKE_CONSIGNMENT < 1:
    raise ValueError("MAX_FILES_PER_FAKE_CONSIGNMENT must be greater than 0")


# If a consignment has reached one of these statuses, the coordinator must not
# create or resend worker messages for it.
CONSIGNMENT_STATUSES_SKIP_WORKER = {
    "READY_TO_FINALISE",
    "FINALISING",
    "SENT_TO_DDT",
}

# We only skip files that are definitely finished.
FILE_STATUSES_SKIP_WORKER = {
    "COMPLETE",
}


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Start a series migration.

    Expected event:
    {
      "series": "LEV 2"
    }

    The coordinator lists DRI JSON files for the series, groups records by
    ConsignmentReference, writes tracking rows, and sends one worker SQS message
    per record.
    """
    series = require_text(event, "series")
    run_id = resolve_run_id(event, series)

    logger.info("Starting migration run_id=%s series=%s", run_id, series)

    records = list_series_records(series)

    if not records:
        raise ValueError(f"No DRI JSON records found for series: {series}")

    consignment_groups = group_records_by_consignment(records, series)

    worker_messages_sent = 0
    consignments_skipped = []
    files_skipped = 0

    for consignment_reference, group_records in consignment_groups.items():
        result = process_consignment_group(
            run_id=run_id,
            series=series,
            consignment_reference=consignment_reference,
            group_records=group_records,
        )

        worker_messages_sent += result["workerMessagesSent"]
        files_skipped += result["filesSkipped"]

        if result["consignmentSkipped"]:
            consignments_skipped.append(result["consignmentSkipped"])

    return {
        "status": "started",
        "runId": run_id,
        "series": series,
        "maxFilesPerFakeConsignment": MAX_FILES_PER_FAKE_CONSIGNMENT,
        "recordCount": len(records),
        "consignmentCount": len(consignment_groups),
        "workerMessagesSent": worker_messages_sent,
        "filesSkipped": files_skipped,
        "consignmentsSkipped": consignments_skipped,
        "consignments": [
            {
                "consignmentReference": consignment_reference,
                "expectedFileCount": len(group_records),
            }
            for consignment_reference, group_records in consignment_groups.items()
        ],
    }


def process_consignment_group(
    run_id: str,
    series: str,
    consignment_reference: str,
    group_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create/check consignment tracking and send worker messages for its records."""
    existing_consignment = get_consignment_tracking_item(
        run_id=run_id,
        consignment_reference=consignment_reference,
    )

    if existing_consignment:
        consignment_status = get_ddb_string(existing_consignment, "status")
        logger.info(
            "Existing consignment found run_id=%s consignment=%s status=%s",
            run_id,
            consignment_reference,
            consignment_status,
        )

        if consignment_status in CONSIGNMENT_STATUSES_SKIP_WORKER:
            logger.info(
                "Skipping worker messages for consignment=%s because status=%s",
                consignment_reference,
                consignment_status,
            )
            return {
                "workerMessagesSent": 0,
                "filesSkipped": 0,
                "consignmentSkipped": {
                    "consignmentReference": consignment_reference,
                    "status": consignment_status,
                },
            }
    else:
        put_consignment_tracking_item(
            run_id=run_id,
            series=series,
            consignment_reference=consignment_reference,
            expected_file_count=len(group_records),
        )

    worker_messages_sent = 0
    files_skipped = 0

    for record in group_records:
        result = process_record(
            run_id=run_id,
            series=series,
            consignment_reference=consignment_reference,
            record=record,
        )
        worker_messages_sent += result["workerMessageSent"]
        files_skipped += result["fileSkipped"]

    return {
        "workerMessagesSent": worker_messages_sent,
        "filesSkipped": files_skipped,
        "consignmentSkipped": None,
    }


def process_record(
    run_id: str,
    series: str,
    consignment_reference: str,
    record: dict[str, Any],
) -> dict[str, int]:
    """Create/check file tracking and send a worker message if needed."""
    file_id = require_file_id(record)

    existing_file = get_file_tracking_item(
        run_id=run_id,
        consignment_reference=consignment_reference,
        file_id=file_id,
    )

    if existing_file:
        file_status = get_ddb_string(existing_file, "status")
        if file_status in FILE_STATUSES_SKIP_WORKER:
            logger.info(
                "Skipping worker message for file=%s consignment=%s because status=%s",
                file_id,
                consignment_reference,
                file_status,
            )
            return {
                "workerMessageSent": 0,
                "fileSkipped": 1,
            }
    else:
        put_file_tracking_item(
            run_id=run_id,
            series=series,
            consignment_reference=consignment_reference,
            record=record,
            file_id=file_id,
        )

    send_worker_message(
        run_id=run_id,
        series=series,
        reference=require_text(record, "reference"),
        consignment_reference=consignment_reference,
        file_id=file_id,
    )

    return {
        "workerMessageSent": 1,
        "fileSkipped": 0,
    }


def group_records_by_consignment(
    records: list[dict[str, Any]],
    series: str,
) -> dict[str, list[dict[str, Any]]]:
    """
    Group records by ConsignmentReference.

    Real consignments use tdrConsignmentId and can contain any number of files.
    Fake consignments are chunked so each fake consignment contains no more than
    MAX_FILES_PER_FAKE_CONSIGNMENT records.
    """
    consignment_groups: dict[str, list[dict[str, Any]]] = {}
    fake_consignment_records: list[dict[str, Any]] = []

    for record in sorted(records, key=record_sort_key):
        real_consignment_reference = get_real_consignment_reference(record)

        if real_consignment_reference:
            consignment_groups.setdefault(
                real_consignment_reference, []
            ).append(record)
        else:
            fake_consignment_records.append(record)

    fake_chunks = chunk_fake_records(fake_consignment_records)

    for chunk_number, chunk_records in enumerate(fake_chunks, start=1):
        fake_consignment_reference = build_fake_consignment_reference(
            series=series,
            chunk_number=chunk_number,
        )
        consignment_groups[fake_consignment_reference] = chunk_records

    return consignment_groups


def chunk_fake_records(
    records: list[dict[str, Any]],
) -> list[list[dict[str, Any]]]:
    """Split fake-consignment records into chunks under the configured record limit."""
    sorted_records = sorted(records, key=record_sort_key)

    return [
        sorted_records[index : index + MAX_FILES_PER_FAKE_CONSIGNMENT]
        for index in range(
            0, len(sorted_records), MAX_FILES_PER_FAKE_CONSIGNMENT
        )
    ]


def get_real_consignment_reference(record: dict[str, Any]) -> str | None:
    """Return tdrConsignmentId when present, otherwise None."""
    tdr_consignment_id = record.get("tdrConsignmentId")

    if tdr_consignment_id:
        return tdr_consignment_id

    return None


def build_fake_consignment_reference(series: str, chunk_number: int) -> str:
    """Build a deterministic fake ConsignmentReference for missing tdrConsignmentId records."""
    return (
        f"{DEFAULT_DUMMY_CONSIGNMENT_PREFIX}-"
        f"{safe_reference(series)}-"
        f"{chunk_number:04d}"
    )


def record_sort_key(record: dict[str, Any]) -> str:
    """Return the record reference so fake consignment chunking is repeatable."""
    return record["reference"]


def list_series_records(series: str) -> list[dict[str, Any]]:
    """List and load DRI JSON records for a series."""
    prefix = join_s3_key(JSON_PREFIX, f"{series}-")
    logger.info(
        "Listing DRI JSON records from s3://%s/%s", DRI_JSON_BUCKET, prefix
    )

    records: list[dict[str, Any]] = []
    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=DRI_JSON_BUCKET, Prefix=prefix):
        for item in page.get("Contents", []):
            key = item["Key"]

            if not key.endswith(".json"):
                continue

            record = read_json_record(key)
            record_reference = record.get("reference")

            if not isinstance(
                record_reference, str
            ) or not record_reference.startswith(f"{series}/"):
                logger.warning(
                    "Skipping JSON because record.reference does not belong to series. key=%s reference=%s series=%s",
                    key,
                    record_reference,
                    series,
                )
                continue

            records.append(record)

    return records


def read_json_record(key: str) -> dict[str, Any]:
    response = s3.get_object(Bucket=DRI_JSON_BUCKET, Key=key)
    body = response["Body"].read().decode("utf-8")
    data = json.loads(body)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected JSON object in s3://{DRI_JSON_BUCKET}/{key}"
        )

    return data


def require_file_id(record: dict[str, Any]) -> str:
    try:
        file_id = record["digitalFiles"][0]["fileId"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(
            f"Missing digitalFiles[].fileId for reference={record.get('reference')}"
        ) from exc

    if isinstance(file_id, str) and file_id.strip():
        return file_id.strip()

    raise ValueError(
        f"Missing digitalFiles[].fileId for reference={record.get('reference')}"
    )


def get_consignment_tracking_item(
    run_id: str,
    consignment_reference: str,
) -> dict[str, Any] | None:
    response = dynamodb.get_item(
        TableName=TRACKING_TABLE_NAME,
        Key={
            "PK": {"S": f"RUN#{run_id}"},
            "SK": {"S": f"CONSIGNMENT#{consignment_reference}"},
        },
    )
    return response.get("Item")


def get_file_tracking_item(
    run_id: str,
    consignment_reference: str,
    file_id: str,
) -> dict[str, Any] | None:
    response = dynamodb.get_item(
        TableName=TRACKING_TABLE_NAME,
        Key={
            "PK": {"S": f"RUN#{run_id}#CONSIGNMENT#{consignment_reference}"},
            "SK": {"S": f"FILE#{file_id}"},
        },
    )
    return response.get("Item")


def put_consignment_tracking_item(
    run_id: str,
    series: str,
    consignment_reference: str,
    expected_file_count: int,
) -> None:
    now = utc_now_text()

    try:
        dynamodb.put_item(
            TableName=TRACKING_TABLE_NAME,
            ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
            Item={
                "PK": {"S": f"RUN#{run_id}"},
                "SK": {"S": f"CONSIGNMENT#{consignment_reference}"},
                "entityType": {"S": "CONSIGNMENT"},
                "runId": {"S": run_id},
                "series": {"S": series},
                "consignmentReference": {"S": consignment_reference},
                "expectedFileCount": {"N": str(expected_file_count)},
                "completedFileCount": {"N": "0"},
                "failedFileCount": {"N": "0"},
                "status": {"S": "STAGING"},
                "createdAt": {"S": now},
                "updatedAt": {"S": now},
            },
        )
    except ClientError as exc:
        if (
            exc.response.get("Error", {}).get("Code")
            == "ConditionalCheckFailedException"
        ):
            logger.info(
                "Consignment tracking item already exists run_id=%s consignment=%s",
                run_id,
                consignment_reference,
            )
            return
        raise


def put_file_tracking_item(
    run_id: str,
    series: str,
    consignment_reference: str,
    record: dict[str, Any],
    file_id: str,
) -> None:
    now = utc_now_text()
    reference = require_text(record, "reference")

    try:
        dynamodb.put_item(
            TableName=TRACKING_TABLE_NAME,
            ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
            Item={
                "PK": {
                    "S": f"RUN#{run_id}#CONSIGNMENT#{consignment_reference}"
                },
                "SK": {"S": f"FILE#{file_id}"},
                "entityType": {"S": "FILE"},
                "runId": {"S": run_id},
                "series": {"S": series},
                "consignmentReference": {"S": consignment_reference},
                "reference": {"S": reference},
                "fileId": {"S": file_id},
                "status": {"S": "PENDING"},
                "createdAt": {"S": now},
                "updatedAt": {"S": now},
            },
        )
    except ClientError as exc:
        if (
            exc.response.get("Error", {}).get("Code")
            == "ConditionalCheckFailedException"
        ):
            logger.info(
                "File tracking item already exists run_id=%s consignment=%s file_id=%s",
                run_id,
                consignment_reference,
                file_id,
            )
            return
        raise


def send_worker_message(
    run_id: str,
    series: str,
    reference: str,
    consignment_reference: str,
    file_id: str,
) -> None:
    message = {
        "runId": run_id,
        "series": series,
        "reference": reference,
        "consignmentReference": consignment_reference,
        "fileId": file_id,
    }

    sqs.send_message(
        QueueUrl=WORKER_QUEUE_URL,
        MessageBody=json.dumps(message),
    )


def resolve_run_id(event: dict[str, Any], series: str) -> str:
    """
    Resolve whether this is a resume or a new run.

    If runId is supplied, we assume the caller intentionally wants to resume
    that exact run.

    If runId is not supplied, we check whether this series has already been
    started before creating a new run. This avoids accidentally running the
    same series again and sending duplicate worker messages.

    To deliberately create a new run for the same series, pass:
      {"series": "MIG 1", "forceNewRun": true}
    """
    supplied_run_id = event.get("runId")

    if isinstance(supplied_run_id, str) and supplied_run_id.strip():
        return supplied_run_id.strip()

    force_new_run = event.get("forceNewRun") is True

    if series_has_existing_run(series):
        if not force_new_run:
            raise ValueError(
                f"Existing migration run found for series '{series}'. "
                "Please provide runId to resume the existing run, or set "
                "forceNewRun=true to deliberately start a new run."
            )

        logger.warning(
            "forceNewRun=true supplied for series=%s. Existing run will not be resumed.",
            series,
        )

    return build_run_id(series)


def series_has_existing_run(series: str) -> bool:
    """Return True if this series already has tracking rows for a run."""
    paginator = dynamodb.get_paginator("scan")

    for page in paginator.paginate(
        TableName=TRACKING_TABLE_NAME,
        FilterExpression="#series = :series AND attribute_exists(runId)",
        ProjectionExpression="runId",
        ExpressionAttributeNames={
            "#series": "series",
        },
        ExpressionAttributeValues={
            ":series": {"S": series},
        },
    ):
        if page.get("Items"):
            return True

    return False


def get_ddb_string(item: dict[str, Any], key: str) -> str | None:
    value = item.get(key)

    if not isinstance(value, dict):
        return None

    text = value.get("S")

    if isinstance(text, str) and text.strip():
        return text.strip()

    return None


def require_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing required field: {key}")

    return value.strip().rstrip("/")


def safe_reference(reference: str) -> str:
    return re.sub(r"[^A-Za-z0-9._=-]+", "-", reference).strip("-")


def join_s3_key(*parts: str) -> str:
    return "/".join(part.strip("/") for part in parts)


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_run_id(series: str) -> str:
    timestamp = int(time.time())
    return f"{safe_reference(series)}-{timestamp}-{uuid.uuid4().hex[:8]}"
