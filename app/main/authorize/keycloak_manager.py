import keycloak

from app.main.aws.parameter import (
    get_aws_environment_prefix,
    get_parameter_store_key_value,
)


def get_keycloak_openid_object_from_aws_params():
    """
    Get Keycloak object based on configuration values.
    :return: Keycloak object.
    """
    AWS_ENVIRONMENT_PREFIX = get_aws_environment_prefix()
    KEYCLOAK_BASE_URI = get_parameter_store_key_value(
        AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_BASE_URI"
    )
    KEYCLOAK_CLIENT_ID = get_parameter_store_key_value(
        AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_CLIENT_ID"
    )
    KEYCLOAK_REALM_NAME = get_parameter_store_key_value(
        AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_REALM_NAME"
    )
    KEYCLOAK_CLIENT_SECRET = get_parameter_store_key_value(
        AWS_ENVIRONMENT_PREFIX + "KEYCLOAK_CLIENT_SECRET"
    )

    keycloak_openid = keycloak.KeycloakOpenID(
        server_url=KEYCLOAK_BASE_URI,
        client_id=KEYCLOAK_CLIENT_ID,
        realm_name=KEYCLOAK_REALM_NAME,
        client_secret_key=KEYCLOAK_CLIENT_SECRET,
    )
    return keycloak_openid
