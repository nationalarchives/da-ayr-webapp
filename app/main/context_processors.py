from flask import g

from app.main import bp


@bp.context_processor
def inject_authenticated_view_status():
    """
    This context processor is designed to be used with Flask Blueprints to provide
    information about the authentication status of the current view to the templates.
    It specifically checks if the `access_token_login_required` attribute is set on
    the Flask `g` object, indicating whether the current view requires authentication.

    The `access_token_login_required` attribute is typically set by the
    `access_token_login_required` decorator applied to specific routes. This decorator
    is responsible for enforcing access token login requirements and protecting routes
    that require authentication.

    The primary purpose of this context processor is to make the `authenticated_view`
    variable available in templates, allowing template logic to conditionally display
    elements based on whether the current view requires authentication or not.

    Example Usage in a Template:
    ```html
    {% if authenticated_view %}
        <!-- Display elements for authenticated views -->
        <div class="user-menu">
            Welcome, {{ current_user.username }}!
        </div>
    {% else %}
        <!-- Display elements for views that do not require authentication -->
        <div class="login-prompt">
            Please log in to access this page.
        </div>
    {% endif %}
    ```

    Note: Ensure that the `access_token_login_required` decorator is appropriately
    applied to routes where authentication is required for accurate behavior of
    this context processor.

    Args:
        None

    Returns:
        dict: A dictionary containing the `authenticated_view` variable, which is a
              boolean indicating whether the current view requires authentication.

    See Also:
        - app.main.access_token_login_required: The decorator responsible for
          enforcing access token login requirements on specific routes.
        - Flask Blueprint Documentation: https://flask.palletsprojects.com/en/2.0.x/blueprints/
    """
    authenticated_view = getattr(g, "access_token_login_required", False)
    return dict(authenticated_view=authenticated_view)
