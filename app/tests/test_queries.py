import uuid

import pytest
import werkzeug
from flask.testing import FlaskClient

from app.main.db.queries import browse_data, fuzzy_search, get_file_metadata
from app.tests.factories import (
    ConsignmentFactory,
    FileFactory,
    FileMetadataFactory,
)
from app.tests.mock_database import create_multiple_test_records

per_page = 5


class TestFuzzySearch:
    def test_fuzzy_search_blank_query_parameter(self, client: FlaskClient):
        """
        Given a query string not provided
        When fuzzy_search is called with it
        Then None is returned
        """

        query = ""
        result = fuzzy_search(query, page=1, per_page=per_page)
        assert result is None

    def test_fuzzy_search_no_results(self, client: FlaskClient):
        """
        Given a query string that does not match any field in any file object
            in the database
        When fuzzy_search is called with it
        Then an empty list is returned
        """

        query = "junk"
        result = fuzzy_search(query, page=1, per_page=per_page)
        assert result.items == []

    def test_fuzzy_search_with_single_record_result(self, client: FlaskClient):
        """
        Given multiple File objects in the database
            and a query string that matches some fields in only 1 of them
        When fuzzy_search is called with the query
        Then a list containing 1 dictionary with information for the corresponding
            file is returned
        """
        files = create_multiple_test_records()

        query = "test body2"
        result = fuzzy_search(query, page=1, per_page=per_page)
        assert result.items == [
            (
                "test body2",
                "test series2",
                "test consignment2",
                "test_file2.txt",
                files[1].file_consignments.consignment_bodies.BodyId,
                files[1].file_consignments.consignment_series.SeriesId,
            )
        ]

    def test_fuzzy_search_with_single_page_result(self, client: FlaskClient):
        """
        Given multiple File objects in the database
            and a query string that matches some fields in only 1 of them
        When fuzzy_search is called with the query
        Then a list containing 2 (max - per_page) dictionary with information for the corresponding
            file is returned
        and more than 1 page returned false
        and has_next return false
        """
        files = create_multiple_test_records()

        query = "test body1"
        result = fuzzy_search(query, page=1, per_page=per_page)
        assert result.items == [
            (
                "test body1",
                "test series1",
                "test consignment1",
                "test_file1.pdf",
                files[0].file_consignments.consignment_bodies.BodyId,
                files[0].file_consignments.consignment_series.SeriesId,
            ),
            (
                "testing body11",
                "test series11",
                "test consignment11",
                "test_file11.txt",
                files[10].file_consignments.consignment_bodies.BodyId,
                files[10].file_consignments.consignment_series.SeriesId,
            ),
        ]
        assert result.pages == 1
        assert result.has_next is False

    def test_fuzzy_search_with_multiple_page_results(self, client: FlaskClient):
        """
        Given multiple File objects in the database
            and a query string that matches some fields in only 1 of them
        When fuzzy_search is called with the query
        Then a list containing 5 (per_page) dictionary with information for the corresponding
            file is returned
        and more than 1 page returned true
        and has_next return true
        """
        files = create_multiple_test_records()

        query = "testing body"
        result = fuzzy_search(query, page=1, per_page=per_page)
        assert result.items == [
            (
                "testing body10",
                "test series10",
                "test consignment10",
                "test_file10.txt",
                files[9].file_consignments.consignment_bodies.BodyId,
                files[9].file_consignments.consignment_series.SeriesId,
            ),
            (
                "testing body11",
                "test series11",
                "test consignment11",
                "test_file11.txt",
                files[10].file_consignments.consignment_bodies.BodyId,
                files[10].file_consignments.consignment_series.SeriesId,
            ),
            (
                "testing body3",
                "test series3",
                "test consignment3",
                "test_file3.pdf",
                files[2].file_consignments.consignment_bodies.BodyId,
                files[2].file_consignments.consignment_series.SeriesId,
            ),
            (
                "testing body4",
                "test series4",
                "test consignment4",
                "test_file4.txt",
                files[3].file_consignments.consignment_bodies.BodyId,
                files[3].file_consignments.consignment_series.SeriesId,
            ),
            (
                "testing body5",
                "test series5",
                "test consignment5",
                "test_file5.txt",
                files[4].file_consignments.consignment_bodies.BodyId,
                files[4].file_consignments.consignment_series.SeriesId,
            ),
        ]
        assert result.pages > 0
        assert result.has_next is True

    def test_fuzzy_search_get_specific_page_results(self, client: FlaskClient):
        """
        Given multiple File objects in the database
            and a query string that matches some fields in only 1 of them
        When fuzzy_search is called with the query
        Then a list containing 5 (per_page) dictionary with information for the corresponding
            file is returned for page 2
        """
        files = create_multiple_test_records()

        query = "testing body"
        result = fuzzy_search(query, page=2, per_page=per_page)
        assert result.items == [
            (
                "testing body6",
                "test series6",
                "test consignment6",
                "test_file6.txt",
                files[5].file_consignments.consignment_bodies.BodyId,
                files[5].file_consignments.consignment_series.SeriesId,
            ),
            (
                "testing body7",
                "test series7",
                "test consignment7",
                "test_file7.txt",
                files[6].file_consignments.consignment_bodies.BodyId,
                files[6].file_consignments.consignment_series.SeriesId,
            ),
            (
                "testing body8",
                "test series8",
                "test consignment8",
                "test_file8.txt",
                files[7].file_consignments.consignment_bodies.BodyId,
                files[7].file_consignments.consignment_series.SeriesId,
            ),
            (
                "testing body9",
                "test series9",
                "test consignment9",
                "test_file9.txt",
                files[8].file_consignments.consignment_bodies.BodyId,
                files[8].file_consignments.consignment_series.SeriesId,
            ),
        ]
        assert result.pages > 0
        assert result.has_next is False
        assert result.has_prev is True


class TestBrowse:
    def test_browse_without_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'browse'
        Then it returns a Pagination object with 5 total results as per page option value
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse"
        )

        assert pagination_object.total == 7

        expected_results = [
            (
                browse_files[19].file_consignments.consignment_bodies.BodyId,
                browse_files[19].file_consignments.consignment_bodies.Name,
                browse_files[19].file_consignments.consignment_series.SeriesId,
                browse_files[19].file_consignments.consignment_series.Name,
                "21/09/2023",
                2,
                6,
            ),
            (
                browse_files[0].file_consignments.consignment_bodies.BodyId,
                browse_files[0].file_consignments.consignment_bodies.Name,
                browse_files[0].file_consignments.consignment_series.SeriesId,
                browse_files[0].file_consignments.consignment_series.Name,
                "07/02/2023",
                2,
                3,
            ),
            (
                browse_files[13].file_consignments.consignment_bodies.BodyId,
                browse_files[13].file_consignments.consignment_bodies.Name,
                browse_files[13].file_consignments.consignment_series.SeriesId,
                browse_files[13].file_consignments.consignment_series.Name,
                "03/08/2023",
                2,
                6,
            ),
            (
                browse_files[3].file_consignments.consignment_bodies.BodyId,
                browse_files[3].file_consignments.consignment_bodies.Name,
                browse_files[3].file_consignments.consignment_series.SeriesId,
                browse_files[3].file_consignments.consignment_series.Name,
                "26/04/2023",
                2,
                7,
            ),
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[27].file_consignments.consignment_series.SeriesId,
                browse_files[27].file_consignments.consignment_series.Name,
                "25/11/2023",
                1,
                1,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_get_specific_page_results(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'browse' and
            with page=2 ( specific page)
        Then it returns a Pagination object with 2 total results as per page option value
            ordered by Body name then Series name
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        pagination_object = browse_data(
            page=2, per_page=per_page, browse_type="browse"
        )

        assert pagination_object.total == 7

        # return 2 records on page 2 as first five records are on page 1
        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[25].file_consignments.consignment_series.SeriesId,
                browse_files[25].file_consignments.consignment_series.Name,
                "14/10/2023",
                1,
                2,
            ),
            (
                browse_files[10].file_consignments.consignment_bodies.BodyId,
                browse_files[10].file_consignments.consignment_bodies.Name,
                browse_files[10].file_consignments.consignment_series.SeriesId,
                browse_files[10].file_consignments.consignment_series.Name,
                "17/06/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_transferring_body_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            transferring body filter
        Then it returns a Pagination object with 1 total results corresponding to the
            transferring body which match to the filter value
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        filters = {"transferring_body": "third_body"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[10].file_consignments.consignment_bodies.BodyId,
                browse_files[10].file_consignments.consignment_bodies.Name,
                browse_files[10].file_consignments.consignment_series.SeriesId,
                browse_files[10].file_consignments.consignment_series.Name,
                "17/06/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_transferring_body_filter_return_multiple_results(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            transferring body filter
        Then it returns a Pagination object with 2 total results corresponding to the
            transferring body which match to the filter value
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        # use like comparison to return multiple bodies start with fi keyword e.g. first, fifth
        filters = {"transferring_body": "fi"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[19].file_consignments.consignment_bodies.BodyId,
                browse_files[19].file_consignments.consignment_bodies.Name,
                browse_files[19].file_consignments.consignment_series.SeriesId,
                browse_files[19].file_consignments.consignment_series.Name,
                "21/09/2023",
                2,
                6,
            ),
            (
                browse_files[0].file_consignments.consignment_bodies.BodyId,
                browse_files[0].file_consignments.consignment_bodies.Name,
                browse_files[0].file_consignments.consignment_series.SeriesId,
                browse_files[0].file_consignments.consignment_series.Name,
                "07/02/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_series_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            series filter
        Then it returns a Pagination object with 1 total results corresponding to the
            series which match to the filter value
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        filters = {"series": "third_series"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[10].file_consignments.consignment_bodies.BodyId,
                browse_files[10].file_consignments.consignment_bodies.Name,
                browse_files[10].file_consignments.consignment_series.SeriesId,
                browse_files[10].file_consignments.consignment_series.Name,
                "17/06/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_series_filter_return_multiple_results(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            series filter
        Then it returns a Pagination object with 2 total results corresponding to the
            series which match to the filter value
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        # use like comparison to return multiple series start with fi keyword e.g. first, fifth
        filters = {"series": "fi"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[19].file_consignments.consignment_bodies.BodyId,
                browse_files[19].file_consignments.consignment_bodies.Name,
                browse_files[19].file_consignments.consignment_series.SeriesId,
                browse_files[19].file_consignments.consignment_series.Name,
                "21/09/2023",
                2,
                6,
            ),
            (
                browse_files[0].file_consignments.consignment_bodies.BodyId,
                browse_files[0].file_consignments.consignment_bodies.Name,
                browse_files[0].file_consignments.consignment_series.SeriesId,
                browse_files[0].file_consignments.consignment_series.Name,
                "07/02/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_date_consignment_transferred_filter_using_date_from_option(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            date from filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is greater than or equal to the date from value
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        filters = {"date_range": {"date_from": "01/11/2023"}}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[27].file_consignments.consignment_bodies.BodyId,
                browse_files[27].file_consignments.consignment_bodies.Name,
                browse_files[27].file_consignments.consignment_series.SeriesId,
                browse_files[27].file_consignments.consignment_series.Name,
                "25/11/2023",
                1,
                1,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_date_consignment_transferred_filter_using_date_to_option(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            date to filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is less than or equal to the date to value
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        filters = {"date_range": {"date_to": "07/02/2023"}}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[0].file_consignments.consignment_bodies.BodyId,
                browse_files[0].file_consignments.consignment_bodies.Name,
                browse_files[0].file_consignments.consignment_series.SeriesId,
                browse_files[0].file_consignments.consignment_series.Name,
                "07/02/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_date_consignment_transferred_filter_using_date_from_and_date_to_option(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            date from and date to filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is between date from and date to values
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        filters = {
            "date_range": {"date_from": "01/01/2023", "date_to": "07/02/2023"}
        }
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[0].file_consignments.consignment_bodies.BodyId,
                browse_files[0].file_consignments.consignment_bodies.Name,
                browse_files[0].file_consignments.consignment_series.SeriesId,
                browse_files[0].file_consignments.consignment_series.Name,
                "07/02/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_date_consignment_transferred_filter_using_date_from_and_date_to_option_multiple_results(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            date from and date to filter
        Then it returns a Pagination object with 2 total results corresponding to the
            consignment transfer complete date which is between date from and date to values
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        filters = {
            "date_range": {"date_from": "01/01/2023", "date_to": "30/04/2023"}
        }
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[0].file_consignments.consignment_bodies.BodyId,
                browse_files[0].file_consignments.consignment_bodies.Name,
                browse_files[0].file_consignments.consignment_series.SeriesId,
                browse_files[0].file_consignments.consignment_series.Name,
                "07/02/2023",
                2,
                3,
            ),
            (
                browse_files[3].file_consignments.consignment_bodies.BodyId,
                browse_files[3].file_consignments.consignment_bodies.Name,
                browse_files[3].file_consignments.consignment_series.SeriesId,
                browse_files[3].file_consignments.consignment_series.Name,
                "26/04/2023",
                2,
                7,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_date_consignment_transferred_filter_using_date_from_and_date_to_option_no_result(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            date from and date to filter
        Then if date range not matched to any records
            it returns empty list containing multiple dictionary
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        filters = {
            "date_range": {"date_from": "01/01/2023", "date_to": "10/01/2023"}
        }
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 0

    def test_browse_with_transferring_body_and_series_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            transferring body and series filter
        Then it returns a Pagination object with 1 total results corresponding to the
            transferring body and series which match to the filter value
        """

        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        filters = {"transferring_body": "third_body", "series": "third_series"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[10].file_consignments.consignment_bodies.BodyId,
                browse_files[10].file_consignments.consignment_bodies.Name,
                browse_files[10].file_consignments.consignment_series.SeriesId,
                browse_files[10].file_consignments.consignment_series.Name,
                "17/06/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_transferring_body_and_date_consignment_transferred_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            transferring body and date range (date from, date to) filter
        Then it returns a Pagination object with 1 total results corresponding to the
            transferring body match to the filter value and
            consignment transfer complete date which is between date from and date to values
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        filters = {
            "transferring_body": "second_body",
            "date_range": {"date_from": "01/01/2023", "date_to": "26/04/2023"},
        }
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[3].file_consignments.consignment_bodies.BodyId,
                browse_files[3].file_consignments.consignment_bodies.Name,
                browse_files[3].file_consignments.consignment_series.SeriesId,
                browse_files[3].file_consignments.consignment_series.Name,
                "26/04/2023",
                2,
                7,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_series_and_date_consignment_transferred_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            series and date range (date from, date to) filter
        Then it returns a Pagination object with 1 total results corresponding to the
            series match to the filter value and
            consignment transfer complete date which is between date from and date to values
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        filters = {
            "series": "second_series",
            "date_range": {"date_from": "01/01/2023", "date_to": "26/04/2023"},
        }
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[3].file_consignments.consignment_bodies.BodyId,
                browse_files[3].file_consignments.consignment_bodies.Name,
                browse_files[3].file_consignments.consignment_series.SeriesId,
                browse_files[3].file_consignments.consignment_series.Name,
                "26/04/2023",
                2,
                7,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_transferring_body_and_series_and_date_consignment_transferred_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            transferring body and series and date range (date from, date to) filter
        Then it returns a Pagination object with 1 total results corresponding to the
            transferring body match to the filter value and series match to the filter value and
            consignment transfer complete date which is between date from and date to values
        """
        mock_standard_user(
            client, [browse_files[0].file_consignments.consignment_bodies.Name]
        )

        filters = {
            "transferring_body": "second_body",
            "series": "second_series",
            "date_range": {"date_from": "01/01/2023", "date_to": "26/04/2023"},
        }
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[3].file_consignments.consignment_bodies.BodyId,
                browse_files[3].file_consignments.consignment_bodies.Name,
                browse_files[3].file_consignments.consignment_series.SeriesId,
                browse_files[3].file_consignments.consignment_series.Name,
                "26/04/2023",
                2,
                7,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results


class TestBrowseTransferringBody:
    def test_browse_transferring_body_without_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'transferring body' and
            without any filter values
        Then it returns a Pagination object with 2 total results
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        transferring_body_id = browse_files[
            25
        ].file_consignments.consignment_bodies.BodyId

        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            transferring_body_id=transferring_body_id,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[27].file_consignments.consignment_series.SeriesId,
                browse_files[27].file_consignments.consignment_series.Name,
                "25/11/2023",
                1,
                1,
            ),
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[25].file_consignments.consignment_series.SeriesId,
                browse_files[25].file_consignments.consignment_series.Name,
                "14/10/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_series_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with the series filter
        Then it returns a Pagination object with 1 total results corresponding to the
            series which match to the filter value
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        transferring_body_id = browse_files[
            25
        ].file_consignments.consignment_bodies.BodyId

        filters = {"series": "sixth_series"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            filters=filters,
            transferring_body_id=transferring_body_id,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[25].file_consignments.consignment_series.SeriesId,
                browse_files[25].file_consignments.consignment_series.Name,
                "14/10/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_series_filter_return_multiple_results(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with the series filter
        Then it returns a Pagination object with 2 total results corresponding to the
            series which match to the filter value
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        transferring_body_id = browse_files[
            25
        ].file_consignments.consignment_bodies.BodyId

        # use like comparison to return multiple series start with fi keyword e.g. sixth, seventh
        filters = {"series": "s"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            filters=filters,
            transferring_body_id=transferring_body_id,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[27].file_consignments.consignment_series.SeriesId,
                browse_files[27].file_consignments.consignment_series.Name,
                "25/11/2023",
                1,
                1,
            ),
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[25].file_consignments.consignment_series.SeriesId,
                browse_files[25].file_consignments.consignment_series.Name,
                "14/10/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_date_consignment_transferred_filter_using_date_from_option(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with date from filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is greater than or equal to the date from value
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        transferring_body_id = browse_files[
            25
        ].file_consignments.consignment_bodies.BodyId

        filters = {"date_range": {"date_from": "20/10/2023"}}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            filters=filters,
            transferring_body_id=transferring_body_id,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[27].file_consignments.consignment_series.SeriesId,
                browse_files[27].file_consignments.consignment_series.Name,
                "25/11/2023",
                1,
                1,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_date_consignment_transferred_filter_using_date_to_option(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with date to filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is less than or equal to the date to value
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        transferring_body_id = browse_files[
            25
        ].file_consignments.consignment_bodies.BodyId

        filters = {"date_range": {"date_to": "20/10/2023"}}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            filters=filters,
            transferring_body_id=transferring_body_id,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[25].file_consignments.consignment_series.SeriesId,
                browse_files[25].file_consignments.consignment_series.Name,
                "14/10/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_date_consignment_transferred_filter_using_date_from_and_date_to_option(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with date range (date from and date to) filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date between date from and date to value
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        transferring_body_id = browse_files[
            25
        ].file_consignments.consignment_bodies.BodyId

        filters = {
            "date_range": {"date_from": "20/10/2023", "date_to": "25/11/2023"}
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            filters=filters,
            transferring_body_id=transferring_body_id,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[27].file_consignments.consignment_series.SeriesId,
                browse_files[27].file_consignments.consignment_series.Name,
                "25/11/2023",
                1,
                1,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_date_consignment_transferred_filter_using_date_range_option_multiple_results(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with date range (date from and date to) filter
        Then it returns a Pagination object with 2 total results corresponding to the
            consignment transfer complete date between date from and date to value
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        transferring_body_id = browse_files[
            25
        ].file_consignments.consignment_bodies.BodyId

        filters = {
            "date_range": {"date_from": "10/10/2023", "date_to": "25/11/2023"}
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            filters=filters,
            transferring_body_id=transferring_body_id,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[27].file_consignments.consignment_series.SeriesId,
                browse_files[27].file_consignments.consignment_series.Name,
                "25/11/2023",
                1,
                1,
            ),
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[25].file_consignments.consignment_series.SeriesId,
                browse_files[25].file_consignments.consignment_series.Name,
                "14/10/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_series_and_date_consignment_transferred_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with date range (date from and date to) filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date between date from and date to value
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        transferring_body_id = browse_files[
            25
        ].file_consignments.consignment_bodies.BodyId

        filters = {
            "series": "seventh_series",
            "date_range": {"date_from": "10/10/2023", "date_to": "25/11/2023"},
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            filters=filters,
            transferring_body_id=transferring_body_id,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[27].file_consignments.consignment_series.SeriesId,
                browse_files[27].file_consignments.consignment_series.Name,
                "25/11/2023",
                1,
                1,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results


class TestBrowseSeries:
    def test_browse_series_without_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            without any filter values
        Then it returns a Pagination object with 1 total results
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        series_id = browse_files[
            25
        ].file_consignments.consignment_series.SeriesId

        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="series", series_id=series_id
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[25].file_consignments.consignment_series.SeriesId,
                browse_files[25].file_consignments.consignment_series.Name,
                "14/10/2023",
                2,
                browse_files[25].file_consignments.ConsignmentId,
                browse_files[25].file_consignments.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_transferring_body_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            with transferring body as filter
        Then it returns a Pagination object with 1 total results corresponding to
            transferring body filter value
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        series_id = browse_files[
            25
        ].file_consignments.consignment_series.SeriesId
        filters = {"transferring_body": "sixth_body"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
            filters=filters,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[25].file_consignments.consignment_series.SeriesId,
                browse_files[25].file_consignments.consignment_series.Name,
                "14/10/2023",
                2,
                browse_files[25].file_consignments.ConsignmentId,
                browse_files[25].file_consignments.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_date_consignment_transferred_filter_using_date_from_option(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            with date from filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is greater than or equal to the date from value
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        series_id = browse_files[
            25
        ].file_consignments.consignment_series.SeriesId
        filters = {"date_range": {"date_from": "10/10/2023"}}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
            filters=filters,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[25].file_consignments.consignment_series.SeriesId,
                browse_files[25].file_consignments.consignment_series.Name,
                "14/10/2023",
                2,
                browse_files[25].file_consignments.ConsignmentId,
                browse_files[25].file_consignments.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_date_consignment_transferred_filter_using_date_to_option(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            with date to filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is greater than or equal to the date from value
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        series_id = browse_files[
            25
        ].file_consignments.consignment_series.SeriesId
        filters = {"date_range": {"date_to": "15/10/2023"}}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
            filters=filters,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[25].file_consignments.consignment_series.SeriesId,
                browse_files[25].file_consignments.consignment_series.Name,
                "14/10/2023",
                2,
                browse_files[25].file_consignments.ConsignmentId,
                browse_files[25].file_consignments.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_date_consignment_transferred_filter_using_date_from_and_date_to_option(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 28 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            with date range (date from and date to) filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date between date from and date to value
        """
        mock_standard_user(
            client, [browse_files[25].file_consignments.consignment_bodies.Name]
        )

        series_id = browse_files[
            25
        ].file_consignments.consignment_series.SeriesId
        filters = {
            "date_range": {"date_from": "10/10/2023", "date_to": "15/10/2023"}
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
            filters=filters,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[25].file_consignments.consignment_bodies.BodyId,
                browse_files[25].file_consignments.consignment_bodies.Name,
                browse_files[25].file_consignments.consignment_series.SeriesId,
                browse_files[25].file_consignments.consignment_series.Name,
                "14/10/2023",
                2,
                browse_files[25].file_consignments.ConsignmentId,
                browse_files[25].file_consignments.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results


class TestBrowseConsignment:
    def test_browse_data_with_consignment_filter(
        self, client, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            of the first 3 file objects
        Then it returns a Pagination object with 2 total results corresponding to the
            first 2 files, ordered by their names and with the expected metadata values
        """
        consignment = ConsignmentFactory()

        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment, FileName="file_1", FileType="file"
        )

        file_1_metadata = {
            "date_last_modified": "2023-02-25T10:12:47",
            "closure_type": "Closed",
            "closure_start_date": "2023-02-25T11:14:34",
            "closure_period": "50",
        }

        [
            FileMetadataFactory(
                file_metadata=file_1,
                PropertyName=property_name,
                Value=value,
            )
            for property_name, value in file_1_metadata.items()
        ]

        file_2 = FileFactory(
            file_consignments=consignment, FileName="file_2", FileType="file"
        )

        file_2_metadata = {
            "date_last_modified": "2023-02-27T12:28:08",
            "closure_type": "Open",
            "closure_start_date": None,
            "closure_period": None,
        }

        [
            FileMetadataFactory(
                file_metadata=file_2,
                PropertyName=property_name,
                Value=value,
            )
            for property_name, value in file_2_metadata.items()
        ]

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                file_1.FileId,
                "file_1",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "50",
            ),
            (
                file_2.FileId,
                "file_2",
                "27/02/2023",
                "Open",
                None,
                None,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_and_record_status_open_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id and record status filter as 'Open'
            of the first 3 file objects
        Then it returns a Pagination object with 1 total results corresponding to the
            closure_type file metadata value set to 'Open' ( 1 file),
            ordered by their names and with the expected metadata values
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "record_status": "Open",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                file_2.FileId,
                "file_2",
                "27/02/2023",
                "Open",
                None,
                None,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_and_record_status_closed_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id and record status filter as 'Closed'
            of the first 3 file objects
        Then it returns a Pagination object with 1 total results corresponding to the
            closure_type file metadata value set to 'Closed' ( 1 file),
            ordered by their names and with the expected metadata values
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "record_status": "Closed",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                file_1.FileId,
                "file_1",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_and_record_status_all_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id and record status filter as 'all'
            of the first 3 file objects
        Then it returns a Pagination object with 2 total results corresponding to the
            closure_type file metadata value is either 'Open' or 'Closed' (2 files),
            ordered by their names and with the expected metadata values
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "record_status": "all",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                file_1.FileId,
                "file_1",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_2.FileId,
                "file_2",
                "27/02/2023",
                "Open",
                None,
                None,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_and_file_type_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id and file type filter as '.docx'
            of the first 3 file objects
        Then it returns a Pagination object with 2 total results corresponding to the
            file_name file metadata value contains extension '.docx' (2 files),
            ordered by their names and with the expected metadata values
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment,
            FileName="file_1.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment,
            FileName="file_2.ppt",
            FileType="file",
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            file_consignments=consignment,
            FileName="file_3.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "file_type": ".docx",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                file_1.FileId,
                "file_1.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_3.FileId,
                "file_3.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_and_record_status_and_file_type_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id and record status filter as 'Closed'
        and file type filter as '.docx'
            of the first 3 file objects
        Then it returns a Pagination object with 1 total results corresponding to the
            closure_type metadata value set to 'Closed' and
            file_name file metadata value contains extension '.docx' (1 file),
            ordered by their names and with the expected metadata values
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment,
            FileName="file_1.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment,
            FileName="file_2.ppt",
            FileType="file",
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            file_consignments=consignment,
            FileName="file_3.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_3, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_start_date",
            Value=None,
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_period",
            Value=None,
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "record_status": "Closed",
            "file_type": ".docx",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                file_1.FileId,
                "file_1.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_and_record_status_and_date_range_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id and record status filter as 'Closed'
        and date_range between from and to date
            of the first 3 file objects
        Then it returns a Pagination object with 1 total results corresponding to the
            closure_type metadata value set to 'Closed' and
            date_last_modified metadata value match between date_from and date_to filter (1 file),
            ordered by their names and with the expected metadata values
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment,
            FileName="file_1.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment,
            FileName="file_2.ppt",
            FileType="file",
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            file_consignments=consignment,
            FileName="file_3.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-28T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-28T10:12:47",
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "record_status": "Closed",
            "date_range": {"date_from": "01/02/2023", "date_to": "25/02/2023"},
            "date_filter_field": "date_last_modified",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                file_1.FileId,
                "file_1.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_and_file_type_and_date_range_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id and file_type filter as '.docx'
        and date_range between from and to date
            of the first 3 file objects
        Then it returns a Pagination object with 1 total results corresponding to the
            file_name metadata value contains file extension as '.docx'
            date_last_modified metadata value match between date_from and date_to filter (1 file),
            ordered by their names and with the expected metadata values
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment,
            FileName="file_1.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment,
            FileName="file_2.ppt",
            FileType="file",
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            file_consignments=consignment,
            FileName="file_3.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-28T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-28T10:12:47",
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "file_type": ".docx",
            "date_range": {"date_from": "01/02/2023", "date_to": "25/02/2023"},
            "date_filter_field": "date_last_modified",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                file_1.FileId,
                "file_1.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_and_date_from_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id and date_from filter
            of the first 3 file objects
        Then it returns a Pagination object with 2 total results corresponding to the
            date_last_modified greater than or equal date_from filter value ( 2 files),
            ordered by their names and with the expected metadata values
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "date_range": {"date_from": "25/02/2023"},
            "date_filter_field": "date_last_modified",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                file_1.FileId,
                "file_1",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_2.FileId,
                "file_2",
                "27/02/2023",
                "Open",
                None,
                None,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_and_date_to_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id and date_to filter
            of the first 3 file objects
        Then it returns a Pagination object with 1 total results corresponding to the
            date_last_modified less than or equal date_to filter value ( 1 file),
            ordered by their names and with the expected metadata values
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "date_range": {"date_to": "26/02/2023"},
            "date_filter_field": "date_last_modified",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                file_1.FileId,
                "file_1",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            )
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_and_date_from_and_to_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id and date_from and date_to filter
            of the first 3 file objects
        Then it returns a Pagination object with 2 total results corresponding to the
            date_last_modified greater than or equal to date_from filter value and
            date_last_modified less than or equal date_to filter value ( 2 file),
            ordered by their names and with the expected metadata values
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        mock_standard_user(
            client, file_1.file_consignments.consignment_bodies.Name
        )
        filters = {
            "date_range": {"date_from": "01/02/2023", "date_to": "28/02/2023"},
            "date_filter_field": "date_last_modified",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                file_1.FileId,
                "file_1",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_2.FileId,
                "file_2",
                "27/02/2023",
                "Open",
                None,
                None,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_filter_and_record_status_sorting_closed_first(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id filter and record_status as sorting in ascending
            of the first 3 file objects
        Then it returns a Pagination object with 3 total results
            ordered by their closure_type 'Closed' first and then 'Open' in ascending orders
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            file_consignments=consignment, FileName="file_3", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "record_status": "all",
        }
        sorting_orders = {
            "closure_type": "asc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                file_1.FileId,
                "file_1",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_3.FileId,
                "file_3",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_2.FileId,
                "file_2",
                "27/02/2023",
                "Open",
                None,
                None,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_filter_and_record_status_sorting_open_first(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id filter and record_status as sorting in descending
            of the first 3 file objects
        Then it returns a Pagination object with 3 total results
            ordered by their closure_type 'Closed' first and then 'Open' in ascending orders
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            file_consignments=consignment, FileName="file_3", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "record_status": "all",
        }
        sorting_orders = {
            "closure_type": "desc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                file_2.FileId,
                "file_2",
                "27/02/2023",
                "Open",
                None,
                None,
            ),
            (
                file_1.FileId,
                "file_1",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_3.FileId,
                "file_3",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_filter_and_date_last_modified_sorting_oldest_first(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id filter
            and sort by date last modified as oldest first(ascending)
            of the first 3 file objects
        Then it returns a Pagination object with 3 total results
            ordered by their date last modified as oldest first(ascending)
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            file_consignments=consignment, FileName="file_3", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="date_last_modified",
            Value="2023-01-23T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_start_date",
            Value="2023-01-23T10:12:47",
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "record_status": "all",
        }
        sorting_orders = {
            "date_last_modified": "asc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                file_3.FileId,
                "file_3",
                "23/01/2023",
                "Closed",
                "23/01/2023",
                "1",
            ),
            (
                file_1.FileId,
                "file_1",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_2.FileId,
                "file_2",
                "27/02/2023",
                "Open",
                None,
                None,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_filter_and_date_last_modified_sorting_most_recent_first(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id filter
            and sort by date last modified as most recent(descending)
            of the first 3 file objects
        Then it returns a Pagination object with 3 total results
            ordered by their date last modified as most recent(descending)
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            file_consignments=consignment, FileName="file_3", FileType="file"
        )

        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="date_last_modified",
            Value="2023-01-23T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_start_date",
            Value="2023-01-23T10:12:47",
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "record_status": "all",
        }
        sorting_orders = {
            "date_last_modified": "desc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                file_2.FileId,
                "file_2",
                "27/02/2023",
                "Open",
                None,
                None,
            ),
            (
                file_1.FileId,
                "file_1",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_3.FileId,
                "file_3",
                "23/01/2023",
                "Closed",
                "23/01/2023",
                "1",
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_filter_and_record_filename_sorting_a_to_z(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id filter and file name as sorting in ascending
            of the first 3 file objects
        Then it returns a Pagination object with 3 total results
            ordered by their file name in ascending orders (A to Z)
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment,
            FileName="first_file.txt",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment,
            FileName="fourth_file.pdf",
            FileType="file",
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            file_consignments=consignment,
            FileName="fifth_file.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "record_status": "all",
        }
        sorting_orders = {
            "file_name": "asc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                file_3.FileId,
                "fifth_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_1.FileId,
                "first_file.txt",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_2.FileId,
                "fourth_file.pdf",
                "27/02/2023",
                "Open",
                None,
                None,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_consignment_filter_and_record_filename_sorting_z_to_a(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given three file objects with associated metadata part of 1 consignment,
            where 2 file types is 'file', another file 'folder', and another file of
            type 'file' and metadata associated with a different consignment
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id filter and file name as sorting in descending
            of the first 3 file objects
        Then it returns a Pagination object with 3 total results
            ordered by their file name in descending orders (Z to A)
        """
        consignment = ConsignmentFactory()
        mock_standard_user(client, consignment.consignment_bodies.Name)

        file_1 = FileFactory(
            file_consignments=consignment,
            FileName="first_file.txt",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            file_consignments=consignment,
            FileName="fourth_file.pdf",
            FileType="file",
        )
        FileMetadataFactory(
            file_metadata=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file_metadata=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            file_consignments=consignment,
            FileName="fifth_file.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file_metadata=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file_metadata=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(file_consignments=consignment, FileType="folder")

        FileFactory(FileType="file")

        filters = {
            "record_status": "all",
        }
        sorting_orders = {
            "file_name": "desc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment.ConsignmentId,
            filters=filters,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                file_2.FileId,
                "fourth_file.pdf",
                "27/02/2023",
                "Open",
                None,
                None,
            ),
            (
                file_1.FileId,
                "first_file.txt",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
            (
                file_3.FileId,
                "fifth_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                "1",
            ),
        ]

        results = pagination_object.items

        assert results == expected_results


class TestGetFileMetadata:
    def test_invalid_uuid_raises_not_found_error(self, client: FlaskClient):
        """
        Given a UUID not corresponding to the id of a file in the database
        When get_file_metadata is called with it
        Then werkzeug.exceptions.NotFound is raised
        """
        non_existent_file_id = uuid.uuid4()
        with pytest.raises(werkzeug.exceptions.NotFound):
            get_file_metadata(non_existent_file_id)

    def test_valid_uuid_returns_metadata(self, client: FlaskClient):
        """
        Given a file with associated metadata,
        When get_file_metadata is called with its UUID,
        Then a tuple of specific metadata for the file is returned
        """
        file = FileFactory(
            FileName="test_file.txt",
            FilePath="data/content/test_file.txt",
            FileType="file",
        )

        metadata = {
            "date_last_modified": "2023-02-25T10:12:47",
            "closure_type": "Closed",
            "description": "Test description",
            "held_by": "Test holder",
            "legal_status": "Test legal status",
            "rights_copyright": "Test copyright",
            "language": "English",
        }

        [
            FileMetadataFactory(
                file_metadata=file,
                PropertyName=property_name,
                Value=value,
            )
            for property_name, value in metadata.items()
        ]

        assert get_file_metadata(file_id=file.FileId) == {
            "file_id": file.FileId,
            "file_name": "test_file.txt",
            "file_path": "data/content/test_file.txt",
            "status": "Closed",
            "description": "Test description",
            "date_last_modified": "2023-02-25T10:12:47",
            "held_by": "Test holder",
            "legal_status": "Test legal status",
            "rights_copyright": "Test copyright",
            "language": "English",
            "consignment": file.file_consignments.ConsignmentReference,
            "consignment_id": file.ConsignmentId,
            "transferring_body": file.file_consignments.consignment_bodies.Name,
            "transferring_body_id": file.file_consignments.consignment_bodies.BodyId,
            "series": file.file_consignments.consignment_series.Name,
            "series_id": file.file_consignments.consignment_series.SeriesId,
        }
