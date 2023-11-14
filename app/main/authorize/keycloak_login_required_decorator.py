from functools import wraps

import keycloak
from flask import current_app, flash, redirect, session, url_for


def access_token_login_required(view_func):
    """
    Decorator that checks if the user is logged in via Keycloak and has access to AYR.

    This decorator is typically applied to view functions that require authentication via Keycloak
    and access to the AYR application. It checks for the presence of an access token in the session,
    verifies the token's validity, and checks if the user belongs to the AYR user group in Keycloak.

    Args:
        view_func (function): The view function to be wrapped.

    Returns:
        function: The wrapped view function.

    If the user is not authenticated or does not have access, this decorator redirects to the login page
    or the main index and displays a flash message accordingly.

    Configuration options for Keycloak, such as the client ID, realm name, base URI, and client secret,
    are expected to be set in the Flask application configuration.

    When the application is running in testing mode and the 'FORCE_AUTHENTICATION_FOR_IN_TESTING' config
    option is not set, the decorator allows unauthenticated access to facilitate testing.

    Example:
        @app.route('/protected')
        @access_token_login_required
        def protected_route():
            return 'Access granted'
    """

    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if current_app.config["TESTING"] and not current_app.config.get(
            "FORCE_AUTHENTICATION_FOR_IN_TESTING"
        ):
            return view_func(*args, **kwargs)

        access_token = session.get("access_token")
        if not access_token:
            return redirect(url_for("main.login"))

        keycloak_openid = keycloak.KeycloakOpenID(
            server_url=current_app.config["KEYCLOAK_BASE_URI"],
            client_id=current_app.config["KEYCLOAK_CLIENT_ID"],
            realm_name=current_app.config["KEYCLOAK_REALM_NAME"],
            client_secret_key=current_app.config["KEYCLOAK_CLIENT_SECRET"],
        )

        decoded_token = keycloak_openid.introspect(access_token)

        if not decoded_token["active"]:
            session.clear()
            return redirect(url_for("main.login"))

        keycloak_ayr_user_group = current_app.config["KEYCLOAK_AYR_USER_GROUP"]
        if not _check_if_user_has_access_to_ayr(
            keycloak_ayr_user_group, decoded_token
        ):
            flash(
                "TNA User is logged in but does not have access to AYR. Please contact your admin."
            )
            return redirect(url_for("main.index"))

        return view_func(*args, **kwargs)
    
    decorated_view.access_token_login_required = True
    
    return decorated_view


def _check_if_user_has_access_to_ayr(keycloak_ayr_user_group, decoded_token):
    groups = decoded_token["groups"]
    group_exists = False
    for group in groups:
        if keycloak_ayr_user_group in group:
            group_exists = True
    return group_exists
