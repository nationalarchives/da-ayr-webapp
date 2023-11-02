from functools import wraps

import keycloak
from flask import current_app, flash, redirect, session, url_for


def access_token_login_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if current_app.config["TESTING"] and not current_app.config.get(
            "FORCE_AUTHENTICATION_FOR_IN_TESTING"
        ):
            return view_func(*args, **kwargs)

        access_token = session.get("access_token")
        if not access_token:
            return redirect(url_for("main.login"))

        keycloak_openid = keycloak_openid = keycloak.KeycloakOpenID(
            server_url=current_app.config["KEYCLOAK_BASE_URI"],
            client_id=current_app.config["KEYCLOAK_CLIENT_ID"],
            realm_name=current_app.config["KEYCLOAK_REALM_NAME"],
            client_secret_key=current_app.config["KEYCLOAK_CLIENT_SECRET"],
        )

        decoded_token = keycloak_openid.introspect(access_token)

        if not decoded_token["active"]:
            session.pop("access_token", None)
            return redirect(url_for("main.login"))

        keycloak_ayr_user_group = current_app.config["KEYCLOAK_AYR_USER_GROUP"]
        if not _check_if_user_has_access_to_ayr(
            keycloak_ayr_user_group, decoded_token
        ):
            flash(
                "TNA User is logged in but does not have access to AYR. Please contact your admin."
            )
            return redirect(url_for("main.index"))

        flash("TNA User is logged in and has access to AYR.")
        return view_func(*args, **kwargs)

    return decorated_view


def _check_if_user_has_access_to_ayr(keycloak_ayr_user_group, decoded_token):
    groups = decoded_token["groups"]
    group_exists = False
    for group in groups:
        if keycloak_ayr_user_group in group:
            group_exists = True
    return group_exists
