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
    monkeypatch.setenv("KEYCLOAK_BASE_URI", "test_keycloak_base_uri")
    monkeypatch.setenv("KEYCLOAK_CLIENT_ID", "test_keycloak_client_id")
    monkeypatch.setenv("KEYCLOAK_REALM_NAME", "test_keycloak_realm_name")
    monkeypatch.setenv(
        "KEYCLOAK_CLIENT_SECRET", "test_keycloak_client_secret"
    )  # pragma: allowlist secret
    monkeypatch.setenv(
        "KEYCLOAK_AYR_USER_GROUP", "test_keycloak_ayr_user_group"
    )
    monkeypatch.setenv(
        "SECRET_KEY", "test_secret_key"  # pragma: allowlist secret
    )
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "test_ratelimit_storage_uri")

    config = EnvConfig()

    assert config.SQLALCHEMY_DATABASE_URI == "test_sqlalchemy_database_uri"
    assert config.KEYCLOAK_BASE_URI == "test_keycloak_base_uri"
    assert config.KEYCLOAK_CLIENT_ID == "test_keycloak_client_id"
    assert config.KEYCLOAK_REALM_NAME == "test_keycloak_realm_name"
    assert (
        config.KEYCLOAK_CLIENT_SECRET
        == "test_keycloak_client_secret"  # pragma: allowlist secret
    )
    assert config.KEYCLOAK_AYR_USER_GROUP == "test_keycloak_ayr_user_group"
    assert config.SECRET_KEY == "test_secret_key"  # pragma: allowlist secret
    assert config.RATELIMIT_STORAGE_URI == "test_ratelimit_storage_uri"


@mock_ssm
def test_aws_params_config_initialized(monkeypatch):
    """
    GIVEN DEFAULT_AWS_PROFILE env var is set and AWS SSM parameters are set
    WHEN Config is initialized
    THEN it should have attributes with the expected values from the AWS SSM
    """
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
        Name="/test_env/SQLALCHEMY_DATABASE_URI",
        Value="test_sqlalchemy_database_uri",
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
        Name="/test_env/KEYCLOAK_AYR_USER_GROUP",
        Value="test_keycloak_ayr_user_group",
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
        Name="/test_env/RATELIMIT_STORAGE_URI",
        Value="test_ratelimit_storage_uri",
        Type="String",
        Overwrite=True,
    )

    config = AWSParameterStoreConfig()

    assert config.SQLALCHEMY_DATABASE_URI == "test_sqlalchemy_database_uri"
    assert config.KEYCLOAK_BASE_URI == "test_keycloak_base_uri"
    assert config.KEYCLOAK_CLIENT_ID == "test_keycloak_client_id"
    assert config.KEYCLOAK_REALM_NAME == "test_keycloak_realm_name"
    assert (
        config.KEYCLOAK_CLIENT_SECRET
        == "test_keycloak_client_secret"  # pragma: allowlist secret
    )
    assert config.KEYCLOAK_AYR_USER_GROUP == "test_keycloak_ayr_user_group"
    assert config.SECRET_KEY == "test_secret_key"  # pragma: allowlist secret
    assert config.RATELIMIT_STORAGE_URI == "test_ratelimit_storage_uri"
