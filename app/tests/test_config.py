from unittest.mock import patch

import boto3
from moto import mock_ssm

from configs.aws_parameter_store_config import AWSParameterStoreConfig
from configs.env_config import EnvConfig


def test_local_env_vars_config_initialized(monkeypatch):
    """
    GIVEN environment variables are set without DEFAULT_AWS_PROFILE
    WHEN Config is initialized
    THEN it should have attributes with the expected environment variables
    """
    monkeypatch.setenv(
        "SQLALCHEMY_DATABASE_URI", "test_sqlalchemy_database_uri"
    )
    monkeypatch.setenv("DB_PORT", "5432")
    monkeypatch.setenv("DB_HOST", "test_db_host")
    monkeypatch.setenv("DB_USER", "test_db_user")
    monkeypatch.setenv("DB_PASSWORD", "test_db_password")
    monkeypatch.setenv("DB_NAME", "test_db_name")
    monkeypatch.setenv("KEYCLOAK_BASE_URI", "test_keycloak_base_uri")
    monkeypatch.setenv("KEYCLOAK_CLIENT_ID", "test_keycloak_client_id")
    monkeypatch.setenv("KEYCLOAK_REALM_NAME", "test_keycloak_realm_name")
    monkeypatch.setenv(
        "KEYCLOAK_CLIENT_SECRET", "test_keycloak_client_secret"
    )  # pragma: allowlist secret
    monkeypatch.setenv(
        "SECRET_KEY", "test_secret_key"  # pragma: allowlist secret
    )
    monkeypatch.setenv("DEFAULT_PAGE_SIZE", "test_default_page_size")
    monkeypatch.setenv("DEFAULT_DATE_FORMAT", "test_default_date_format")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "test_ratelimit_storage_uri")

    config = EnvConfig()

    assert (
        config.SQLALCHEMY_DATABASE_URI == "postgresql+psycopg2://test_db_user:"
        "test_db_password@test_db_host:5432/test_db_name?sslmode=require"
    )
    assert config.KEYCLOAK_BASE_URI == "test_keycloak_base_uri"
    assert config.KEYCLOAK_CLIENT_ID == "test_keycloak_client_id"
    assert config.KEYCLOAK_REALM_NAME == "test_keycloak_realm_name"
    assert (
        config.KEYCLOAK_CLIENT_SECRET
        == "test_keycloak_client_secret"  # pragma: allowlist secret
    )
    assert config.SECRET_KEY == "test_secret_key"  # pragma: allowlist secret
    assert config.DEFAULT_PAGE_SIZE == "test_default_page_size"
    assert config.DEFAULT_DATE_FORMAT == "test_default_date_format"
    assert config.RATELIMIT_STORAGE_URI == "test_ratelimit_storage_uri"


@patch("configs.aws_parameter_store_config.boto3")
@mock_ssm
def test_aws_params_config_initialized(mock_boto3, monkeypatch):
    """
    GIVEN DEFAULT_AWS_PROFILE env var is set and AWS SSM parameters are set
    WHEN Config is initialized
    THEN it should have attributes with the expected values from the AWS SSM
    """
    # Mock RDS client and generate_db_auth_token method
    mock_boto3.client.return_value.generate_db_auth_token.return_value = (
        "mocked_unescaped_%F4_/rds@_:token"
    )
    monkeypatch.setenv("DEFAULT_AWS_PROFILE", "test_default_aws_profile")

    ssm_client = boto3.client("ssm")

    ssm_client.put_parameter(
        Name="ENVIRONMENT_NAME",
        Value="test_env",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/AWS_REGION",
        Value="test_aws_region",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/DB_PORT",
        Value="5432",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/DB_HOST",
        Value="test_db_host",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/DB_USER",
        Value="test_db_user",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/DB_NAME",
        Value="test_db_name",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/KEYCLOAK_BASE_URI",
        Value="test_keycloak_base_uri",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/KEYCLOAK_CLIENT_ID",
        Value="test_keycloak_client_id",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/KEYCLOAK_REALM_NAME",
        Value="test_keycloak_realm_name",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/KEYCLOAK_CLIENT_SECRET",
        Value="test_keycloak_client_secret",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/SECRET_KEY",
        Value="test_secret_key",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/DEFAULT_PAGE_SIZE",
        Value="test_default_page_size",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/DEFAULT_DATE_FORMAT",
        Value="test_default_date_format",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/RATELIMIT_STORAGE_URI",
        Value="test_ratelimit_storage_uri",
        Type="String",
        Overwrite=True,
    )

    config = AWSParameterStoreConfig()

    assert (
        config.SQLALCHEMY_DATABASE_URI == "postgresql+psycopg2://test_db_user:"
        "mocked_unescaped_%25F4_%2Frds%40_%3Atoken@test_db_host:5432/"
        "test_db_name?sslmode=require"
    )
    assert config.KEYCLOAK_BASE_URI == "test_keycloak_base_uri"
    assert config.KEYCLOAK_CLIENT_ID == "test_keycloak_client_id"
    assert config.KEYCLOAK_REALM_NAME == "test_keycloak_realm_name"
    assert (
        config.KEYCLOAK_CLIENT_SECRET
        == "test_keycloak_client_secret"  # pragma: allowlist secret
    )
    assert config.SECRET_KEY == "test_secret_key"  # pragma: allowlist secret
    assert config.DEFAULT_PAGE_SIZE == "test_default_page_size"
    assert config.DEFAULT_DATE_FORMAT == "test_default_date_format"
    assert config.RATELIMIT_STORAGE_URI == "test_ratelimit_storage_uri"
