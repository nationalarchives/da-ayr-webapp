from datetime import datetime
from unittest.mock import patch

from flask.testing import FlaskClient
from sqlalchemy import exc

from app.main.db.models import Body, Series
from app.main.db.queries import (
    browse_data,
    fuzzy_search,
    get_file_metadata,
    get_user_accessible_transferring_bodies,
)
from app.tests.mock_database import create_test_file, create_two_test_records


class TestFuzzySearch:
    def test_fuzzy_search_no_results(self, client: FlaskClient):
        """
        Given a user with a search query
        When they make a request, and no results are found
        Then they should see no records found.
        """

        query = "junk"
        search_results = fuzzy_search(query)

        assert len(search_results) == 0


    def test_fuzzy_search_with_results(self, client: FlaskClient):
        """
        Given a user with a search query
        When they make a request, and no results are found
        Then they should see no records found.
        """
        create_two_test_records()

        query = "test body1"
        search_results = fuzzy_search(query)

        assert len(search_results) == 1
        assert search_results[0]["transferring_body"] == "test body1"
        assert search_results[0]["series"] == "test series1"
        assert search_results[0]["consignment_reference"] == "test consignment1"
        assert search_results[0]["file_name"] == "test_file1.pdf"


    @patch("app.main.db.queries.db")
    def test_fuzzy_search_exception_raised(self, db, capsys):
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


class TestBrowseData:
    def test_browse_data_without_filters(self, client: FlaskClient):
        """
        Given a user accessing the browse view query
        When they make a POST request without a filter
        Then it should return all the records.
        """
        create_two_test_records()

        search_results = browse_data()
        assert len(search_results) == 2
        assert search_results[0]["transferring_body"] == "test body1"
        assert search_results[0]["series"] == "test series1"
        assert search_results[0]["consignment_in_series"] == 1
        assert search_results[0]["last_record_transferred"] == datetime(
            2023, 1, 1, 0, 0
        )
        assert search_results[0]["records_held"] == 1
        assert search_results[1]["transferring_body"] == "test body2"
        assert search_results[1]["series"] == "test series2"
        assert search_results[1]["consignment_in_series"] == 1
        assert search_results[1]["last_record_transferred"] == datetime(
            2023, 1, 1, 0, 0
        )
        assert search_results[1]["records_held"] == 1


    def test_browse_data_with_transferring_body_filter(self, client: FlaskClient):
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
        assert search_results[0]["transferring_body"] == "test body1"
        assert search_results[0]["series"] == "test series1"
        assert search_results[0]["consignment_in_series"] == 1
        assert search_results[0]["last_record_transferred"] == datetime(
            2023, 1, 1, 0, 0
        )
        assert search_results[0]["records_held"] == 1


    def test_browse_data_with_series_filter(self, client: FlaskClient):
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
        assert search_results[0]["transferring_body"] == "test body1"
        assert search_results[0]["series"] == "test series1"
        assert search_results[0]["last_record_transferred"] == datetime(
            2023, 1, 1, 0, 0
        )
        assert search_results[0]["records_held"] == 1
        assert search_results[0]["consignment_reference"] == "test consignment1"


    @patch("app.main.db.queries.db")
    def test_browse_data_exception_raised(self, db, capsys):
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


class TestGetFileMetadata:
    def test_get_file_metadata_no_results(self, client: FlaskClient):
        """
        Given a user with a search query
        When they make a request on the browse view series page, and no results are found
        Then they should see no records found.
        """
        file_id = "junk"
        search_results = get_file_metadata(file_id)

        assert len(search_results) == 0


    def test_get_file_metadata(self, client: FlaskClient):
        """
        Given a file with 3 related file metadata objects
        When get_file_metadata is called with the file's FileId
        Then a list of dicts is returned with the property name-value pair in each dict
        """
        file = create_test_file()

        search_results = get_file_metadata(file_id=file.FileId)

        expected_search_results = [
            {"property_name": "file_name", "property_value": "test_file1.pdf"},
            {"property_name": "closure_type", "property_value": "open"},
            {"property_name": "file_type", "property_value": "pdf"},
        ]
        assert search_results == expected_search_results


    @patch("app.main.db.queries.db")
    def test_get_file_metadata_exception_raised(self, db, capsys):
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

class TestGetUserAccessibleTransferringBodies:

    @patch("app.main.authorize.keycloak_manager.keycloak.KeycloakOpenID.introspect")
    def test_get_user_accessible_transferring_bodies(
        self, mock_decode_keycloak_access_token, client: FlaskClient
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
        assert results == ["test body1", "test body2"]


    @patch("app.main.db.queries.db")
    def test_get_user_accessible_transferring_bodies_exception_raised(self, db, capsys):
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
