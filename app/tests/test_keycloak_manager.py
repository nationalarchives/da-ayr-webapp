from unittest.mock import patch

from app.main.authorize.keycloak_manager import (
    decode_token,
    get_user_transferring_body_keycloak_groups,
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
    def test_no_transferring_body_user_groups_returns_empty_list(self, app):
        """
        Given a list of keycloak groups which has no transferring_body_user groups
        When calling get_user_transferring_body_keycloak_groups with it
        Then it should return an empty list
        """
        with app.app_context():
            assert (
                get_user_transferring_body_keycloak_groups(
                    ["application_1/foo", "application_2/bar"]
                )
                == []
            )

    def test_multiple_transferring_body_user_groups_returns_corresponding_bodies(
        self, app
    ):
        """
        Given a list of keycloak groups including 2 transferring bodies
        When calling get_user_transferring_body_keycloak_groups with it
        Then it should return the 2 corresponding bodies in a list
        """
        with app.app_context():
            assert get_user_transferring_body_keycloak_groups(
                [
                    "/transferring_body_user/foo",
                    "/transferring_body_user/bar",
                    "/ayr_user/abc",
                ]
            ) == [
                "foo",
                "bar",
            ]

    def test_group_with_transferring_body_group_prefix_without_suffix_not_returned(
        self, app
    ):
        """
        Given a list of keycloak groups including 2 with
            `/transferring_body_user/` prefix but only has a suffix
        When calling get_user_transferring_body_keycloak_groups with it
        Then it should return a list including 1 element corresponding to the suffix
        """

        with app.app_context():
            assert get_user_transferring_body_keycloak_groups(
                [
                    "/transferring_body_user/foo",
                    "/ayr_user/abc",
                    "/transferring_body_user/",
                ]
            ) == [
                "foo",
            ]
