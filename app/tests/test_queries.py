from unittest.mock import patch

from flask.testing import FlaskClient
from sqlalchemy import exc

from app.main.db.models import Body, Consignment, File, Series
from app.main.db.queries import (
    browse_data,
    fuzzy_search,
    get_file_metadata,
    get_user_accessible_transferring_bodies,
)
from app.tests.mock_database import create_two_test_records


def test_fuzzy_search_no_results(client: FlaskClient):
    """
    Given a user with a search query
    When they make a request, and no results are found
    Then they should see no records found.
    """

    query = "junk"
    search_results = fuzzy_search(query)

    assert len(search_results) == 0


def test_fuzzy_search_with_results(client: FlaskClient):
    """
    Given a user with a search query
    Then it should return n results
    """
    create_two_test_records()

    query = "test body1"
    search_results = fuzzy_search(query)

    assert len(search_results) == 1


@patch("app.main.db.queries.db")
def test_fuzzy_search_exception_raised(db, capsys):
    """
    Given a fuzzy search function
    When a call made to fuzzy search , when database execution failed with error
    Then list should be empty and should raise an exception
    """

    def mock_execute(_):
        raise exc.SQLAlchemyError("foo bar")

    db.session.execute.side_effect = mock_execute
    results = fuzzy_search("")
    assert results == []
    assert (
        "Failed to return results from database with error : foo bar"
        in capsys.readouterr().out
    )


def test_browse_data_without_filters(client: FlaskClient):
    """
    Given a user accessing the browse view query
    When they make a POST request without a filter
    Then it should return all the records.
    """
    create_two_test_records()

    search_results = browse_data()
    for result in search_results:
        print(result)
    assert len(search_results) == 2


def test_browse_data_with_transferring_body_filter(client: FlaskClient):
    """
    Given a user accessing the browse view query
    When they make a POST request with a transferring body filter
    Then it should return records matched to transferring body filter.
    """
    create_two_test_records()
    bodies = Body.query.all()

    transferring_body = bodies[0].BodyId
    search_results = browse_data(transferring_body_id=transferring_body)
    assert len(search_results) == 1


def test_browse_data_with_series_filter(client: FlaskClient):
    """
    Given a user accessing the browse view query
    When they make a POST request with a series filter
    Then it should return records matched to series filter.
    """
    create_two_test_records()
    series = Series.query.all()

    series_id = series[0].SeriesId
    search_results = browse_data(series_id=series_id)
    assert len(search_results) == 1


def test_browse_data_with_consignment_reference_filter(client: FlaskClient):
    """
    Given a user accessing the browse view query
    When they make a POST request with a consignment reference filter
    Then it should return records matched to consignment reference filter.
    """
    create_two_test_records()
    consignments = Consignment.query.all()

    consignment_id = consignments[0].ConsignmentId
    search_results = browse_data(consignment_id=consignment_id)
    assert len(search_results) == 1


@patch("app.main.db.queries.db")
def test_browse_data_exception_raised(db, capsys):
    """
    Given a browse data query
    When a call made to browse data , when database execution failed with error
    Then list should be empty and should raise an exception
    """

    def mock_execute(_):
        raise exc.SQLAlchemyError("foo bar")

    db.session.execute.side_effect = mock_execute
    results = browse_data()
    assert results == []
    assert (
        "Failed to return results from database with error : foo bar"
        in capsys.readouterr().out
    )


def test_get_file_metadata_no_results(client: FlaskClient):
    """
    Given a user with a search query
    When they make a request on the browse view series page, and no results are found
    Then they should see no records found.
    """
    file_id = "junk"
    search_results = get_file_metadata(file_id)

    assert len(search_results) == 0


def test_get_file_metadata_with_results(client: FlaskClient):
    """
    Given a user with a search query which should return n results
    When they make a request on the browse series page
    Then a table is populated with the n results with metadata fields.
    """
    create_two_test_records()
    files = File.query.all()

    file_id = files[0].FileId
    search_results = get_file_metadata(file_id=file_id)
    assert len(search_results) == 3


@patch("app.main.db.queries.db")
def test_get_file_metadata_exception_raised(db, capsys):
    """
    Given a file metadata query
    When a call made to file metadata , when database execution failed with error
    Then list should be empty and should raise an exception
    """

    def mock_execute(_):
        raise exc.SQLAlchemyError("foo bar")

    db.session.execute.side_effect = mock_execute
    results = get_file_metadata("")
    assert results == []
    assert (
        "Failed to return results from database with error : foo bar"
        in capsys.readouterr().out
    )


@patch("app.main.authorize.keycloak_manager.keycloak.KeycloakOpenID.introspect")
def test_get_user_accessible_transferring_bodies(
    mock_decode_keycloak_access_token, client: FlaskClient
):
    """
    Given a user calling get user accessible transferring bodies function
    Then it should return list of transferring bodies which user has access to
    """
    create_two_test_records()

    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": [
            "/transferring_body_user/test body1",
            "/transferring_body_user/test body2",
            "/ayr_user/bar",
        ],
    }
    results = get_user_accessible_transferring_bodies(
        mock_decode_keycloak_access_token
    )
    assert len(results) == 2
    assert results[0] == "test body1"


@patch("app.main.db.queries.db")
def test_get_user_accessible_transferring_bodies_exception_raised(db, capsys):
    """
    Given a get user accessible transferring bodies query
    When a call made to get user accessible transferring bodies , when database execution failed with error
    Then list should be empty and should raise an exception
    """

    def mock_execute(_):
        raise exc.SQLAlchemyError("foo bar")

    db.session.execute.side_effect = mock_execute

    results = get_user_accessible_transferring_bodies("")
    assert results == []
    assert (
        "Failed to return results from database with error : foo bar"
        in capsys.readouterr().out
    )
