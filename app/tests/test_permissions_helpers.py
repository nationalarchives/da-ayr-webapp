import pytest
import werkzeug

from app.main.authorize.permissions_helpers import (
    validate_body_user_groups_or_404,
)
from app.tests.factories import BodyFactory


def test_does_not_raise_404_for_body_name_user_has_access_to_and_is_in_database(
    client, mock_standard_user
):
    """
    Given a Body with name 'foo' in the database
    And a standard user with access to the body 'foo'
    When validate_body_user_groups_or_404 is called with 'foo'
    Then the function should not raise a 404 exception
    """
    BodyFactory(Name="foo")
    mock_standard_user(client, ["foo"])

    validate_body_user_groups_or_404("foo")


def test_raises_404_for_body_name_in_database_but_user_does_not_have_access_to(
    client, mock_standard_user
):
    """
    Given a Body with name 'foo' in the database
    And a standard user without access to the body 'foo'
    When validate_body_user_groups_or_404 is called with 'foo'
    Then the function should raise a 404 exception
    """
    BodyFactory(Name="foo")
    mock_standard_user(client, ["bar"])

    with pytest.raises(werkzeug.exceptions.NotFound):
        validate_body_user_groups_or_404("foo")


def test_raises_404_for_body_name_user_has_access_to_but_is_not_in_database(
    client, mock_standard_user
):
    """
    Given a standard user with access to the body 'foo'
    And no Body with name 'foo' in the database
    When validate_body_user_groups_or_404 is called with 'foo'
    Then the function should raise a 404 exception
    """
    BodyFactory(Name="bar")
    mock_standard_user(client, ["foo"], get_or_create_body=False)

    with pytest.raises(werkzeug.exceptions.NotFound):
        validate_body_user_groups_or_404("foo")


def test_does_not_raise_404_for_body_name_not_in_database_or_assigned_to_user_for_superuser(
    client, mock_superuser
):
    """
    Given a superuser
    When validate_body_user_groups_or_404 is called with any body name, e.g. 'foo'
    Then the function should not raise a 404 exception
    """
    mock_superuser(client)

    validate_body_user_groups_or_404("foo")
