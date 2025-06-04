import json
import logging
import os
from typing import Any, Dict

from .bulk_index_consignment import bulk_index_consignment_from_aws

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> None:

    logger.info("Lambda started")
    logger.info("Event received: %s", json.dumps(event))

    sns_message = json.loads(event["Records"][0]["Sns"]["Message"])
    consignment_reference = sns_message.get("parameters", {}).get("reference")

    if not consignment_reference:
        error_message = "Missing reference in SNS Message required for indexing"
        logger.error(error_message)
        raise Exception(error_message)

    secret_id = os.getenv("SECRET_ID")

    if not secret_id:
        error_message = (
            "Missing SECRET_ID environment variable required for indexing"
        )
        logger.error(error_message)
        raise Exception(error_message)

    db_secret_id = os.getenv("DB_SECRET_ID")

    if not db_secret_id:
        error_message = (
            "Missing DB_SECRET_ID environment variable required for indexing"
        )
        logger.error(error_message)
        raise Exception(error_message)

    # Log and process the consignment reference
    logger.info(f"Processing consignment reference: {consignment_reference}")
    bulk_index_consignment_from_aws(
        consignment_reference, secret_id, db_secret_id
    )
    logger.info("Lambda completed")
