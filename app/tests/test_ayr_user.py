from app.main.authorize.ayr_user import AYRUser
from app.tests.factories import BodyFactory


class TestAYRUser:
    def test_type_of_user_when_ayr_user_type_view_dept_group(self):
        groups = ["/ayr_user_type/view_dept"]
        user = AYRUser(groups)
        assert user.is_standard_user
        assert not user.is_all_access_user

    def test_type_of_user_when_ayr_user_type_view_all_group(self):
        groups = ["/ayr_user_type/view_all"]
        user = AYRUser(groups)
        assert user.is_all_access_user
        assert not user.is_standard_user

    def test_type_of_user_when_no_valid_ayr_user_group(self):
        groups = ["/ayr_user_type/foo"]
        user = AYRUser(groups)
        assert not user.is_all_access_user
        assert not user.is_standard_user

    def test_can_access_ayr_when_all_access_user_and_no_bodies(self):
        groups = ["/ayr_user_type/view_all"]
        user = AYRUser(groups)
        assert user.is_all_access_user
        assert user.transferring_body is None
        assert user.can_access_ayr

    def test_can_access_ayr_when_standard_user_and_one_valid_body(self, app):
        body = BodyFactory(Name="foo")
        groups = ["/ayr_user_type/view_dept", "/transferring_body_user/foo"]
        user = AYRUser(groups)
        assert user.is_standard_user
        assert user.transferring_body == body
        assert user.can_access_ayr

    def test_cannot_access_ayr_when_all_access_user_and_some_bodies(self, app):
        groups = ["/ayr_user_type/view_all", "/transferring_body_user/foo"]
        user = AYRUser(groups)
        assert user.is_all_access_user
        assert user.transferring_body is None
        assert user.can_access_ayr

    def test_transferring_body_is_none_when_empty_groups(self, app):
        BodyFactory(Name="foo")
        BodyFactory(Name="bar")
        groups = []
        user = AYRUser(groups)
        assert user.transferring_body is None

    def test_transferring_body_is_first_valid_transferring_body_in_groups(
        self, app
    ):
        body = BodyFactory(Name="foo")
        BodyFactory(Name="bar")
        groups = [
            "/ayr_user_type/view_dept",
            "/transferring_body_user/foo",
            "/transferring_body_user/bar",
        ]
        user = AYRUser(groups)
        assert user.transferring_body == body

    def test_transferring_body_is_none_when_no_valid_transferring_body_in_groups(
        self, app
    ):
        groups = [
            "/ayr_user_type/view_dept",
            "/transferring_body_user/foo",
            "/transferring_body_user/bar",
        ]
        user = AYRUser(groups)
        assert user.transferring_body is None

    def test_when_all_access_user_transferring_bodies_is_none(self, client):
        groups = ["/ayr_user_type/view_all", "/transferring_body_user/foo"]
        user = AYRUser(groups)
        assert user.transferring_body is None

    def test_no_transferring_bodies_returns_empty_list(
        self,
    ):
        """
        Given a list of groups not containing any /transferring_body_user/ groups
        When I call get_user_accessible_transferring_body with it
        Then it should return an empty list
        """
        groups = [
            "/something_else/test body1",
            "/something_else/test body2",
            "/ayr_user_type/bar",
        ]

        user = AYRUser(groups)
        assert user.transferring_body is None
