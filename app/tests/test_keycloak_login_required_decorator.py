from unittest.mock import patch

import pytest
from flask import url_for

EXPECTED_PROTECTED_VIEWS = [("main.poc_search"), ("main.record")]


@pytest.mark.parametrize("view_name", EXPECTED_PROTECTED_VIEWS)
def test_access_token_login_required_decorator_no_token(view_name, app):
    """
    Given no access token in the session,
    When accessing a route protected by the 'access_token_login_required' decorator,
    Then it should redirect to the login page.
    """
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = None
        response = client.get(url_for(view_name))
        assert response.status_code == 302
        assert response.headers["Location"] == url_for("main.login")


@pytest.mark.parametrize("view_name", EXPECTED_PROTECTED_VIEWS)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.decode_keycloak_access_token"
)
def test_access_token_login_required_decorator_inactive_token(
    mock_decode_keycloak_access_token, view_name, app
):
    """
    Given an inactive access token in the session,
    When accessing a route protected by the 'access_token_login_required' decorator,
    Then it should redirect to the login page.
    """
    mock_decode_keycloak_access_token.return_value = {"active": False}

    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "some_token"
        response = client.get(url_for(view_name))

        assert response.status_code == 302
        assert response.headers["Location"] == url_for("main.login")


@pytest.mark.parametrize("view_name", EXPECTED_PROTECTED_VIEWS)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.check_if_user_has_access_to_ayr"
)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.decode_keycloak_access_token"
)
def test_access_token_login_required_decorator_active_without_ayr_access(
    mock_decode_keycloak_access_token,
    mock_check_if_user_has_access_to_ayr,
    view_name,
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
        "groups": ["foo", "bar"],
    }
    mock_check_if_user_has_access_to_ayr.return_value = False

    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        response = client.get(url_for(view_name))

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


@pytest.mark.parametrize("view_name", EXPECTED_PROTECTED_VIEWS)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.check_if_user_has_access_to_ayr"
)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.decode_keycloak_access_token"
)
def test_access_token_login_required_decorator_valid_token(
    mock_decode_keycloak_access_token,
    mock_check_if_user_has_access_to_ayr,
    view_name,
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
        "groups": ["foo", "bar"],
    }
    mock_check_if_user_has_access_to_ayr.return_value = True

    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        response = client.get(url_for(view_name))

        assert response.status_code == 200
