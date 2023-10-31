import boto3
from moto import mock_ssm

from app.main.authorize.keycloak_manager import (
    get_keycloak_openid_object_from_aws_params,
)


@mock_ssm
def test_get_keycloak_openid_object():
    """
    GIVEN AWS SSM parameters are set with Keycloak configuration
    WHEN get_keycloak_openid_object_from_aws_params is called
    THEN it should return a KeycloakOpenID object with the expected configuration
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

    keycloak_openid = get_keycloak_openid_object_from_aws_params()
    assert keycloak_openid.connection.base_url == "a"
    assert keycloak_openid.client_id == "b"
    assert keycloak_openid.realm_name == "c"
    assert keycloak_openid.client_secret_key == "d"
