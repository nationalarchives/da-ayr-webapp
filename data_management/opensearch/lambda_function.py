import json
import logging
import os
from typing import Any, Dict, Tuple
from urllib.parse import quote_plus

import boto3
from requests_aws4auth import AWS4Auth

from data_management.opensearch.index_file_content_and_metadata_in_opensearch import (
    index_file_content_and_metadata_in_opensearch,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> None:
    logger.info("Lambda started")

    bucket_name, object_key = _extract_s3_event_info(event)
    secret_string = _get_secret_data(bucket_name)

    file_id = object_key.split("/")[-1]

    file_stream = _get_s3_file(secret_string["RECORD_BUCKET_NAME"], object_key)

    database_url = _build_db_url(secret_string)

    open_search_host_url = secret_string["OPEN_SEARCH_HOST"]
    open_search_http_auth = _get_opensearch_auth(secret_string)

    index_file_content_and_metadata_in_opensearch(
        file_id,
        file_stream,
        database_url,
        open_search_host_url,
        open_search_http_auth,
    )

    logger.info("Lambda complete")


def _extract_s3_event_info(event: Dict[str, Any]) -> Tuple[str, str]:
    s3_event_record = event["Records"][0]["s3"]
    return s3_event_record["bucket"]["name"], s3_event_record["object"]["key"]


def _get_secret_data(bucket_name: str) -> Dict[str, Any]:
    sm = boto3.client("secretsmanager")
    secret_id = os.getenv("SECRET_ID")
    secret_response = sm.get_secret_value(SecretId=secret_id)
    return json.loads(secret_response["SecretString"])


def _get_s3_file(bucket_name: str, object_key: str) -> bytes:
    s3 = boto3.client("s3")
    s3_file_object = s3.get_object(Bucket=bucket_name, Key=object_key)
    return s3_file_object["Body"].read()


def _get_opensearch_auth(secret_string: Dict[str, Any]) -> AWS4Auth:
    sts_client = boto3.client("sts")
    assumed_role = sts_client.assume_role(
        RoleArn=secret_string["OPEN_SEARCH_MASTER_ROLE_ARN"],
        RoleSessionName="LambdaOpenSearchSession",
    )
    logger.info("Extract temporary credentials to access OpenSearch with")
    credentials = assumed_role["Credentials"]
    open_search_http_auth = AWS4Auth(
        credentials["AccessKeyId"],
        credentials["SecretAccessKey"],
        secret_string["AWS_REGION"],
        "es",
        session_token=credentials["SessionToken"],
    )

    return open_search_http_auth


def _build_db_url(secret_string: Dict[str, Any]) -> str:
    return (
        "postgresql+pg8000://"
        f'{secret_string["DB_USER"]}:{quote_plus(secret_string["DB_PASSWORD"])}'
        f'@{secret_string["DB_HOST"]}:{secret_string["DB_PORT"]}/{secret_string["DB_NAME"]}'
    )
