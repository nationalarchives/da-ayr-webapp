from typing import Tuple

import boto3
from flask import current_app
from opensearchpy import AWSV4SignerAuth, OpenSearch


def generate_open_search_client_from_current_app_config() -> OpenSearch:
    """
    Generate an OpenSearch client with the specified configuration for the AYR application.

    Returns:
        OpenSearch: An OpenSearch client configured with settings obtained from the current app's configuration.
    """
    open_search_client = OpenSearch(
        hosts=[
            {"host": current_app.config["AWS_OPEN_SEARCH_HOST"], "port": 443}
        ],
        http_auth=get_open_search_http_auth(),
        use_ssl=True,
        verify_certs=True,
        http_compress=True,
        ssl_assert_hostname=False,
        ssl_show_warn=True,
    )
    return open_search_client


def get_open_search_http_auth(iam=False) -> Tuple[str, str] | AWSV4SignerAuth:
    """
    Get the authentication method for OpenSearch.

    Args:
        iam (bool): A boolean indicating whether IAM authentication should be used.

    Returns:
        Tuple[str, str] | AWSV4SignerAuth: Depending on the IAM parameter
    """
    if not iam:
        return (
            current_app.config["AWS_OPEN_SEARCH_USERNAME"],
            current_app.config["AWS_OPEN_SEARCH_PASSWORD"],
        )
    return _get_open_search_iam_auth(current_app.config["AWS_REGION"])


def _get_open_search_iam_auth(aws_region) -> AWSV4SignerAuth:
    credentials = boto3.Session().get_credentials()
    service = "es"
    aws_auth = AWSV4SignerAuth(credentials, aws_region, service)
    return aws_auth
