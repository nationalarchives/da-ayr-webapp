import json
import logging
from typing import Any, Dict

import boto3
from requests_aws4auth import AWS4Auth

from .aws_helpers import _build_db_url, get_secret_data
from .index_file_content_and_metadata_in_opensearch import (
    index_file_content_and_metadata_in_opensearch,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def index_file_content_and_metadata_in_opensearch_from_aws(
    bucket_name, object_key, secret_id, db_secret_id
):
    secret_string = get_secret_data(secret_id)
    db_secret_string = get_secret_data(db_secret_id)

    file_id = object_key.split("/")[-1]

    file_stream = get_s3_file(bucket_name, object_key)

    database_url = _build_db_url(db_secret_string)

    open_search_host_url = secret_string["OPEN_SEARCH_HOST"]
    open_search_http_auth = _get_opensearch_auth(secret_string)

    index_file_content_and_metadata_in_opensearch(
        file_id,
        file_stream,
        database_url,
        open_search_host_url,
        open_search_http_auth,
    )

    sm = boto3.client("secretsmanager")
    secret_response = sm.get_secret_value(SecretId=secret_id)
    return json.loads(secret_response["SecretString"])


def get_s3_file(bucket_name: str, object_key: str) -> bytes:
    s3 = boto3.client("s3")
    s3_file_object = s3.get_object(Bucket=bucket_name, Key=object_key)
    return s3_file_object["Body"].read()


def _get_opensearch_auth(secret_string: Dict[str, Any]) -> AWS4Auth:
    session = boto3.Session()
    credentials = session.get_credentials()
    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        secret_string["AWS_REGION"],
        "es",
        session_token=credentials.token,
    )
    return auth
