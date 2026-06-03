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


def get_iam_connection(db_secret_string: Dict[str, Any]):
    rds = boto3.client("rds")
    host = db_secret_string["proxy"]
    port = int(db_secret_string["port"])
    user = db_secret_string["username"]

    return rds.generate_db_auth_token(
        DBHostname=host, Port=port, DBUsername=user
    )


def _build_db_url(db_secret_string: Dict[str, Any]) -> str:
    token = get_iam_connection(db_secret_string)
    return (
        "postgresql+pg8000://"
        f"{db_secret_string['username']}:{quote_plus(token)}"
        f"@{db_secret_string['proxy']}:{db_secret_string['port']}/{db_secret_string['dbname']}"
    )


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
