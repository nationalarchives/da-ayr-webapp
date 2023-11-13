from unittest.mock import patch

import pytest
from flask import url_for

EXPECTED_PROTECTED_VIEWS = ["main.poc_search", "main.record"]


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
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
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
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
)
def test_access_token_login_required_decorator_active_without_ayr_access(
        mock_decode_keycloak_access_token,
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
        "groups": ["application_1/foo", "application_2/bar"],
    }

    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    app.config["KEYCLOAK_AYR_USER_GROUP"] = "application_3"

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
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
)
def test_access_token_login_required_decorator_valid_token(
        mock_decode_keycloak_access_token,
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
        "groups": ["application_1/foo", "application_2/bar"],
    }

    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    app.config["KEYCLOAK_AYR_USER_GROUP"] = "application_1"
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        response = client.get(url_for(view_name))

        assert response.status_code == 200


@pytest.mark.parametrize("view_name", EXPECTED_PROTECTED_VIEWS)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
)
def test_decode_token(mock_decode_keycloak_access_token, view_name, app):
    """
    Given an active access token in the session,
    When access token given
    Then it should decode token
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["application_1/foo", "application_2/bar"],
    }
    print(mock_decode_keycloak_access_token.return_value["active"])
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    app.config["KEYCLOAK_AYR_USER_GROUP"] = "application_1"
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        assert mock_decode_keycloak_access_token.return_value["active"]
        assert mock_decode_keycloak_access_token.return_value["groups"][0] == "application_1/foo"


@pytest.mark.parametrize("view_name", EXPECTED_PROTECTED_VIEWS)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
)
def test_get_user_transferring_body_groups_invalid_access_token(mock_decode_keycloak_access_token, view_name, app):
    """
    Given an active access token in the session,
    When access token given
    Then it should not return user groups
    """
    mock_decode_keycloak_access_token.return_value = {}
    user_groups_list = []
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    app.config["KEYCLOAK_AYR_USER_GROUP"] = "application_1"
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = None

        assert len(user_groups_list) == 0


@pytest.mark.parametrize("view_name", EXPECTED_PROTECTED_VIEWS)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
)
def test_get_user_transferring_body_groups_inactive_access_token(mock_decode_keycloak_access_token, view_name, app):
    """
    Given an active access token in the session,
    When access token given
    Then it should not return user groups list
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": False,
        "groups": ["application_1/foo", "application_2/bar"],
    }
    user_groups_list = []
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    app.config["KEYCLOAK_AYR_USER_GROUP"] = "application_1"
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        assert len(user_groups_list) == 0


@pytest.mark.parametrize("view_name", EXPECTED_PROTECTED_VIEWS)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
)
def test_get_user_transferring_body_groups_active_access_token_invalid_transferring_body(
        mock_decode_keycloak_access_token, view_name, app):
    """
    Given an active access token in the session,
    When access token given
    Then it should not return user group list
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["/application_1/foo", "/application_2/bar"],
    }
    user_groups_list = []
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    app.config["KEYCLOAK_AYR_USER_GROUP"] = "application_1"
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        for group in mock_decode_keycloak_access_token.return_value["groups"]:
            index = group.find("transferring_body")

        assert index == -1


@pytest.mark.parametrize("view_name", EXPECTED_PROTECTED_VIEWS)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
)
def test_get_user_transferring_body_groups_active_access_token_valid_transferring_body(mock_decode_keycloak_access_token,
                                                                                       view_name, app):
    """
    Given an active access token in the session,
    When access token given
    Then it should return 2 items in user group list
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["/transferring_body/foo", "/transferring_body/bar"],
    }
    user_groups_list = []
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    app.config["KEYCLOAK_AYR_USER_GROUP"] = "application_1"
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        for group in mock_decode_keycloak_access_token.return_value["groups"]:
            index = group.find("transferring_body")
            print(index)
            if index != -1:
                user_groups_list.append(group[2])

        assert len(user_groups_list) == 2


@pytest.mark.parametrize("view_name", EXPECTED_PROTECTED_VIEWS)
@patch(
    "app.main.authorize.keycloak_login_required_decorator.keycloak.KeycloakOpenID.introspect"
)
def test_get_user_transferring_body_groups_active_access_token_valid_transferring_body(mock_decode_keycloak_access_token,
                                                                                       view_name, app):
    """
    Given an active access token in the session,
    When access token given
    Then it should return 2 items in user group list
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["/transferring_body/foo", "/transferring_body/bar", "/ayr_user/bar"],
    }
    user_groups_list = []
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    app.config["KEYCLOAK_AYR_USER_GROUP"] = "application_1"
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        for group in mock_decode_keycloak_access_token.return_value["groups"]:
            index = group.find("transferring_body")
            if index != -1:
                user_groups_list.append(group[2])

        assert len(user_groups_list) == 2
