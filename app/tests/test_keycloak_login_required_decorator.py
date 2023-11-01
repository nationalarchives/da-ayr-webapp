from unittest.mock import patch

from flask import url_for

from app.main.authorize.keycloak_login_required_decorator import (
    access_token_login_required,
)


def test_access_token_login_required_decorator_no_token(app):
    """
    Given no access token in the session,
    When accessing a route protected by the 'access_token_login_required' decorator,
    Then it should redirect to the login page.
    """

    @app.route("/protected")
    @access_token_login_required
    def protected_route():
        return "Access granted"

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = None
        response = client.get("/protected")
        assert response.status_code == 302
        assert response.headers["Location"] == url_for("main.login")


@patch(
    "app.main.authorize.keycloak_login_required_decorator.decode_keycloak_access_token"
)
def test_access_token_login_required_decorator_inactive_token(
    mock_decode_keycloak_access_token, app
):
    """
    Given an inactive access token in the session,
    When accessing a route protected by the 'access_token_login_required' decorator,
    Then it should redirect to the login page.
    """

    @app.route("/protected")
    @access_token_login_required
    def protected_route():
        return "Access granted"

    mock_decode_keycloak_access_token.return_value = {"active": False}

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "some_token"
        response = client.get("/protected")

        assert response.status_code == 302
        assert response.headers["Location"] == url_for("main.login")


@patch(
    "app.main.authorize.keycloak_login_required_decorator.check_if_user_has_access_to_ayr"
)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.decode_keycloak_access_token"
)
def test_access_token_login_required_decorator_active_without_ayr_access(
    mock_decode_keycloak_access_token, mock_check_if_user_has_access_to_ayr, app
):
    """
    Given an active access token in the session,
    And the user does not have access to AYR,
    When accessing a route protected by the 'access_token_login_required' decorator,
    Then it should redirect to the index page with a flashed message.
    """

    @app.route("/protected")
    @access_token_login_required
    def protected_route():
        return "Access granted"

    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["foo", "bar"],
    }
    mock_check_if_user_has_access_to_ayr.return_value = False

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        response = client.get("/protected")

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
    "app.main.authorize.keycloak_login_required_decorator.check_if_user_has_access_to_ayr"
)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.decode_keycloak_access_token"
)
def test_access_token_login_required_decorator_valid_token(
    mock_decode_keycloak_access_token, mock_check_if_user_has_access_to_ayr, app
):
    """
    Given an active access token in the session,
    And the user has access to AYR,
    When accessing a route protected by the 'access_token_login_required' decorator,
    Then it should grant access and display a flashed message.
    """

    @app.route("/protected")
    @access_token_login_required
    def protected_route():
        return "Access granted"

    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["foo", "bar"],
    }
    mock_check_if_user_has_access_to_ayr.return_value = True

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        response = client.get("/protected")

        with client.session_transaction() as session:
            flashed_messages = session["_flashes"]

        assert flashed_messages == [
            ("message", "TNA User is logged in and has access to AYR.")
        ]

        assert response.status_code == 200
        assert b"Access granted" in response.data
