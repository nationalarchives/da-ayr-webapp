import os
from functools import wraps

import keycloak
from flask import flash, g, redirect, request, session, url_for

from app.main.authorize.ayr_user import AYRUser
from app.main.flask_config_helpers import (
    get_keycloak_instance_from_flask_config,
)


def get_access_token():
    """
    Retrieve the access token based on the environment variable.
    If PERF_TEST is True, get the token from the headers. Otherwise, get it from the session.
    """
    if os.getenv("PERF_TEST", "False") == "True":
        access_token = request.headers.get("Authorization")
        if access_token and access_token.startswith("Bearer "):
            return access_token[len("Bearer ") :], None
    else:
        return session.get("access_token"), session.get("refresh_token")
    return None, None


def clear_session_and_redirect():
    """
    Clear the session and redirect the user to the sign-in page.
    """
    session.clear()
    return redirect(url_for("main.sign_in"))


def handle_tokens(access_token, refresh_token):
    """
    Validate or refresh tokens. Clear session and redirect if validation fails.
    """
    try:
        return _validate_or_refresh_tokens(access_token, refresh_token)
    except InvalidAccessToken:
        return clear_session_and_redirect()


def update_session_tokens(access_token, refresh_token):
    """
    Update session tokens if not in PERF_TEST mode.
    """
    if os.getenv("PERF_TEST", "False") != "True":
        session["access_token"] = access_token
        session["refresh_token"] = refresh_token


def check_user_permissions(decoded_access_token):
    """
    Check if the user belongs to the required AYR group. Redirect if they don't.
    """
    session["user_groups"] = decoded_access_token["groups"]
    ayr_user = AYRUser(session.get("user_groups"))

    session["user_type"] = (
        "all_access_user" if ayr_user.is_all_access_user else "standard_user"
    )

    if not ayr_user.can_access_ayr:
        flash(
            "TNA User is logged in but does not have access to AYR. Please contact your admin."
        )
        return redirect(url_for("main.index"))

    return None


def access_token_sign_in_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        g.access_token_sign_in_required = True

        # Retrieve access and refresh tokens
        access_token, refresh_token = get_access_token()

        if not access_token and not refresh_token:
            return clear_session_and_redirect()

        # Validate or refresh tokens
        tokens_are_refreshed = handle_tokens(access_token, refresh_token)

        # Update session tokens if necessary
        if tokens_are_refreshed:
            update_session_tokens(access_token, refresh_token)

        # Decode the access token and check user permissions
        keycloak_openid = get_keycloak_instance_from_flask_config()
        decoded_access_token = keycloak_openid.introspect(access_token)

        permission_check = check_user_permissions(decoded_access_token)
        if permission_check:
            return permission_check

        return view_func(*args, **kwargs)

    decorated_view.access_token_sign_in_required = True

    return decorated_view


def _validate_or_refresh_tokens(access_token, refresh_token):
    tokens_are_refreshed = False

    # PERFORMANCE TEST MODE
    if os.getenv("PERF_TEST", "False") == "True":
        if not (access_token):
            raise InvalidAccessToken
    else:  # NORMAL MODE
        if not (access_token and refresh_token):
            raise InvalidAccessToken

    keycloak_openid = get_keycloak_instance_from_flask_config()

    decoded_token = keycloak_openid.introspect(access_token)

    if decoded_token["active"] is False:
        try:
            refreshed_token_response = keycloak_openid.refresh_token(
                refresh_token
            )
        except keycloak.exceptions.KeycloakPostError:
            raise InvalidAccessToken

        access_token = refreshed_token_response["access_token"]
        refresh_token = refreshed_token_response["refresh_token"]
        tokens_are_refreshed = True

    return access_token, refresh_token, tokens_are_refreshed


class InvalidAccessToken(Exception):
    pass
