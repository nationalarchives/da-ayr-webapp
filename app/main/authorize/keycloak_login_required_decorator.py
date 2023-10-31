from functools import wraps

from flask import flash, redirect, session, url_for

from app.main.authorize.keycloak_manager import get_keycloak_openid_object
from app.main.aws.parameter import (
    get_aws_environment_prefix,
    get_parameter_store_key_value,
)


def access_token_login_required():
    def decorator(view_func):
        @wraps(view_func)
        def decorated_view(*args, **kwargs):
            access_token = session.get("access_token")
            if not (access_token and is_valid_token_for_ayr(access_token)):
                return redirect(url_for("main.index"))
            return view_func(*args, **kwargs)

        return decorated_view

    return decorator


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
        flash(
            "TNA User is logged in but is not active. Please contact your admin."
        )
        return False

    groups = decoded_token["groups"]

    for group in groups:
        if keycloak_ayr_user_group in group:
            flash("TNA User is logged in and has access to AYR.")
            return True

    flash(
        "TNA User is logged in but does not have access to AYR. Please contact your admin."
    )
    return False
