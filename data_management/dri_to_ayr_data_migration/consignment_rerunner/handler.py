import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DYNAMODB_TRANSACTION_MAX_ACTIONS = 100
FILE_RESETS_PER_TRANSACTION = DYNAMODB_TRANSACTION_MAX_ACTIONS - 1


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    TRACKING_TABLE_NAME = os.environ["TRACKING_TABLE_NAME"]
    WORKER_QUEUE_URL = os.environ["WORKER_QUEUE_URL"]
    DDT_TEMP_CSV_BUCKET = os.environ["DDT_TEMP_CSV_BUCKET"]
    STAGING_PREFIX = os.getenv("STAGING_PREFIX", "ayr-mds-staging")
    OUTPUT_PREFIX = os.getenv("OUTPUT_PREFIX", "ayr-mds-csv")

    dynamodb = boto3.client("dynamodb")
    sqs = boto3.client("sqs")
    run_id = require_text(event, "runId")
    series = require_text(event, "series")
    consignment_reference = require_text(
        event,
        "consignmentReference",
    )

    reason = event.get("reason", "Manual rerun")

    if not isinstance(reason, str):
        raise ValueError("reason must be a string")

    triggered_by = event.get("triggeredBy", "unknown")

    if not isinstance(triggered_by, str):
        raise ValueError("triggeredBy must be a string")

    response = dynamodb.get_item(
        TableName=TRACKING_TABLE_NAME,
        Key={
            "PK": {"S": f"RUN#{run_id}"},
            "SK": {"S": f"CONSIGNMENT#{consignment_reference}"},
        },
        ConsistentRead=True,
    )
    tracked_series = response.get("Item", {}).get("series", {}).get("S")
    if tracked_series != series:
        raise ValueError(
            f"Series {series!r} does not match tracked series "
            f"{tracked_series!r} for consignment {consignment_reference}"
        )

    files = get_files(
        run_id=run_id,
        consignment_reference=consignment_reference,
        dynamodb=dynamodb,
        tracking_table_name=TRACKING_TABLE_NAME,
    )

    if not files:
        raise ValueError(
            f"No files found for consignment {consignment_reference}"
        )

    logger.info(
        "Found %s files for consignment %s",
        len(files),
        consignment_reference,
    )

    include_consignment = True

    reset_tracking_for_rerun(
        run_id=run_id,
        series=series,
        consignment_reference=consignment_reference,
        reason=reason,
        triggered_by=triggered_by,
        files=files,
        tracking_table_name=TRACKING_TABLE_NAME,
        dynamodb=dynamodb,
    )

    cleanup_result = prepare_consignment_rerun(
        series=series,
        consignment_reference=consignment_reference,
        ddt_temp_csv_bucket=DDT_TEMP_CSV_BUCKET,
        staging_prefix=STAGING_PREFIX,
        output_prefix=OUTPUT_PREFIX,
    )

    for file_item in files:
        payload = {
            "runId": run_id,
            "series": series,
            "reference": file_item["reference"],
            "consignmentReference": consignment_reference,
            "fileId": file_item["fileId"],
            "includeBodyAndSeries": False,
            "includeConsignment": include_consignment,
        }

        sqs.send_message(
            QueueUrl=WORKER_QUEUE_URL,
            MessageBody=json.dumps(payload),
        )

        include_consignment = False

    logger.info(
        "Queued %s worker messages for %s",
        len(files),
        consignment_reference,
    )

    return {
        "consignmentReference": consignment_reference,
        "filesQueued": len(files),
        **cleanup_result,
    }


def get_files(
    run_id: str,
    consignment_reference: str,
    dynamodb: Any,
    tracking_table_name: str,
) -> list[dict[str, str]]:

    pk = f"RUN#{run_id}#CONSIGNMENT#{consignment_reference}"

    items = []
    last_key = None

    while True:
        request = {
            "TableName": tracking_table_name,
            "ConsistentRead": True,
            "KeyConditionExpression": "PK = :pk",
            "ExpressionAttributeValues": {
                ":pk": {"S": pk},
            },
        }

        if last_key:
            request["ExclusiveStartKey"] = last_key

        response = dynamodb.query(**request)

        items.extend(response.get("Items", []))

        last_key = response.get("LastEvaluatedKey")

        if not last_key:
            break

    results = []

    for item in items:
        if item.get("entityType", {}).get("S") != "FILE":
            continue

        results.append(
            {
                "reference": item["reference"]["S"],
                "fileId": item["fileId"]["S"],
            }
        )

    return results


def require_text(
    data: dict[str, Any],
    key: str,
) -> str:

    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing required field: {key}")

    return value.strip()


def reset_tracking_for_rerun(
    run_id: str,
    series: str,
    consignment_reference: str,
    reason: str,
    triggered_by: str,
    files: list[dict[str, str]],
    tracking_table_name: str,
    dynamodb: Any,
) -> None:
    """Reset tracking before publishing any worker messages.

    DynamoDB permits 100 actions per transaction. Reserve one action for the
    consignment update or condition check, leaving room for 99 file resets.

    With at most 99 files, one transaction resets every file to PENDING and
    returns the consignment to STAGING, zeroing its completed count, removing
    old completion/finaliser markers, and recording the rerun once.

    Larger consignments cannot reset atomically in a single transaction:
    1. Set RERUN_PREPARING so DROID's STAGING-only completion cannot proceed.
    2. Reset batches of 99 files, checking in each transaction that the
       consignment is still RERUN_PREPARING.
    3. Atomically reset the remaining files and update the consignment as above.
       Only this final transaction re-enables DROID completion.

    The caller must wait for this function to succeed before queueing workers.
    Errors propagate without queueing work. A failed batch leaves the large
    consignment in RERUN_PREPARING; after the pipeline is quiescent, retrying
    the rerun repeats the file resets.
    """
    now = utc_now_text()
    consignment_key = {
        "PK": {"S": f"RUN#{run_id}"},
        "SK": {"S": f"CONSIGNMENT#{consignment_reference}"},
    }
    file_updates = [
        {
            "Update": {
                "TableName": tracking_table_name,
                "Key": {
                    "PK": {
                        "S": f"RUN#{run_id}#CONSIGNMENT#{consignment_reference}"
                    },
                    "SK": {"S": f"FILE#{file_item['fileId']}"},
                },
                "UpdateExpression": (
                    "SET #status = :pending, updatedAt = :now REMOVE completedAt"
                ),
                "ConditionExpression": "attribute_exists(PK)",
                "ExpressionAttributeNames": {"#status": "status"},
                "ExpressionAttributeValues": {
                    ":pending": {"S": "PENDING"},
                    ":now": {"S": now},
                },
            }
        }
        for file_item in files
    ]
    condition = (
        "attribute_exists(PK) AND series = :series AND expectedFileCount = :file_count AND "
        "#status IN (:sent, :staging, :preparing)"
    )
    condition_values = {
        ":sent": {"S": "SENT_TO_DDT"},
        ":staging": {"S": "STAGING"},
        ":preparing": {"S": "RERUN_PREPARING"},
        ":series": {"S": series},
    }

    if len(file_updates) > FILE_RESETS_PER_TRANSACTION:
        dynamodb.update_item(
            TableName=tracking_table_name,
            Key=consignment_key,
            UpdateExpression="SET #status = :preparing, updatedAt = :now",
            ConditionExpression=condition,
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                **condition_values,
                ":file_count": {"N": str(len(files))},
                ":now": {"S": now},
            },
        )
        condition = (
            "#status = :preparing AND series = :series "
            "AND expectedFileCount = :file_count"
        )
        condition_values = {
            ":preparing": {"S": "RERUN_PREPARING"},
            ":series": {"S": series},
        }

        while len(file_updates) > FILE_RESETS_PER_TRANSACTION:
            dynamodb.transact_write_items(
                TransactItems=[
                    {
                        "ConditionCheck": {
                            "TableName": tracking_table_name,
                            "Key": consignment_key,
                            "ConditionExpression": condition,
                            "ExpressionAttributeNames": {"#status": "status"},
                            "ExpressionAttributeValues": {
                                **condition_values,
                                ":file_count": {"N": str(len(files))},
                            },
                        }
                    },
                    *file_updates[:FILE_RESETS_PER_TRANSACTION],
                ]
            )
            file_updates = file_updates[FILE_RESETS_PER_TRANSACTION:]

    dynamodb.transact_write_items(
        TransactItems=[
            {
                "Update": {
                    "TableName": tracking_table_name,
                    "Key": consignment_key,
                    "UpdateExpression": """
            SET
                #status = :staging,
                completedFileCount = :zero,
                lastRerunAt = :now,
                lastRerunReason = :reason,
                lastRerunTriggeredBy = :triggered_by,
                lastRerunFileCount = :file_count,
                rerunType = :rerun_type,
                updatedAt = :now
            REMOVE
                finaliserMessageSentAt,
                finaliserSqsMessageId,
                readyAt,
                finalisingStartedAt,
                finalisingFailedAt,
                sentToDdtAt,
                ddtSnsMessageId
            ADD
                rerunCount :one
        """,
                    "ConditionExpression": condition,
                    "ExpressionAttributeNames": {"#status": "status"},
                    "ExpressionAttributeValues": {
                        **condition_values,
                        ":staging": {"S": "STAGING"},
                        ":zero": {"N": "0"},
                        ":now": {"S": now},
                        ":reason": {"S": reason},
                        ":triggered_by": {"S": triggered_by},
                        ":file_count": {"N": str(len(files))},
                        ":rerun_type": {"S": "WORKER_REPROCESS"},
                        ":one": {"N": "1"},
                    },
                }
            },
            *file_updates,
        ],
    )


def utc_now_text() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def prepare_consignment_rerun(
    series: str,
    consignment_reference: str,
    ddt_temp_csv_bucket: str,
    staging_prefix: str,
    output_prefix: str,
) -> dict[str, int]:
    s3 = boto3.client("s3")

    deleted_staging = delete_prefix(
        s3=s3,
        bucket=ddt_temp_csv_bucket,
        prefix=join_s3_key(
            series,
            staging_prefix,
            consignment_reference,
        ),
    )

    deleted_output = delete_prefix(
        s3=s3,
        bucket=ddt_temp_csv_bucket,
        prefix=join_s3_key(
            series,
            output_prefix,
            consignment_reference,
        ),
    )

    logger.info(
        "Prepared consignment rerun. "
        "consignment=%s "
        "deleted_staging=%s "
        "deleted_output=%s",
        consignment_reference,
        deleted_staging,
        deleted_output,
    )

    return {
        "deletedStagingObjects": deleted_staging,
        "deletedOutputObjects": deleted_output,
    }


def delete_prefix(
    s3: Any,
    bucket: str,
    prefix: str,
) -> int:

    paginator = s3.get_paginator("list_objects_v2")

    deleted = 0

    for page in paginator.paginate(
        Bucket=bucket,
        Prefix=ensure_trailing_slash(prefix),
    ):
        keys = page.get("Contents", [])

        if not keys:
            continue

        objects = [{"Key": item["Key"]} for item in keys]

        response = s3.delete_objects(
            Bucket=bucket,
            Delete={"Objects": objects},
        )

        errors = response.get("Errors", [])
        if errors:
            raise RuntimeError(
                f"Failed to delete {len(errors)} objects from "
                f"bucket={bucket} prefix={prefix}: "
                + ", ".join(
                    f"{error.get('Key', '<unknown>')}: "
                    f"{error.get('Code', '<unknown>')} "
                    f"{error.get('Message', '')}"
                    for error in errors
                )
            )

        deleted += len(objects)

    return deleted


def ensure_trailing_slash(value: str) -> str:
    value = value.strip()
    return value if value.endswith("/") else f"{value}/"


def join_s3_key(*parts: str) -> str:
    return "/".join(part.strip("/") for part in parts if part)
