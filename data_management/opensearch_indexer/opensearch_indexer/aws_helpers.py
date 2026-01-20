import json
import logging
from typing import Any, Dict

import boto3
import psycopg2
from requests_aws4auth import AWS4Auth
from sqlalchemy import create_engine

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


def get_iam_connection(db_secret_string: Dict[str, Any]):
    rds = boto3.client("rds")
    host = db_secret_string["proxy"]
    port = int(db_secret_string["port"])
    user = db_secret_string["username"]
    dbname = db_secret_string["dbname"]

    token = rds.generate_db_auth_token(
        DBHostname=host, Port=port, DBUsername=user
    )

    return psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=token,
        database=dbname,
        sslmode="require",
        connect_timeout=10,
    )


def _build_db_engine(db_secret_string):

    def connection_creator():
        return get_iam_connection(db_secret_string)

    return create_engine(
        "postgresql+psycopg2://",
        creator=connection_creator,
        pool_pre_ping=True,
        pool_recycle=300,
    )
