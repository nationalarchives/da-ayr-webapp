from app.main.authorize.keycloak_manager import (
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
