import json

import boto3
from moto import mock_aws

from configs.aws_secrets_manager_config import AWSSecretsManagerConfig
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
    monkeypatch.setenv("RECORD_BUCKET_NAME", "test_record_bucket_name")
    monkeypatch.setenv("FLASKS3_ACTIVE", "False")
    monkeypatch.setenv("FLASKS3_CDN_DOMAIN", "test_flasks3_cdn_domain")
    monkeypatch.setenv("FLASKS3_BUCKET_NAME", "test_flasks3_bucket_name")

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
    assert config.RECORD_BUCKET_NAME == "test_record_bucket_name"
    assert config.FLASKS3_ACTIVE is False
    assert config.FLASKS3_CDN_DOMAIN == "test_flasks3_cdn_domain"
    assert config.FLASKS3_BUCKET_NAME == "test_flasks3_bucket_name"


@mock_aws
def test_aws_secrets_manager_config_initialized(monkeypatch):
    """
    GIVEN AWS secret with secret_id `AWS_SM_CONFIG_SECRET_ID` is set with all config key value pairs
    WHEN Config is initialized
    THEN it should have attributes with the expected values from the AWS Secrets Manager secret
    """
    secret_value = json.dumps(
        {
            "AWS_REGION": "test_aws_region",
            "KEYCLOAK_BASE_URI": "test_keycloak_base_uri",
            "KEYCLOAK_CLIENT_ID": "test_keycloak_client_id",
            "KEYCLOAK_REALM_NAME": "test_keycloack_realm_name",
            "KEYCLOAK_CLIENT_SECRET": "test_keycloak_client_secret",  # pragma: allowlist secret
            "RECORD_BUCKET_NAME": "test_record_bucket_name",
            "FLASKS3_ACTIVE": "False",
            "FLASKS3_CDN_DOMAIN": "test_flasks3_cdn_domain",
            "FLASKS3_BUCKET_NAME": "test_flasks3_bucket_name",
            "RATELIMIT_STORAGE_URI": "test_ratelimit_storage_uri",
            "DEFAULT_DATE_FORMAT": "test_default_date_format",
            "SECRET_KEY": "test_secret_key",  # pragma: allowlist secret
            "DB_PORT": "5432",
            "DB_HOST": "test_db_host",
            "DB_USER": "test_db_user",
            "DB_PASSWORD": "test_db_password",  # pragma: allowlist secret
            "DB_NAME": "test_db_name",
            "DEFAULT_PAGE_SIZE": "test_default_page_size",
        }
    )

    ssm_client = boto3.client("secretsmanager")

    ssm_client.create_secret(
        Name="test_secret_id",
        SecretString=secret_value,
    )

    monkeypatch.setenv(
        "AWS_SM_CONFIG_SECRET_ID", "test_secret_id"
    )  # pragma: allowlist secret

    config = AWSSecretsManagerConfig()

    assert (
        config.SQLALCHEMY_DATABASE_URI
        == "postgresql+psycopg2://test_db_user:test_db_password"
        "@test_db_host:5432/"
        "test_db_name?sslmode=require"
    )

    assert config.KEYCLOAK_BASE_URI == "test_keycloak_base_uri"
    assert config.KEYCLOAK_CLIENT_ID == "test_keycloak_client_id"
    assert config.KEYCLOAK_REALM_NAME == "test_keycloack_realm_name"
    assert (
        config.KEYCLOAK_CLIENT_SECRET
        == "test_keycloak_client_secret"  # pragma: allowlist secret
    )
    assert config.SECRET_KEY == "test_secret_key"  # pragma: allowlist secret
    assert config.DEFAULT_PAGE_SIZE == "test_default_page_size"
    assert config.DEFAULT_DATE_FORMAT == "test_default_date_format"

    assert config.RECORD_BUCKET_NAME == "test_record_bucket_name"
    assert config.FLASKS3_ACTIVE is False
    assert config.FLASKS3_CDN_DOMAIN == "test_flasks3_cdn_domain"
    assert config.FLASKS3_BUCKET_NAME == "test_flasks3_bucket_name"
