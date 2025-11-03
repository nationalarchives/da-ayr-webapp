import json
import logging
import os

import boto3

from ..aws_helpers import (
    get_secret_data,
)
from .bulk_index_consignment import bulk_index_consignment_from_aws

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger()


class BulkIndexMultipleConsignmentsError(Exception):
    pass


def all_consignments_index(secret_string, db_secret_string):
    s3 = boto3.client("s3", region_name="eu-west-2")
    bucket_name = secret_string["RECORD_BUCKET_NAME"]
    paginator = s3.get_paginator("list_objects_v2")
    response = paginator.paginate(Bucket=bucket_name)
    consignments = set()
    for page in response:
        for obj in page["Contents"]:
            consignments.add(obj["Key"].split("/")[0])

    logger.info(f"Found {len(consignments)} consignments")

    errors = {}

    for consignment_reference in consignments:
        logger.info(f"Processing consignment: {consignment_reference}")
        try:
            bulk_index_consignment_from_aws(
                consignment_reference, secret_string, db_secret_string
            )
        except Exception as e:
            logger.error(f"{consignment_reference} had error(s):\n{e}")
            errors[consignment_reference] = str(e)

    if errors:
        error_summary_lines = [
            f"{consignment}: {msg}" for consignment, msg in errors.items()
        ]
        error_summary = (
            f"{len(errors)} consignments had error(s):\n"
            + "\n".join(error_summary_lines)
        )

        raise BulkIndexMultipleConsignmentsError(error_summary)

    logger.info("All consignments indexed without errors")


def single_consignment_index(secret_string, db_secret_string):

    raw_sns_message = os.getenv("SNS_MESSAGE")
    logger.info(f"Message Received: {raw_sns_message}")
    if not raw_sns_message:
        raise Exception("SNS_MESSAGE environment variable not found")

    try:
        sns_message = json.loads(raw_sns_message)
    except Exception as e:
        logger.error(f"Error parsing SNS_MESSAGE: {e}")
        raise

    consignment_reference = sns_message.get("parameters", {}).get("reference")

    if not consignment_reference:
        raise Exception(
            "Missing reference in SNS Message required for indexing"
        )
    logger.info(f"Processing consignment: {consignment_reference}")
    bulk_index_consignment_from_aws(
        consignment_reference, secret_string, db_secret_string
    )
    logger.info("Indexing completed")


def consignment_indexer():

    secret_id = os.getenv("SECRET_ID")
    db_secret_id = os.getenv("DB_SECRET_ID")
    if not secret_id or not db_secret_id:
        raise Exception(
            "Missing required environment variables: SECRET_ID or DB_SECRET_ID"
        )
    secret_string = get_secret_data(secret_id)
    db_secret_string = get_secret_data(db_secret_id)

    indexer_type = os.getenv("INDEXER_TYPE", "SINGLE")

    if indexer_type == "ALL":
        all_consignments_index(secret_string, db_secret_string)
    elif indexer_type == "SINGLE":
        single_consignment_index(secret_string, db_secret_string)
    else:
        raise ValueError("Invalid INDEXER_TYPE. Expected 'ALL' or 'SINGLE'")


if __name__ == "__main__":
    consignment_indexer()
