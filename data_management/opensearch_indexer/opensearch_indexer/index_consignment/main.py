import json
import logging
import os

from .bulk_index_consignment import bulk_index_consignment_from_aws

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger()


def consingment_indexer():

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

    secret_id = os.getenv("SECRET_ID")
    db_secret_id = os.getenv("DB_SECRET_ID")

    if not secret_id or not db_secret_id:
        raise Exception(
            "Missing required environment variables: SECRET_ID or DB_SECRET_ID"
        )

    logger.info(f"Processing consignment reference: {consignment_reference}")
    bulk_index_consignment_from_aws(
        consignment_reference, secret_id, db_secret_id
    )
    logger.info("Indexing completed")


if __name__ == "__main__":
    consingment_indexer()
