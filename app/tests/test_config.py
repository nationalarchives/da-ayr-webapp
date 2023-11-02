import boto3
from moto import mock_ssm

from config import Config


@mock_ssm
def test_aws_params_config_initialized():
    """
    GIVEN AWS SSM parameters are set
    WHEN Config is initialized
    THEN it should have attributes with the expected values from the AWS SSM
    """
    ssm_client = boto3.client("ssm")
    ssm_client.put_parameter(
        Name="ENVIRONMENT_NAME",
        Value="test_env",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/KEYCLOAK_BASE_URI",
        Value="a",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/KEYCLOAK_CLIENT_ID",
        Value="b",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/KEYCLOAK_REALM_NAME",
        Value="c",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/KEYCLOAK_CLIENT_SECRET",
        Value="d",
        Type="String",
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name="/test_env/KEYCLOAK_AYR_USER_GROUP",
        Value="e",
        Type="String",
        Overwrite=True,
    )

    config = Config()

    assert config.AWS_ENVIRONMENT_PREFIX == "/test_env/"

    assert config.KEYCLOAK_BASE_URI == "a"
    assert config.KEYCLOAK_CLIENT_ID == "b"
    assert config.KEYCLOAK_REALM_NAME == "c"
    assert config.KEYCLOAK_CLIENT_SECRET == "d"
    assert config.KEYCLOAK_AYR_USER_GROUP == "e"
