from functools import wraps

from flask import flash, redirect, session, url_for

from app.main import keycloak_openid
from app.main.aws.parameter import (
    get_aws_environment_prefix,
    get_parameter_store_key_value,
)


def access_token_login_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        access_token = session.get("access_token")
        if not access_token:
            return redirect(url_for("main.login"))

        decoded_token = decode_keycloak_access_token(access_token)

        if not decoded_token["active"]:
            session.pop("access_token", None)
            return redirect(url_for("main.login"))

        if not check_if_user_has_access_to_ayr(decoded_token):
            flash(
                "TNA User is logged in but does not have access to AYR. Please contact your admin."
            )
            return redirect(url_for("main.index"))

        flash("TNA User is logged in and has access to AYR.")
        return view_func(*args, **kwargs)

    return decorated_view


def check_if_user_has_access_to_ayr(decoded_token):
    groups = decoded_token["groups"]
    keycloak_ayr_user_group = get_parameter_store_key_value(
        get_aws_environment_prefix() + "KEYCLOAK_AYR_USER_GROUP"
    )
    group_exists = group_exists_in_groups(keycloak_ayr_user_group, groups)
    return group_exists


def group_exists_in_groups(keycloak_ayr_user_group, groups):
    group_exists = False
    for group in groups:
        if keycloak_ayr_user_group in group:
            group_exists = True
    return group_exists


def decode_keycloak_access_token(access_token):
    decoded_token = keycloak_openid.introspect(access_token)
    return decoded_token
