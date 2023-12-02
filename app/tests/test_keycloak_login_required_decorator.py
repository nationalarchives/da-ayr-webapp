from unittest.mock import patch

from flask import Flask, render_template, url_for

from app.main.authorize.access_token_sign_in_required import (
    access_token_sign_in_required,
)


def test_access_token_sign_in_required_decorator_no_token(app):
    """
    Given no access token in the session,
    When accessing a route protected by the 'access_token_sign_in_required' decorator,
    Then it should redirect to the sign in view.
    """
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    view_name = "/protected_view"
    with app.test_client() as client:

        @app.route(view_name)
        @access_token_sign_in_required
        def protected_view():
            return "Access granted"

        with client.session_transaction() as session:
            session["access_token"] = None
        response = client.get(view_name)
        assert response.status_code == 302
        assert response.headers["Location"] == url_for("main.sign_in")


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_access_token_sign_in_required_decorator_inactive_token(
    mock_decode_keycloak_access_token, app
):
    """
    Given an inactive access token in the session,
    When accessing a route protected by the 'access_token_sign_in_required' decorator,
    Then it should redirect to the sign in view.
    And the session should be cleared
    """
    mock_decode_keycloak_access_token.return_value = {"active": False}

    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    view_name = "/protected_view"
    with app.test_client() as client:

        @app.route(view_name)
        @access_token_sign_in_required
        def protected_view():
            return "Access granted"

        with client.session_transaction() as session:
            session["access_token"] = "some_token"
            session["foo"] = "bar"
        response = client.get(view_name)

        assert response.status_code == 302
        assert response.headers["Location"] == url_for("main.sign_in")

        with client.session_transaction() as cleared_session:
            assert cleared_session == {}


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_access_token_sign_in_required_decorator_active_without_ayr_access(
    mock_decode_keycloak_access_token,
    app,
):
    """
    Given an active access token in the session,
    And the user does not have access to AYR,
    When accessing a route protected by the 'access_token_sign_in_required' decorator,
    Then it should redirect to the index page with a flashed message.
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["application_1/foo", "application_2/bar"],
    }

    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    app.config["KEYCLOAK_AYR_USER_GROUP"] = "application_3"

    view_name = "/protected_view"
    with app.test_client() as client:

        @app.route(view_name)
        @access_token_sign_in_required
        def protected_view():
            return "Access granted"

        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        response = client.get(view_name)

        with client.session_transaction() as session:
            flashed_messages = session["_flashes"]

        assert flashed_messages == [
            (
                "message",
                "TNA User is logged in but does not have access to AYR. Please contact your admin.",
            )
        ]

        assert response.status_code == 302
        assert response.headers["Location"] == url_for("main.index")


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_access_token_sign_in_required_decorator_valid_token(
    mock_decode_keycloak_access_token,
    app,
):
    """
    Given an active access token in the session,
    And the user has access to AYR,
    When accessing a route protected by the 'access_token_sign_in_required' decorator,
    Then it should grant access
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["application_1/foo", "application_2/bar"],
    }

    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    app.config["KEYCLOAK_AYR_USER_GROUP"] = "application_1"

    view_name = "/protected_view"
    with app.test_client() as client:

        @app.route(view_name)
        @access_token_sign_in_required
        def protected_view():
            return "Access granted"

        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        response = client.get(view_name)

    assert response.status_code == 200
    assert response.data.decode() == "Access granted"


def test_expected_unprotected_routes_decorated_by_access_token_sign_in_required(
    app,
):
    """
    Given a Flask application created by create_app,
    When checking which routes are protected or unprotected by the 'access_token_sign_in_required' decorator,
    Then the protected routes should match the expected protected routes,
    And the unprotected routes should match the expected unprotected routes.
    """
    expected_protected_routes = [
        "main.poc_search",
        "main.record",
        "main.sign_out",
        "main.poc_browse",
        "main.poc_browse_series"
    ]
    expected_unprotected_routes = [
        "static",
        "main.index",
        "main.sign_in",
        "main.callback",
        "main.accessibility",
        "main.dashboard",
        "main.search",
        "main.results",
        "main.start_page",
        "main.signed_out",
        "main.browse",
        "main.quick_access",
        "main.departments",
        "main.cookies",
        "main.privacy",
        "main.how_to_use",
        "main.terms_of_use",
    ]

    (
        protected_routes,
        unprotected_routes,
    ) = get_expected_routes_separated_by_protection(app)

    assert set(protected_routes) == set(expected_protected_routes)
    assert set(unprotected_routes) == set(expected_unprotected_routes)


def get_expected_routes_separated_by_protection(app) -> tuple[list, list]:
    """
    Retrieve the routes of a Flask application separated by 'access_token_sign_in_required' protection.

    Args:
        app (Flask): The Flask application instance.

    Returns:
        tuple[list, list]: A tuple containing two lists.
            - The first list includes the names of routes protected by 'access_token_sign_in_required' decorator.
            - The second list includes the names of routes without the 'access_token_sign_in_required' decorator.
    """
    protected_routes = []
    unprotected_routes = []
    with app.app_context():
        for view_function_name, view_function in app.view_functions.items():
            if (
                getattr(view_function, "access_token_sign_in_required", False)
                is True
            ):
                protected_routes.append(view_function_name)
            else:
                unprotected_routes.append(view_function_name)
    return protected_routes, unprotected_routes


def test_get_expected_routes_separated_by_protection():
    """
    Given a basic Flask application with routes and views,
    When calling the get_expected_routes_separated_by_protection function,
    Then the returned protected routes should match the routes with the 'access_token_sign_in_required' decorator
    And the returned unprotected routes should match the routes without the 'access_token_sign_in_required' decorator
    """
    app = Flask(__name__)

    @app.route("/protected")
    @access_token_sign_in_required
    def protected_view():
        return "Protected View"

    @app.route("/unprotected")
    def unprotected_view():
        return "Unprotected View"

    @app.route("/another_protected")
    @access_token_sign_in_required
    def another_protected_view():
        return "Another Protected View"

    (
        protected_routes,
        unprotected_routes,
    ) = get_expected_routes_separated_by_protection(app)

    assert set(protected_routes) == {"protected_view", "another_protected_view"}
    assert set(unprotected_routes) == {"static", "unprotected_view"}


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_sign_out_button_on_protected_view_that_uses_base_template(
    mock_decode_keycloak_access_token, app
):
    """
    Given a view that is protected by the 'access_token_sign_in_required' decorator,
        and renders the `base.html` template
    When an authenticated user accesses the view,
    Then the response should contain a 'Sign out' button.
    """
    view_name = "/extended_base_view"

    @app.route(view_name)
    @access_token_sign_in_required
    def protected_base_view():
        return render_template(
            "base.html",
        )

    with app.test_client() as client:
        response = client.get(view_name)

    assert response.status_code == 200
    assert "Sign out" in response.data.decode()


def test_no_sign_out_button_on_unprotected_view_that_uses_base_template(app):
    """
    Given a view that is NOT protected by the 'access_token_sign_in_required' decorator,
        and renders the `base.html` template
    When a user accesses the view,
    Then the response should not contain a 'Sign out' button.
    """
    view_name = "/extended_base_view"

    @app.route(view_name)
    def unprotected_base_view():
        return render_template(
            "base.html",
        )

    with app.test_client() as client:
        response = client.get(view_name)

    assert response.status_code == 200
    assert "Sign out" not in response.data.decode()
