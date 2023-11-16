from unittest.mock import patch

from flask import url_for

from app.main.authorize.keycloak_login_required_decorator import (
    access_token_login_required,
)
from app.main.routes import logout, poc_search, record


def test_access_token_login_required_decorator_no_token(app):
    """
    Given no access token in the session,
    When accessing a route protected by the 'access_token_login_required' decorator,
    Then it should redirect to the login page.
    """
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    view_name = "/protected_view"
    with app.test_client() as client:

        @app.route(view_name)
        @access_token_login_required
        def protected_view():
            return "Access granted"

        with client.session_transaction() as session:
            session["access_token"] = None
        response = client.get(view_name)
        assert response.status_code == 302
        assert response.headers["Location"] == url_for("main.login")


@patch(
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
)
def test_access_token_login_required_decorator_inactive_token(
    mock_decode_keycloak_access_token, app
):
    """
    Given an inactive access token in the session,
    When accessing a route protected by the 'access_token_login_required' decorator,
    Then it should redirect to the login page.
    And the session should be cleared
    """
    mock_decode_keycloak_access_token.return_value = {"active": False}

    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    view_name = "/protected_view"
    with app.test_client() as client:

        @app.route(view_name)
        @access_token_login_required
        def protected_view():
            return "Access granted"

        with client.session_transaction() as session:
            session["access_token"] = "some_token"
            session["foo"] = "bar"
        response = client.get(view_name)

        assert response.status_code == 302
        assert response.headers["Location"] == url_for("main.login")

        with client.session_transaction() as cleared_session:
            assert cleared_session == {}


@patch(
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
)
def test_access_token_login_required_decorator_active_without_ayr_access(
    mock_decode_keycloak_access_token,
    app,
):
    """
    Given an active access token in the session,
    And the user does not have access to AYR,
    When accessing a route protected by the 'access_token_login_required' decorator,
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
        @access_token_login_required
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
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
)
def test_access_token_login_required_decorator_valid_token(
    mock_decode_keycloak_access_token,
    app,
):
    """
    Given an active access token in the session,
    And the user has access to AYR,
    When accessing a route protected by the 'access_token_login_required' decorator,
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
        @access_token_login_required
        def protected_view():
            return "Access granted"

        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        response = client.get(view_name)

    assert response.status_code == 200
    assert response.data.decode() == "Access granted"


def test_expected_protected_routes_decorated_by_access_token_login_required():
    """
    Given a list of views we expect to be protected by the access_token_login_required decorator
    When introspecting the view function
    Then it should have the `access_token_login_required` property set to True
    """
    expected_protected_views = [poc_search, record, logout]
    assert all(
        getattr(expected_protected_view, "access_token_login_required") is True
        for expected_protected_view in expected_protected_views
    )
