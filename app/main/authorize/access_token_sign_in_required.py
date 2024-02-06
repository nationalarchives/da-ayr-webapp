from functools import wraps

from flask import flash, g, redirect, session, url_for

from app.main.authorize.ayr_user import AYRUser
from app.main.authorize.keycloak_manager import decode_keycloak_token


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
            access_token = session.get("access_token")

            if not access_token:
                session.clear()
                return redirect(url_for("main.sign_in"))

            decoded_token = decode_keycloak_token(access_token)

            if decoded_token["active"] is False:
                session.clear()
                return redirect(url_for("main.sign_in"))

            user_groups = session["user_groups"] = decoded_token["groups"]

            if not user_groups:
                session.clear()
                return redirect(url_for("main.sign_in"))

            ayr_user = AYRUser(user_groups)

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
