import json
import logging
from typing import Any, Dict
from urllib.parse import quote_plus

import boto3
from requests_aws4auth import AWS4Auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_s3_file(bucket_name: str, object_key: str) -> bytes:
    s3 = boto3.client("s3")
    s3_file_object = s3.get_object(Bucket=bucket_name, Key=object_key)
    return s3_file_object["Body"].read()


def get_secret_data(secret_id: str) -> Dict[str, Any]:
    sm = boto3.client("secretsmanager")
    secret_response = sm.get_secret_value(SecretId=secret_id)
    return json.loads(secret_response["SecretString"])


def _build_db_url(secret_string: Dict[str, Any]) -> str:
    return (
        "postgresql+pg8000://"
        f'{secret_string["DB_USER"]}:{quote_plus(secret_string["DB_PASSWORD"])}'
        f'@{secret_string["DB_HOST"]}:{secret_string["DB_PORT"]}/{secret_string["DB_NAME"]}'
    )


def _get_opensearch_auth(secret_string: Dict[str, Any]) -> AWS4Auth:
    sts_client = boto3.client("sts")
    assumed_role = sts_client.assume_role(
        RoleArn=secret_string["OPEN_SEARCH_MASTER_ROLE_ARN"],
        RoleSessionName="LambdaOpenSearchSession",
    )
    logger.info("Extract temporary credentials to access OpenSearch")
    credentials = assumed_role["Credentials"]
    open_search_http_auth = AWS4Auth(
        credentials["AccessKeyId"],
        credentials["SecretAccessKey"],
        secret_string["AWS_REGION"],
        "es",
        session_token=credentials["SessionToken"],
    )

    return open_search_http_auth
