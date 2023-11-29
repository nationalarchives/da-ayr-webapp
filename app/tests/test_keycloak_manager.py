from unittest.mock import patch


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_decode_token(mock_decode_keycloak_access_token, app):
    """
    Given an active access token in the session,
    When access token given
    Then it should decode token
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["application_1/foo", "application_2/bar"],
    }
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        assert mock_decode_keycloak_access_token.return_value["active"]
        assert (
            mock_decode_keycloak_access_token.return_value["groups"][0]
            == "application_1/foo"
        )


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_get_user_transferring_body_groups_invalid_access_token(
    mock_decode_keycloak_access_token, app
):
    """
    Given an active access token in the session,
    When access token given
    Then it should not return user groups
    """
    mock_decode_keycloak_access_token.return_value = {}
    user_groups_list = []
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = None

        assert len(user_groups_list) == 0


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_get_user_transferring_body_groups_inactive_access_token(
    mock_decode_keycloak_access_token, app
):
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
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        assert len(user_groups_list) == 0


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_get_user_transferring_body_groups_active_access_token_invalid_transferring_body(
    mock_decode_keycloak_access_token, app
):
    """
    Given an active access token in the session,
    When access token given
    Then it should not return user group list
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["/application_1/foo", "/application_2/bar"],
    }
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        for group in mock_decode_keycloak_access_token.return_value["groups"]:
            index = group.find("transferring_body")

        assert index == -1


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_get_user_transferring_body_groups_multiple_transferring_body(
    mock_decode_keycloak_access_token, app
):
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
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        for group in mock_decode_keycloak_access_token.return_value["groups"]:
            index = group.find("transferring_body")
            print(index)
            if index != -1:
                user_groups_list.append(group[2])

        assert len(user_groups_list) == 2


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_get_user_transferring_body_groups_return_multiple_transferring_body(
    mock_decode_keycloak_access_token, app
):
    """
    Given an active access token in the session,
    When access token given
    Then it should return 2 items in user group list
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": [
            "/transferring_body/foo",
            "/transferring_body/bar",
            "/ayr_user/bar",
        ],
    }
    user_groups_list = []
    app.config["FORCE_AUTHENTICATION_FOR_IN_TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        for group in mock_decode_keycloak_access_token.return_value["groups"]:
            index = group.find("transferring_body")
            if index != -1:
                user_groups_list.append(group[2])

        assert len(user_groups_list) == 2
