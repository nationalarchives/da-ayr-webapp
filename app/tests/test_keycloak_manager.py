from unittest.mock import patch

from app.main.authorize.keycloak_manager import (
    get_user_groups,
    get_user_transferring_body_keycloak_groups,
)


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
                    "/ayr_user_type/abc",
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
                    "/ayr_user_type/abc",
                    "/transferring_body_user/",
                ]
            ) == [
                "foo",
            ]


class TestGetUserGroups:
    def test_no_token_returns_empty_list(
        self,
    ):
        """
        Given no access token,
        When calling the get_user_groups
        Then it should return an empty list
        """
        results = get_user_groups("")
        assert results == []

    @patch("app.main.authorize.keycloak_manager.keycloak.KeycloakOpenID")
    def test_inactive_user_returns_empty_list(self, mock_keycloak_open_id, app):
        """
        Given a mocked KeycloakOpenID with introspection result indicating an inactive user
        And configured Keycloak parameters in the Flask app
        When the get_user_groups function is called with a valid token
        Then the result should be an empty list
        And KeycloakOpenID should be instantiated with the correct configuration
        And introspect should be called once on the KeycloakOpenID instance
        """
        mock_keycloak_open_id.return_value.introspect.return_value = {
            "active": False,
        }

        app.config["KEYCLOAK_BASE_URI"] = "a"
        app.config["KEYCLOAK_CLIENT_ID"] = "b"
        app.config["KEYCLOAK_REALM_NAME"] = "c"
        app.config["KEYCLOAK_CLIENT_SECRET"] = "d"

        with app.app_context():
            groups = get_user_groups("valid_token")

        assert groups == []

        mock_keycloak_open_id.assert_called_once_with(
            server_url="a", client_id="b", realm_name="c", client_secret_key="d"
        )
        mock_keycloak_open_id.return_value.introspect.assert_called_once()

    @patch("app.main.authorize.keycloak_manager.keycloak.KeycloakOpenID")
    def test_active_user_returns_groups(self, mock_keycloak_open_id, app):
        """
        Given a mocked KeycloakOpenID with introspection result indicating an active user and associated groups
        And configured Keycloak parameters in the Flask app
        When the get_user_groups function is called with a valid token
        Then the result should be the list of associated groups
        And KeycloakOpenID should be instantiated with the correct configuration
        And introspect should be called once on the KeycloakOpenID instance
        """
        mock_keycloak_open_id.return_value.introspect.return_value = {
            "active": True,
            "groups": ["foo", "bar"],
        }

        app.config["KEYCLOAK_BASE_URI"] = "a"
        app.config["KEYCLOAK_CLIENT_ID"] = "b"
        app.config["KEYCLOAK_REALM_NAME"] = "c"
        app.config["KEYCLOAK_CLIENT_SECRET"] = "d"

        with app.app_context():
            groups = get_user_groups("valid_token")

        assert groups == ["foo", "bar"]

        mock_keycloak_open_id.assert_called_once_with(
            server_url="a", client_id="b", realm_name="c", client_secret_key="d"
        )
        mock_keycloak_open_id.return_value.introspect.assert_called_once()
