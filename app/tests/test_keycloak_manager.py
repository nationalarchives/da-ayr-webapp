from unittest.mock import patch

from app.main.authorize.keycloak_manager import (
    decode_token,
    get_user_transferring_body_groups,
)


@patch("app.main.authorize.keycloak_manager.keycloak.KeycloakOpenID")
def test_decode_token(mock_keycloak_open_id, app):
    """
    Given a valid access token,
    When decoding the token using the decode_token function,
    Then it should return the decoded token,
    And it should make the correct calls to KeycloakOpenID for token introspection.
    """
    mock_keycloak_open_id.return_value.introspect.return_value = {
        "active": True,
        "groups": ["application_1/foo", "application_2/bar"],
    }

    app.config["KEYCLOAK_BASE_URI"] = "a"
    app.config["KEYCLOAK_CLIENT_ID"] = "b"
    app.config["KEYCLOAK_REALM_NAME"] = "c"
    app.config["KEYCLOAK_CLIENT_SECRET"] = "d"

    with app.app_context():
        decoded_token = decode_token("valid_token")

    assert decoded_token == {
        "active": True,
        "groups": ["application_1/foo", "application_2/bar"],
    }

    mock_keycloak_open_id.assert_called_once_with(
        server_url="a", client_id="b", realm_name="c", client_secret_key="d"
    )
    mock_keycloak_open_id.return_value.introspect.assert_called_once()


class TestGetUserTransferringBodyGroups:
    def test_no_token_returns_empty_list(self):
        """
        Given no access token,
        When calling the get_user_transferring_body_groups
        Then it should return an empty list of user groups.
        """
        assert get_user_transferring_body_groups(None) == []

    @patch(
        "app.main.authorize.keycloak_manager.keycloak.KeycloakOpenID.introspect"
    )
    def test_inactive_token_returns_empty_list(
        self, mock_decode_keycloak_access_token, app
    ):
        """
        Given an inactive access token
        When calling get_user_transferring_body_groups with it
        Then it should return an empty list
        """
        mock_decode_keycloak_access_token.return_value = {
            "active": False,
            "groups": ["application_1/foo", "application_2/bar"],
        }

        with app.app_context():
            assert get_user_transferring_body_groups("some_token_string") == []

    @patch(
        "app.main.authorize.keycloak_manager.keycloak.KeycloakOpenID.introspect"
    )
    def test_no_transferring_body_user_groups_returns_empty_list(
        self, mock_decode_keycloak_access_token, app
    ):
        """
        Given an active access token which has no transferring_body_user groups
        When calling get_user_transferring_body_groups with it
        Then it should return an empty list
        """
        mock_decode_keycloak_access_token.return_value = {
            "active": True,
            "groups": ["application_1/foo", "application_2/bar"],
        }
        with app.app_context():
            assert get_user_transferring_body_groups("some_token_string") == []

    @patch(
        "app.main.authorize.keycloak_manager.keycloak.KeycloakOpenID.introspect"
    )
    def test_multiple_transferring_body_user_groups_returns_corresponding_list(
        self, mock_decode_keycloak_access_token, app
    ):
        """
        Given an active access token which has 2 transferring_body_user groups
        When calling get_user_transferring_body_groups with it
        Then it should return the 2 corresponding strings in a list
        """
        mock_decode_keycloak_access_token.return_value = {
            "active": True,
            "groups": [
                "/transferring_body_user/foo",
                "/transferring_body_user/bar",
                "/ayr_user/abc",
            ],
        }

        with app.app_context():
            assert get_user_transferring_body_groups("some_token_string") == [
                "foo",
                "bar",
            ]
