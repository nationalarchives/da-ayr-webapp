from functools import wraps

from flask import current_app, flash, redirect, session, url_for

from app.main import keycloak_openid
from app.main.aws.parameter import (
    get_aws_environment_prefix,
    get_parameter_store_key_value,
)


def access_token_login_required():
    def decorator(view_func):
        @wraps(view_func)
        def decorated_view(*args, **kwargs):
            if current_app.config["TESTING"]:
                return view_func(*args, **kwargs)

            access_token = session.get("access_token")
            if not access_token:
                return redirect(url_for("main.login"))

            decoded_token = keycloak_openid.introspect(access_token)
            if not decoded_token["active"]:
                session.pop("access_token", None)
                return redirect(url_for("main.login"))

            groups = decoded_token["groups"]
            keycloak_ayr_user_group = get_parameter_store_key_value(
                get_aws_environment_prefix() + "KEYCLOAK_AYR_USER_GROUP"
            )
            group_exists = group_exists_in_groups(
                keycloak_ayr_user_group, groups
            )

            if not group_exists:
                flash(
                    "TNA User is logged in but does not have access to AYR. Please contact your admin."
                )
                return redirect(url_for("main.index"))

            flash("TNA User is logged in and has access to AYR.")
            return view_func(*args, **kwargs)

        return decorated_view

    return decorator


def group_exists_in_groups(keycloak_ayr_user_group, groups):
    group_exists = False
    for group in groups:
        if keycloak_ayr_user_group in group:
            group_exists = True
    return group_exists
