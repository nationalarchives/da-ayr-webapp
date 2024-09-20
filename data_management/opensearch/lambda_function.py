import logging
import os
from typing import Any, Dict, Tuple

from data_management.opensearch.index_file_content_and_metadata_in_opensearch_from_aws import (
    index_file_content_and_metadata_in_opensearch_from_aws,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> None:
    logger.info("Lambda started")
    bucket_name, object_key = _extract_s3_event_info(event)
    secret_id = os.getenv("SECRET_ID")
    index_file_content_and_metadata_in_opensearch_from_aws(
        bucket_name, object_key, secret_id
    )
    logger.info("Lambda complete")


def _extract_s3_event_info(event: Dict[str, Any]) -> Tuple[str, str]:
    s3_event_record = event["Records"][0]["s3"]
    return s3_event_record["bucket"]["name"], s3_event_record["object"]["key"]
