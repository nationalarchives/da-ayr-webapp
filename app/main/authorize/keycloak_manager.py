import logging

import keycloak
from flask import flash

from app.main.aws.parameter import (
    get_aws_environment_prefix,
    get_parameter_store_key_value,
)


def get_keycloak_openid_object():
    """
    Get Keycloak object based on configuration values.
    :return: Keycloak object.
    """
    try:
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
    except Exception as e:
        logging.error(
            "Error generating keycloak openid object with error : " + str(e)
        )


def is_valid_token_for_ayr(access_token):
    """
    validate user group.
    :param token: user access token received from keycloak.
    :return: validate user group received in access token from keycloak.
    """
    keycloak_ayr_user_group = get_parameter_store_key_value(
        get_aws_environment_prefix() + "KEYCLOAK_AYR_USER_GROUP"
    )
    keycloak_openid = get_keycloak_openid_object()

    decoded_token = keycloak_openid.introspect(access_token)
    if not decoded_token["active"]:
        flash("TNA User is not active.")
        return False

    groups = decoded_token["groups"]

    for group in groups:
        if keycloak_ayr_user_group in group:
            flash("TNA User has access to AYR.")
            return True

    flash("TNA User does not have access to AYR. Please contact your admin.")
    return False
