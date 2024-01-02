import uuid
from unittest.mock import patch

import pytest
import werkzeug
from flask.testing import FlaskClient
from sqlalchemy import exc

from app.main.authorize.permissions_helpers import (
    get_user_accessible_transferring_bodies,
    validate_body_user_groups_or_404,
)
from app.main.db.models import Body, db
from app.tests.conftest import mock_standard_user, mock_superuser
from app.tests.factories import BodyFactory


def test_does_not_raise_404_for_body_name_user_has_access_to_and_is_in_database(
    client,
):
    """
    Given a Body with name 'foo' in the database
    And a standard user with access to the body 'foo'
    When validate_body_user_groups_or_404 is called with 'foo'
    Then the function should not raise a 404 exception
    """
    BodyFactory(Name="foo")
    mock_standard_user(client, "foo")

    validate_body_user_groups_or_404("foo")


def test_raises_404_for_body_name_in_database_but_user_does_not_have_access_to(
    client,
):
    """
    Given a Body with name 'foo' in the database
    And a standard user without access to the body 'foo'
    When validate_body_user_groups_or_404 is called with 'foo'
    Then the function should raise a 404 exception
    """
    BodyFactory(Name="foo")
    mock_standard_user(client, "bar")

    with pytest.raises(werkzeug.exceptions.NotFound):
        validate_body_user_groups_or_404("foo")


def test_raises_404_for_body_name_user_has_access_to_but_is_not_in_database(
    client,
):
    """
    Given a standard user with access to the body 'foo'
    And no Body with name 'foo' in the database
    When validate_body_user_groups_or_404 is called with 'foo'
    Then the function should raise a 404 exception
    """
    BodyFactory(Name="bar")
    mock_standard_user(client, "foo")

    with pytest.raises(werkzeug.exceptions.NotFound):
        validate_body_user_groups_or_404("foo")


def test_does_not_raise_404_for_body_name_not_in_database_or_assigned_to_user_for_superuser(
    client,
):
    """
    Given a superuser
    When validate_body_user_groups_or_404 is called with any body name, e.g. 'foo'
    Then the function should not raise a 404 exception
    """
    mock_superuser(client)

    validate_body_user_groups_or_404("foo")


class TestGetUserAccessibleTransferringBodies:
    def test_no_groups_returns_empty_list(
        self,
    ):
        """
        Given an empty list,
        When calling get_user_accessible_transferring_bodies with it
        Then it should return an empty list
        """
        results = get_user_accessible_transferring_bodies([])
        assert results == []

    def test_no_transferring_bodies_returns_empty_list(
        self,
    ):
        """
        Given a list of groups not containing any /transferring_body_user/ groups
        When I call get_user_accessible_transferring_bodies with it
        Then it should return an empty list
        """
        results = get_user_accessible_transferring_bodies(
            [
                "/something_else/test body1",
                "/something_else/test body2",
                "/ayr_user_type/bar",
            ]
        )
        assert results == []

    def test_transferring_bodies_in_groups_returns_corresponding_body_names(
        self, client: FlaskClient
    ):
        """
        Given a list of groups including 2 prefixed with
            /transferring_body_user/
            and another group
            and 2 corresponding bodies in the database
            and an extra body in the database
        When get_user_accessible_transferring_bodies is called with it
        Then it should return a list with the 2 corresponding body names
        """
        body_1 = Body(
            BodyId=uuid.uuid4(), Name="test body1", Description="test body1"
        )
        db.session.add(body_1)
        db.session.commit()

        body_2 = Body(
            BodyId=uuid.uuid4(), Name="test body2", Description="test body2"
        )
        db.session.add(body_2)
        db.session.commit()

        body_3 = Body(
            BodyId=uuid.uuid4(), Name="test body3", Description="test body3"
        )
        db.session.add(body_3)
        db.session.commit()

        results = get_user_accessible_transferring_bodies(
            [
                "/transferring_body_user/test body1",
                "/transferring_body_user/test body2",
                "/foo/bar",
            ]
        )
        assert results == ["test body1", "test body2"]

    @patch("app.main.authorize.permissions_helpers.db")
    def test_db_raised_exception_returns_empty_list_and_log_message(
        self, database, capsys, client
    ):
        """
        Given a db execution error
        When get_user_accessible_transferring_bodies is called
        Then it should return an empty list and an error message is logged
        """

        def mock_execute(_):
            raise exc.SQLAlchemyError("foo bar")

        database.session.execute.side_effect = mock_execute

        results = get_user_accessible_transferring_bodies(
            [
                "/transferring_body_user/test body1",
                "/transferring_body_user/test body2",
                "/ayr_user_type/bar",
            ]
        )
        assert results == []
        assert (
            "Failed to return results from database with error : foo bar"
            in capsys.readouterr().out
        )
