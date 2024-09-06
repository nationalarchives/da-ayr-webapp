import os
from functools import wraps

import keycloak
from flask import flash, g, redirect, request, session, url_for

from app.main.authorize.ayr_user import AYRUser
from app.main.flask_config_helpers import (
    get_keycloak_instance_from_flask_config,
)


def access_token_sign_in_required(view_func):
    """
    Decorator that checks if the user is logged in via Keycloak and has access to AYR.

    If the PERF_TEST environment variable is True, the decorator checks for the access token
    in the request header. Otherwise, it checks the session for the token.

    This decorator is typically applied to view functions that require authentication via Keycloak
    and access to the AYR application. It checks for the presence of an access token in the session,
    verifies the token's validity, and checks if the user belongs to the AYR user group in Keycloak.

    Args:
        view_func (function): The view function to be wrapped.

    Returns:
        function: The wrapped view function.

    If the user is not authenticated or does not have access, this decorator redirects to the sign in page
    or the main index and displays a flash message accordingly.

    Configuration options for Keycloak, such as the client ID, realm name, base URI, and client secret,
    are expected to be set in the Flask application configuration.

    Example:
        @app.route('/protected')
        @access_token_sign_in_required
        def protected_route():
            return 'Access granted'
    """

    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        g.access_token_sign_in_required = True  # Set attribute on g

        # Determine whether to get the token from the header or session
        if os.getenv("PERF_TEST", "False") == "True":
            # In performance testing mode, get the token from the header
            access_token = request.headers.get("Authorization")
            if access_token and access_token.startswith("Bearer "):
                access_token = access_token[len("Bearer ") :]
                refresh_token = None
            else:
                access_token = None
                refresh_token = None
        else:
            # In normal mode, get the token from the session
            access_token = session.get("access_token")
            refresh_token = session.get("refresh_token")

        # If no access token or refresh token, clear session and redirect to sign in
        if not access_token and not refresh_token:
            session.clear()
            return redirect(url_for("main.sign_in"))

        try:
            # Validate or refresh tokens based on the retrieved access token
            access_token, refresh_token, tokens_are_refreshed = (
                _validate_or_refresh_tokens(access_token, refresh_token)
            )
        except InvalidAccessToken:
            session.clear()  # Clear session if token is invalid
            return redirect(url_for("main.sign_in"))

        if tokens_are_refreshed:
            # If tokens are refreshed, update session tokens (only in non-PERF_TEST mode)
            if os.getenv("PERF_TEST", "False") != "True":
                session["access_token"] = access_token
                session["refresh_token"] = refresh_token

        # Decode access token and check user permissions
        keycloak_openid = get_keycloak_instance_from_flask_config()
        decoded_access_token = keycloak_openid.introspect(access_token)
        session["user_groups"] = decoded_access_token["groups"]

        ayr_user = AYRUser(session.get("user_groups"))
        if ayr_user.is_all_access_user:
            session["user_type"] = "all_access_user"
        else:
            session["user_type"] = "standard_user"

        # If the user doesn't have access, flash a message and redirect to index

        if not ayr_user.can_access_ayr:
            flash(
                "TNA User is logged in but does not have access to AYR. Please contact your admin."
            )  # FIXME: this flash doesn't currently show when first redirected, only on a new page load
            return redirect(url_for("main.index"))

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
