from unittest.mock import patch

import boto3
from moto import mock_ssm

from app.main.aws.open_search import (
    generate_open_search_client_from_aws_params,
    get_open_search_index_from_aws_params,
)


@mock_ssm
def test_get_open_search_index_from_aws_params():
    ssm_client = boto3.client("ssm")
    ssm_client.put_parameter(
        Name="ENVIRONMENT_NAME",
        Value="test_env",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/AWS_OPEN_SEARCH_INDEX",
        Value="test_index",
        Type="String",
        Overwrite=True,
    )

    assert get_open_search_index_from_aws_params() == "test_index"


@mock_ssm
@patch("app.main.aws.open_search.OpenSearch")
def test_generate_open_search_client_from_aws_params(mock_open_search):
    ssm_client = boto3.client("ssm")
    ssm_client.put_parameter(
        Name="ENVIRONMENT_NAME",
        Value="test_env",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/AWS_OPEN_SEARCH_HOST",
        Value="mock_opensearch_host",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/AWS_OPEN_SEARCH_USERNAME",
        Value="mock_username",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/AWS_OPEN_SEARCH_PASSWORD",
        Value="mock_password",
        Type="String",
        Overwrite=True,
    )

    assert (
        generate_open_search_client_from_aws_params()
        == mock_open_search.return_value
    )

    mock_open_search.assert_called_once_with(
        hosts=[{"host": "mock_opensearch_host", "port": 443}],
        http_auth=("mock_username", "mock_password"),
        use_ssl=True,
        verify_certs=True,
        http_compress=True,
        ssl_assert_hostname=False,
        ssl_show_warn=True,
    )
