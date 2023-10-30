from typing import Tuple

import boto3
from opensearchpy import AWSV4SignerAuth, OpenSearch

from app.main.aws.parameter import (
    get_aws_environment_prefix,
    get_parameter_store_key_value,
)


def get_open_search_index_from_aws_params() -> str:
    return get_parameter_store_key_value(
        get_aws_environment_prefix() + "AWS_OPEN_SEARCH_INDEX"
    )


def generate_open_search_client_from_aws_params() -> OpenSearch:
    host = get_parameter_store_key_value(
        get_aws_environment_prefix() + "AWS_OPEN_SEARCH_HOST"
    )
    http_auth = _get_open_search_http_auth()

    open_search_client = OpenSearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=http_auth,
        use_ssl=True,
        verify_certs=True,
        http_compress=True,
        ssl_assert_hostname=False,
        ssl_show_warn=True,
    )
    return open_search_client


def _get_open_search_http_auth(
    auth_method: str = "username_password",
) -> Tuple[str, str] | AWSV4SignerAuth:
    if auth_method == "username_password":
        return _get_open_search_username_password_auth()
    return _get_open_search_iam_auth()


def _get_open_search_username_password_auth() -> Tuple[str, str]:
    username = get_parameter_store_key_value(
        get_aws_environment_prefix() + "AWS_OPEN_SEARCH_USERNAME"
    )
    password = get_parameter_store_key_value(
        get_aws_environment_prefix() + "AWS_OPEN_SEARCH_PASSWORD"
    )
    return (username, password)


def _get_open_search_iam_auth() -> AWSV4SignerAuth:
    credentials = boto3.Session().get_credentials()
    aws_region = get_parameter_store_key_value(
        get_aws_environment_prefix() + "AWS_REGION"
    )
    service = "es"
    aws_auth = AWSV4SignerAuth(credentials, aws_region, service)
    return aws_auth
