from functools import wraps

from flask import current_app, flash, g, redirect, session, url_for

from app.main.authorize.ayr_user import AYRUser


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

        try:
            token = session.get("token")
            try:
                (
                    token,
                    token_is_refreshed,
                ) = _validate_or_refresh_token(token)
            except InvalidAccessToken:
                session.clear()
                return redirect(url_for("main.sign_in"))

            if token_is_refreshed:
                session["token"] = token
                ayr_user = AYRUser(session["token"]["userinfo"]["groups"])
                if ayr_user.is_superuser:
                    session["user_type"] = "superuser"
                else:
                    session["user_type"] = "standard_user"

            ayr_user = AYRUser(session["token"]["userinfo"]["groups"])

            if not ayr_user.can_access_ayr:
                flash(
                    "TNA User is logged in but does not have access to AYR. Please contact your admin."
                )  # FIXME: this flash doesn't currently show when first redirected, only on a new page load
                return redirect(url_for("main.index"))

            return view_func(*args, **kwargs)
        finally:
            g.access_token_sign_in_required = (
                False  # Clear attribute after view execution
            )

    decorated_view.access_token_sign_in_required = True

    return decorated_view


def _validate_or_refresh_token(token):
    token_is_refreshed = False

    if not (token["access_token"] and token["refresh_token"]):
        raise InvalidAccessToken
    token_endpoint = f'{current_app.config["KEYCLOAK_BASE_URI"]}realms/{current_app.config["KEYCLOAK_REALM_NAME"]}/protocol/openid-connect/token/introspect'
    introspected_token = (
        current_app.extensions["authlib.integrations.flask_client"]
        .keycloak._get_oauth_client()
        .introspect_token(token_endpoint, token=token["access_token"])
    )
    if introspected_token.ok and introspected_token.json()["active"] is False:
        token_endpoint = f'{current_app.config["KEYCLOAK_BASE_URI"]}realms/{current_app.config["KEYCLOAK_REALM_NAME"]}/protocol/openid-connect/token/refresh'
        refreshed_token_response = (
            current_app.extensions["authlib.integrations.flask_client"]
            .keycloak._get_oauth_client()
            .refresh_token(token_endpoint, token=token)
        )
        if refreshed_token_response.ok():
            token = refreshed_token_response.json()
            token_is_refreshed = True

    return token, token_is_refreshed


class InvalidAccessToken(Exception):
    pass
