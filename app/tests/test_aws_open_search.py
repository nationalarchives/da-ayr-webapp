from unittest.mock import patch

from flask import Flask
from opensearchpy import AWSV4SignerAuth

from app.main.aws.open_search import (
    generate_open_search_client_from_current_app_config,
    get_open_search_http_auth,
)


@patch("app.main.aws.open_search.get_open_search_http_auth")
@patch("app.main.aws.open_search.OpenSearch")
def test_generate_open_search_client_from_current_app_config(
    mock_opensearch, mock_get_open_search_http_auth
):
    """
    Given a Flask application and the necessary configuration set for OpenSearch
    When generating an OpenSearch client using the current application's configuration
    Then an OpenSearch client should be created with the expected configuration
    """
    app = Flask("test")
    app.config["AWS_OPEN_SEARCH_HOST"] = "mock_host"

    with app.app_context():
        assert (
            generate_open_search_client_from_current_app_config()
            == mock_opensearch.return_value
        )
        mock_opensearch.assert_called_once_with(
            hosts=[{"host": "mock_host", "port": 443}],
            http_auth=mock_get_open_search_http_auth.return_value,
            use_ssl=True,
            verify_certs=True,
            http_compress=True,
            ssl_assert_hostname=False,
            ssl_show_warn=True,
        )


def test_get_open_search_http_auth():
    """
    Given a Flask application with AWS_OPEN_SEARCH_USERNAME, AWS_OPEN_SEARCH_PASSWORD in the config
    When calling get_open_search_http_auth with iam as `False`
    Then a tuple of the username and password is returned
    """
    app = Flask("test")
    app.config["AWS_OPEN_SEARCH_USERNAME"] = "test_username"
    app.config[
        "AWS_OPEN_SEARCH_PASSWORD"
    ] = "test_password"  # pragma: allowlist secret

    with app.app_context():
        assert get_open_search_http_auth(iam=False) == (
            "test_username",
            "test_password",
        )


@patch("app.main.aws.open_search.boto3.Session")
def test_get_open_search_http_auth_iam(mock_boto3_session):
    """
    Given a mock Boto3 Session and the current app's configuration set for OpenSearch
    When calling get_open_search_http_auth with iam as "True"
    Then it should return an AWSV4SignerAuth object created using the mock AWS
        credentials and AWS region from the current app's configuration.
    """
    app = Flask("test")
    app.config["AWS_REGION"] = "us-east-1"

    mock_session_instance = mock_boto3_session.return_value
    mock_session_instance.get_credentials.return_value = "mock_credentials"

    with app.app_context():
        auth = get_open_search_http_auth(iam=True)

    assert isinstance(auth, AWSV4SignerAuth)
    assert auth.credentials == "mock_credentials"
    assert auth.region == "us-east-1"
    assert auth.service == "es"
