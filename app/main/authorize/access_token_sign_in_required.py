from functools import wraps

import keycloak
from flask import current_app, flash, g, redirect, session, url_for

from app.main.authorize.ayr_user import AYRUser
from app.main.authorize.keycloak_manager import decode_verified_token_claims
from app.main.flask_config_helpers import (
    get_keycloak_instance_from_flask_config,
)


def access_token_sign_in_required(view_func):
    """
    Decorator that checks if the user is logged in via Keycloak and has access to AYR.

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
        tokens_are_refreshed = False

        access_token = session.get("access_token")
        refresh_token = session.get("refresh_token")
        try:
            (
                access_token,
                refresh_token,
                tokens_are_refreshed,
            ) = _validate_or_refresh_tokens(access_token, refresh_token)
        except InvalidAccessToken:
            session.clear()
            return redirect(url_for("main.sign_in"))

        if tokens_are_refreshed:
            session["access_token"] = access_token
            session["refresh_token"] = refresh_token
            keycloak_openid = get_keycloak_instance_from_flask_config()
            decoded_access_token = keycloak_openid.introspect(
                session["access_token"]
            )
            user_groups = _resolve_user_groups_with_fallbacks(
                keycloak_openid=keycloak_openid,
                access_token=session["access_token"],
                decoded_access_token=decoded_access_token,
            )
            if user_groups:
                session["user_groups"] = user_groups
            elif "user_groups" in session:
                current_app.app_logger.warning(
                    "User groups refresh failed during token refresh; "
                    "keeping previously cached user_groups for this session"
                )
            else:
                session["user_groups"] = user_groups
                current_app.app_logger.warning(
                    "User groups refresh failed during token refresh; "
                    "no cached user_groups exist for this session"
                )
            _set_user_type(session.get("user_groups"))

        ayr_user = AYRUser(session["user_groups"])

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


def _resolve_user_groups_with_fallbacks(
    keycloak_openid, access_token, decoded_access_token
):
    user_groups = decoded_access_token.get("groups")
    if user_groups is None:
        current_app.app_logger.warning(
            "Groups missing from introspection response during refresh; trying userinfo fallback"
        )
        try:
            userinfo_claims = keycloak_openid.userinfo(access_token)
            user_groups = userinfo_claims.get("groups", [])
        except Exception as exception:
            current_app.app_logger.warning(
                f"Failed to fetch userinfo claims during refresh: {exception}"
            )
            user_groups = []

    if not user_groups:
        current_app.app_logger.warning(
            "Groups unavailable from introspection/userinfo during refresh; trying access token claim fallback"
        )
        try:
            token_claims = decode_verified_token_claims(
                keycloak_openid=keycloak_openid,
                access_token=access_token,
            )
            user_groups = token_claims.get("groups", user_groups)
        except Exception as exception:
            current_app.app_logger.warning(
                f"Failed to decode access token claims during refresh: {exception}"
            )

    return user_groups


def _set_user_type(user_groups):
    ayr_user = AYRUser(user_groups)
    if ayr_user.is_all_access_user:
        session["user_type"] = "all_access_user"
    else:
        session["user_type"] = "standard_user"
