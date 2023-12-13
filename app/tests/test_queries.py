import uuid
from datetime import datetime
from unittest.mock import patch

from flask.testing import FlaskClient
from sqlalchemy import exc

from app.main.db.models import Body, db
from app.main.db.queries import (
    browse_data,
    fuzzy_search,
    get_file_metadata,
    get_user_accessible_transferring_bodies,
)
from app.tests.mock_database import create_test_file, create_two_test_files


class TestFuzzySearch:
    def test_fuzzy_search_no_results(self, client: FlaskClient):
        """
        Given a query string that does not match any field in any file object
            in the database
        When fuzzy_search is called with it
        Then an empty list is returned
        """
        create_two_test_files()

        query = "junk"
        assert fuzzy_search(query) == []

    def test_fuzzy_search_with_results(self, client: FlaskClient):
        """
        Given 2 File objects in the database
            and a query string that matches some fields in only 1 of them
        When fuzzy_search is called with the query
        Then a list containing 1 dictionary with information for the corresponding
            file is returned
        """
        files = create_two_test_files()

        query = "test body1"
        assert fuzzy_search(query) == [
            {
                "file_id": files[0].FileId,
                "transferring_body_id": files[
                    0
                ].file_consignments.consignment_bodies.BodyId,
                "transferring_body": "test body1",
                "series_id": files[
                    0
                ].file_consignments.consignment_series.SeriesId,
                "series": "test series1",
                "consignment_reference": "test consignment1",
                "file_name": "test_file1.pdf",
            }
        ]

    @patch("app.main.db.queries.db")
    def test_fuzzy_search_exception_raised(self, db, capsys):
        """
        Given a database execution error
        When fuzzy_search is called
        Then it returns an empty list and logs an error message
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
        Given 2 File objects in the database
        When browse_data is called without any arguments
        Then it returns a list containing dictionaries for each record with
            expected fields
        """
        files = create_two_test_files()

        assert browse_data() == [
            {
                "transferring_body_id": files[
                    0
                ].file_consignments.consignment_bodies.BodyId,
                "transferring_body": "test body1",
                "series_id": files[
                    0
                ].file_consignments.consignment_series.SeriesId,
                "series": "test series1",
                "consignment_in_series": 1,
                "last_record_transferred": datetime(2023, 1, 1, 0, 0),
                "records_held": 1,
            },
            {
                "transferring_body_id": files[
                    1
                ].file_consignments.consignment_bodies.BodyId,
                "transferring_body": "test body2",
                "series_id": files[
                    1
                ].file_consignments.consignment_series.SeriesId,
                "series": "test series2",
                "consignment_in_series": 1,
                "last_record_transferred": datetime(2023, 1, 1, 0, 0),
                "records_held": 1,
            },
        ]

    def test_browse_data_with_transferring_body_filter(
        self, client: FlaskClient
    ):
        """
        Given 2 File objects in the database and a transferring_body_id
            that matches only one of them
        When browse_data is called with transferring_body_id
        Then it returns a list containing 1 dictionary for the matching record with
            expected fields
        """
        files = create_two_test_files()

        file = files[0]

        transferring_body_id = file.file_consignments.consignment_bodies.BodyId
        series_id = file.file_consignments.consignment_series.SeriesId

        assert browse_data(transferring_body_id=transferring_body_id) == [
            {
                "transferring_body_id": transferring_body_id,
                "transferring_body": "test body1",
                "series_id": series_id,
                "series": "test series1",
                "consignment_in_series": 1,
                "last_record_transferred": datetime(2023, 1, 1, 0, 0),
                "records_held": 1,
            }
        ]

    def test_browse_data_with_series_filter(self, client: FlaskClient):
        """
        Given 2 File objects in the database and a series_id
            that matches only one of them
        When browse_data is called with series_id
        Then it returns a list containing 1 dictionary for the matching record with
            expected fields
        """
        files = create_two_test_files()

        file = files[0]

        transferring_body_id = file.file_consignments.consignment_bodies.BodyId
        series_id = file.file_consignments.consignment_series.SeriesId
        consignment_id = file.file_consignments.ConsignmentId

        assert browse_data(series_id=series_id) == [
            {
                "consignment_id": consignment_id,
                "consignment_reference": "test consignment1",
                "transferring_body_id": transferring_body_id,
                "transferring_body": "test body1",
                "series_id": series_id,
                "series": "test series1",
                "last_record_transferred": datetime(2023, 1, 1, 0, 0),
                "records_held": 1,
            }
        ]

    @patch("app.main.db.queries.db")
    def test_browse_data_exception_raised(self, db, capsys):
        """
        Given a database execution error
        When browse_data is called
        Then it returns an empty list and logs an error message
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
        Given n UUID not corresponding to the id of a File in the database
        When get_file_metadata is called with it
        Then an empty list is returned
        """
        non_existent_file_id = uuid.uuid4()
        assert get_file_metadata(non_existent_file_id) == []

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
        Given a database execution error
        When get_file_metadata itransferring_body_ids called
        Then it returns an empty list and logs an error message
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
    def test_no_token_returns_empty_list(
        self,
    ):
        """
        Given no access token,
        When calling the get_user_transferring_body_keycloak_groups
        Then it should return an empty list
        """
        results = get_user_accessible_transferring_bodies(None)
        assert results == []

    @patch("app.main.db.queries.decode_token")
    def test_inactive_token_returns_empty_list(self, mock_decode_token):
        """
        Given an inactive access token
        When calling get_user_transferring_body_keycloak_groups with it
        Then it should return an empty list
        """
        mock_decode_token.return_value = {
            "active": False,
        }
        assert get_user_accessible_transferring_bodies("access_token") == []

    @patch("app.main.db.queries.decode_token")
    def test_no_transferring_bodies_returns_empty_list(
        self,
        mock_decode_token,
    ):
        """
        Given an access token which once decoded contains 2 transferring body groups
        When I call get_user_accessible_transferring_bodies with it
        Then it should return a list with the 2 corresponding body names
        """
        mock_decode_token.return_value = {
            "active": True,
            "groups": [
                "/something_else/test body1",
                "/something_else/test body2",
                "/ayr_user/bar",
            ],
        }
        results = get_user_accessible_transferring_bodies("access_token")
        assert results == []

    @patch("app.main.db.queries.decode_token")
    def test_transferring_bodies_in_groups_returns_corresponding_body_names(
        self, mock_decode_token, client: FlaskClient
    ):
        """
        Given an access token which once decoded contains 2 groups prefixed with
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

        mock_decode_token.return_value = {
            "active": True,
            "groups": [
                "/transferring_body_user/test body1",
                "/transferring_body_user/test body2",
                "/foo/bar",
            ],
        }
        results = get_user_accessible_transferring_bodies("access_token")
        assert results == ["test body1", "test body2"]

    @patch("app.main.db.queries.db")
    @patch("app.main.db.queries.decode_token")
    def test_db_raised_exception_returns_empty_list_and_log_message(
        self, mock_decode_token, db, capsys, client
    ):
        """
        Given a db execution error
        When get_user_accessible_transferring_bodies is called
        Then the list should be empty and an error message is logged
        """
        mock_decode_token.return_value = {
            "active": True,
            "groups": [
                "/transferring_body_user/test body1",
                "/transferring_body_user/test body2",
                "/ayr_user/bar",
            ],
        }

        def mock_execute(_):
            raise exc.SQLAlchemyError("foo bar")

        db.session.execute.side_effect = mock_execute

        results = get_user_accessible_transferring_bodies("access_token")
        assert results == []
        assert (
            "Failed to return results from database with error : foo bar"
            in capsys.readouterr().out
        )
