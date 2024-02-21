import uuid

import pytest
import werkzeug
from flask.testing import FlaskClient

from app.main.db.queries import (
    browse_data,
    build_fuzzy_search_query,
    build_fuzzy_search_summary_query,
    get_file_metadata,
)
from app.tests.factories import FileFactory, FileMetadataFactory

per_page = 5


class TestFuzzySearch:
    def test_build_fuzzy_search_query_with_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a filter value that does match transferring body in the database
        When build_browse_all_query is called with it and is executed
        Then matching list results rows is returned
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        query = build_fuzzy_search_query(query_string="fifth_file")
        results = query.all()

        expected_results = [
            (
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
                browse_consignment_files[4].FileName,
                "Open",
                None,
            ),
        ]
        assert results == expected_results

    def test_build_fuzzy_search_query_no_results(self, client: FlaskClient):
        """
        Given a filter value that does not match transferring body in the database
        When build_browse_all_query is called with it and is executed
        Then an empty list is returned
        """
        query = build_fuzzy_search_query(query_string="junk")
        results = query.all()
        assert results == []

    def test_build_fuzzy_search_summary_query_with_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a filter value that does match multiple in the database
        When build_browse_all_query is called with it and is executed
        Then matching list results rows is returned
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        query = build_fuzzy_search_summary_query(query_string="fi")
        results = query.all()

        expected_results = [
            (
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                15,
            ),
        ]
        assert results == expected_results

    def test_build_fuzzy_search_summary_query_no_results(
        self, client: FlaskClient
    ):
        """
        Given a filter value that does not match transferring body in the database
        When build_browse_all_query is called with it and is executed
        Then an empty list is returned
        """
        query = build_fuzzy_search_summary_query(query_string="junk")
        results = query.all()
        assert results == []


class TestBrowse:
    def test_browse_without_filter(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'browse'
        Then it returns a Pagination object with 5 total results as per page option value
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse"
        )

        assert pagination_object.total == 6

        expected_results = [
            (
                browse_files[19].consignment.series.body.BodyId,
                browse_files[19].consignment.series.body.Name,
                browse_files[19].consignment.series.SeriesId,
                browse_files[19].consignment.series.Name,
                "21/09/2023",
                2,
                6,
            ),
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
                "07/02/2023",
                2,
                3,
            ),
            (
                browse_files[13].consignment.series.body.BodyId,
                browse_files[13].consignment.series.body.Name,
                browse_files[13].consignment.series.SeriesId,
                browse_files[13].consignment.series.Name,
                "03/08/2023",
                2,
                6,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "26/04/2023",
                2,
                7,
            ),
            (
                browse_files[25].consignment.series.body.BodyId,
                browse_files[25].consignment.series.body.Name,
                browse_files[25].consignment.series.SeriesId,
                browse_files[25].consignment.series.Name,
                "14/10/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_get_specific_page_results(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'browse' and
            with page=2 ( specific page)
        Then it returns a Pagination object with 2 total results as per page option value
            ordered by Body name then Series name
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        pagination_object = browse_data(
            page=2, per_page=per_page, browse_type="browse"
        )

        assert pagination_object.total == 6

        # return 1 records on page 2 as first five records are on page 1
        expected_results = [
            (
                browse_files[10].consignment.series.body.BodyId,
                browse_files[10].consignment.series.body.Name,
                browse_files[10].consignment.series.SeriesId,
                browse_files[10].consignment.series.Name,
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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            transferring body filter
        Then it returns a Pagination object with 1 total results corresponding to the
            transferring body which match to the filter value
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        filters = {"transferring_body": "third_body"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[10].consignment.series.body.BodyId,
                browse_files[10].consignment.series.body.Name,
                browse_files[10].consignment.series.SeriesId,
                browse_files[10].consignment.series.Name,
                "17/06/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_transferring_body_filter_with_wildcard_character(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            transferring body filter
        Then it returns a Pagination object with 1 total results corresponding to the
            transferring body which match to the filter value
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        filters = {"transferring_body": "fi"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[19].consignment.series.body.BodyId,
                browse_files[19].consignment.series.body.Name,
                browse_files[19].consignment.series.SeriesId,
                browse_files[19].consignment.series.Name,
                "21/09/2023",
                2,
                6,
            ),
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
                "07/02/2023",
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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            transferring body filter
        Then it returns a Pagination object with 2 total results corresponding to the
            transferring body which match to the filter value
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        # use like comparison to return multiple bodies start with fi keyword e.g. first, fifth
        filters = {"transferring_body": "fi"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[19].consignment.series.body.BodyId,
                browse_files[19].consignment.series.body.Name,
                browse_files[19].consignment.series.SeriesId,
                browse_files[19].consignment.series.Name,
                "21/09/2023",
                2,
                6,
            ),
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            series filter
        Then it returns a Pagination object with 1 total results corresponding to the
            series which match to the filter value
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        filters = {"series": "third_series"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[10].consignment.series.body.BodyId,
                browse_files[10].consignment.series.body.Name,
                browse_files[10].consignment.series.SeriesId,
                browse_files[10].consignment.series.Name,
                "17/06/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_series_filter_with_wildcard_character(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            series filter
        Then it returns a Pagination object with 2 total results corresponding to the
            series which match to the filter value
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        filters = {"series": "fi"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[19].consignment.series.body.BodyId,
                browse_files[19].consignment.series.body.Name,
                browse_files[19].consignment.series.SeriesId,
                browse_files[19].consignment.series.Name,
                "21/09/2023",
                2,
                6,
            ),
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
                "07/02/2023",
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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            series filter
        Then it returns a Pagination object with 2 total results corresponding to the
            series which match to the filter value
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        # use like comparison to return multiple series start with fi keyword e.g. first, fifth
        filters = {"series": "fi"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[19].consignment.series.body.BodyId,
                browse_files[19].consignment.series.body.Name,
                browse_files[19].consignment.series.SeriesId,
                browse_files[19].consignment.series.Name,
                "21/09/2023",
                2,
                6,
            ),
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            date from filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is greater than or equal to the date from value
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        filters = {"date_range": {"date_from": "01/10/2023"}}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[25].consignment.series.body.BodyId,
                browse_files[25].consignment.series.body.Name,
                browse_files[25].consignment.series.SeriesId,
                browse_files[25].consignment.series.Name,
                "14/10/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_date_consignment_transferred_filter_using_date_to_option(
        self, client, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            date to filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is less than or equal to the date to value
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        filters = {"date_range": {"date_to": "07/02/2023"}}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            date from and date to filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is between date from and date to values
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        filters = {
            "date_range": {"date_from": "01/01/2023", "date_to": "07/02/2023"}
        }
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            date from and date to filter
        Then it returns a Pagination object with 2 total results corresponding to the
            consignment transfer complete date which is between date from and date to values
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        filters = {
            "date_range": {"date_from": "01/01/2023", "date_to": "30/04/2023"}
        }
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
                "07/02/2023",
                2,
                3,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            date from and date to filter
        Then if date range not matched to any records
            it returns empty list containing multiple dictionary
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            transferring body and series filter
        Then it returns a Pagination object with 1 total results corresponding to the
            transferring body and series which match to the filter value
        """

        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        filters = {"transferring_body": "third_body", "series": "third_series"}
        pagination_object = browse_data(
            page=1, per_page=per_page, browse_type="browse", filters=filters
        )

        assert pagination_object.total == 1

        expected_results = [
            (
                browse_files[10].consignment.series.body.BodyId,
                browse_files[10].consignment.series.body.Name,
                browse_files[10].consignment.series.SeriesId,
                browse_files[10].consignment.series.Name,
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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            transferring body and date range (date from, date to) filter
        Then it returns a Pagination object with 1 total results corresponding to the
            transferring body match to the filter value and
            consignment transfer complete date which is between date from and date to values
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

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
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            series and date range (date from, date to) filter
        Then it returns a Pagination object with 1 total results corresponding to the
            series match to the filter value and
            consignment transfer complete date which is between date from and date to values
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

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
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
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
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'browse' and
            transferring body and series and date range (date from, date to) filter
        Then it returns a Pagination object with 1 total results corresponding to the
            transferring body match to the filter value and series match to the filter value and
            consignment transfer complete date which is between date from and date to values
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

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
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "26/04/2023",
                2,
                7,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_transferring_body_sorting_a_to_z(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'browse' and
            sort by 'transferring body' ascending
        Then it returns a Paginate object returning the first 5 items
            ordered by transferring body name alphabetically in ascending order (A to Z)
        """

        mock_standard_user(client, browse_files[0].consignment.series.body.Name)
        sorting_orders = {"transferring_body": "asc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="browse",
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 6

        expected_results = [
            (
                browse_files[19].consignment.series.body.BodyId,
                browse_files[19].consignment.series.body.Name,
                browse_files[19].consignment.series.SeriesId,
                browse_files[19].consignment.series.Name,
                "21/09/2023",
                2,
                6,
            ),
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
                "07/02/2023",
                2,
                3,
            ),
            (
                browse_files[13].consignment.series.body.BodyId,
                browse_files[13].consignment.series.body.Name,
                browse_files[13].consignment.series.SeriesId,
                browse_files[13].consignment.series.Name,
                "03/08/2023",
                2,
                6,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "26/04/2023",
                2,
                7,
            ),
            (
                browse_files[25].consignment.series.body.BodyId,
                browse_files[25].consignment.series.body.Name,
                browse_files[25].consignment.series.SeriesId,
                browse_files[25].consignment.series.Name,
                "14/10/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_transferring_body_sorting_z_to_a(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'browse' and
            sort by 'transferring body' descending
        Then it returns a Paginate object returning the first 5 items
            ordered by transferring body name alphabetically in descending order (Z to A)
        """

        mock_standard_user(client, browse_files[0].consignment.series.body.Name)
        sorting_orders = {"transferring_body": "desc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="browse",
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 6

        expected_results = [
            (
                browse_files[10].consignment.series.body.BodyId,
                browse_files[10].consignment.series.body.Name,
                browse_files[10].consignment.series.SeriesId,
                browse_files[10].consignment.series.Name,
                "17/06/2023",
                2,
                3,
            ),
            (
                browse_files[25].consignment.series.body.BodyId,
                browse_files[25].consignment.series.body.Name,
                browse_files[25].consignment.series.SeriesId,
                browse_files[25].consignment.series.Name,
                "14/10/2023",
                1,
                2,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "26/04/2023",
                2,
                7,
            ),
            (
                browse_files[13].consignment.series.body.BodyId,
                browse_files[13].consignment.series.body.Name,
                browse_files[13].consignment.series.SeriesId,
                browse_files[13].consignment.series.Name,
                "03/08/2023",
                2,
                6,
            ),
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
                "07/02/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_series_sorting_a_to_z(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'browse' and
            sort by 'series' ascending
        Then it returns a Paginate object returning the first 5 items
            ordered by series name alphabetically in ascending order (A to Z)
        """

        mock_standard_user(client, browse_files[0].consignment.series.body.Name)
        sorting_orders = {"series": "asc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="browse",
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 6

        expected_results = [
            (
                browse_files[19].consignment.series.body.BodyId,
                browse_files[19].consignment.series.body.Name,
                browse_files[19].consignment.series.SeriesId,
                browse_files[19].consignment.series.Name,
                "21/09/2023",
                2,
                6,
            ),
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
                "07/02/2023",
                2,
                3,
            ),
            (
                browse_files[13].consignment.series.body.BodyId,
                browse_files[13].consignment.series.body.Name,
                browse_files[13].consignment.series.SeriesId,
                browse_files[13].consignment.series.Name,
                "03/08/2023",
                2,
                6,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "26/04/2023",
                2,
                7,
            ),
            (
                browse_files[25].consignment.series.body.BodyId,
                browse_files[25].consignment.series.body.Name,
                browse_files[25].consignment.series.SeriesId,
                browse_files[25].consignment.series.Name,
                "14/10/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_series_sorting_z_to_a(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'browse' and
            sort by 'series' descending
        Then it returns a Paginate object returning the first 5 items
            ordered by series name alphabetically in descending order (Z to A)
        """

        mock_standard_user(client, browse_files[0].consignment.series.body.Name)
        sorting_orders = {"series": "desc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="browse",
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 6

        expected_results = [
            (
                browse_files[10].consignment.series.body.BodyId,
                browse_files[10].consignment.series.body.Name,
                browse_files[10].consignment.series.SeriesId,
                browse_files[10].consignment.series.Name,
                "17/06/2023",
                2,
                3,
            ),
            (
                browse_files[25].consignment.series.body.BodyId,
                browse_files[25].consignment.series.body.Name,
                browse_files[25].consignment.series.SeriesId,
                browse_files[25].consignment.series.Name,
                "14/10/2023",
                1,
                2,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "26/04/2023",
                2,
                7,
            ),
            (
                browse_files[13].consignment.series.body.BodyId,
                browse_files[13].consignment.series.body.Name,
                browse_files[13].consignment.series.SeriesId,
                browse_files[13].consignment.series.Name,
                "03/08/2023",
                2,
                6,
            ),
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
                "07/02/2023",
                2,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_date_last_transferred_sorting_oldest_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'browse' and
            sort by 'date last transferred' ascending
        Then it returns a Paginate object returning the first 5 items
            ordered by consignment transfer complete date in ascending order (oldest first)
        """

        mock_standard_user(client, browse_files[0].consignment.series.body.Name)
        sorting_orders = {"last_record_transferred": "asc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="browse",
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 6

        expected_results = [
            (
                browse_files[0].consignment.series.body.BodyId,
                browse_files[0].consignment.series.body.Name,
                browse_files[0].consignment.series.SeriesId,
                browse_files[0].consignment.series.Name,
                "07/02/2023",
                2,
                3,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "26/04/2023",
                2,
                7,
            ),
            (
                browse_files[10].consignment.series.body.BodyId,
                browse_files[10].consignment.series.body.Name,
                browse_files[10].consignment.series.SeriesId,
                browse_files[10].consignment.series.Name,
                "17/06/2023",
                2,
                3,
            ),
            (
                browse_files[13].consignment.series.body.BodyId,
                browse_files[13].consignment.series.body.Name,
                browse_files[13].consignment.series.SeriesId,
                browse_files[13].consignment.series.Name,
                "03/08/2023",
                2,
                6,
            ),
            (
                browse_files[19].consignment.series.body.BodyId,
                browse_files[19].consignment.series.body.Name,
                browse_files[19].consignment.series.SeriesId,
                browse_files[19].consignment.series.Name,
                "21/09/2023",
                2,
                6,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_with_date_last_transferred_sorting_most_recent_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'browse' and
            sort by 'date last transferred' descending
        Then it returns a Paginate object returning the first 5 items
            ordered by consignment transfer complete date in descending order (most recent first)
        """

        mock_standard_user(client, browse_files[0].consignment.series.body.Name)
        sorting_orders = {"last_record_transferred": "desc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="browse",
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 6

        expected_results = [
            (
                browse_files[25].consignment.series.body.BodyId,
                browse_files[25].consignment.series.body.Name,
                browse_files[25].consignment.series.SeriesId,
                browse_files[25].consignment.series.Name,
                "14/10/2023",
                1,
                2,
            ),
            (
                browse_files[19].consignment.series.body.BodyId,
                browse_files[19].consignment.series.body.Name,
                browse_files[19].consignment.series.SeriesId,
                browse_files[19].consignment.series.Name,
                "21/09/2023",
                2,
                6,
            ),
            (
                browse_files[13].consignment.series.body.BodyId,
                browse_files[13].consignment.series.body.Name,
                browse_files[13].consignment.series.SeriesId,
                browse_files[13].consignment.series.Name,
                "03/08/2023",
                2,
                6,
            ),
            (
                browse_files[10].consignment.series.body.BodyId,
                browse_files[10].consignment.series.body.Name,
                browse_files[10].consignment.series.SeriesId,
                browse_files[10].consignment.series.Name,
                "17/06/2023",
                2,
                3,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "26/04/2023",
                2,
                7,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results


class TestBrowseTransferringBody:
    def test_browse_transferring_body_without_filter(
        self, client, mock_standard_user, browse_transferring_body_files
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'transferring body' and
            without any filter values
        Then it returns a Pagination object with 3 total results
            for the specific transferring body
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            transferring_body_id=transferring_body_id,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                browse_transferring_body_files[
                    0
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[0].consignment.series.body.Name,
                browse_transferring_body_files[0].consignment.series.SeriesId,
                browse_transferring_body_files[0].consignment.series.Name,
                "14/10/2023",
                1,
                1,
            ),
            (
                browse_transferring_body_files[
                    2
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[2].consignment.series.body.Name,
                browse_transferring_body_files[2].consignment.series.SeriesId,
                browse_transferring_body_files[2].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
            (
                browse_transferring_body_files[
                    4
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[4].consignment.series.body.Name,
                browse_transferring_body_files[4].consignment.series.SeriesId,
                browse_transferring_body_files[4].consignment.series.Name,
                "07/07/2023",
                1,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_series_filter(
        self, client, mock_standard_user, browse_transferring_body_files
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with the series filter
        Then it returns a Pagination object with 1 total results corresponding to the
            series which match to the filter value
            for the specific transferring body
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        filters = {"series": "second_series"}
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
                browse_transferring_body_files[
                    2
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[2].consignment.series.body.Name,
                browse_transferring_body_files[2].consignment.series.SeriesId,
                browse_transferring_body_files[2].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_series_filter_wildcard_character(
        self, client, mock_standard_user, browse_transferring_body_files
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with the series filter
        Then it returns a Pagination object with 1 total results corresponding to the
            series which match to the filter value
            for the specific transferring body
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        filters = {"series": "t"}
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
                browse_transferring_body_files[
                    0
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[0].consignment.series.body.Name,
                browse_transferring_body_files[0].consignment.series.SeriesId,
                browse_transferring_body_files[0].consignment.series.Name,
                "14/10/2023",
                1,
                1,
            ),
            (
                browse_transferring_body_files[
                    4
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[4].consignment.series.body.Name,
                browse_transferring_body_files[4].consignment.series.SeriesId,
                browse_transferring_body_files[4].consignment.series.Name,
                "07/07/2023",
                1,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_date_consignment_transferred_filter_using_date_from_option(
        self, client, mock_standard_user, browse_transferring_body_files
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with date from filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is greater than or equal to the date from value
            for the specific transferring body
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        filters = {"date_range": {"date_from": "10/10/2023"}}
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
                browse_transferring_body_files[
                    0
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[0].consignment.series.body.Name,
                browse_transferring_body_files[0].consignment.series.SeriesId,
                browse_transferring_body_files[0].consignment.series.Name,
                "14/10/2023",
                1,
                1,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_date_consignment_transferred_filter_using_date_to_option(
        self, client, mock_standard_user, browse_transferring_body_files
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with date to filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date which is less than or equal to the date to value
            for the specific transferring body
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        filters = {"date_range": {"date_to": "30/03/2023"}}
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
                browse_transferring_body_files[
                    2
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[2].consignment.series.body.Name,
                browse_transferring_body_files[2].consignment.series.SeriesId,
                browse_transferring_body_files[2].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_date_consignment_transferred_filter_using_date_from_and_date_to_option(
        self, client, mock_standard_user, browse_transferring_body_files
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with date range (date from and date to) filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date between date from and date to value
            for the specific transferring body
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        filters = {
            "date_range": {"date_from": "01/03/2023", "date_to": "30/03/2023"}
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
                browse_transferring_body_files[
                    2
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[2].consignment.series.body.Name,
                browse_transferring_body_files[2].consignment.series.SeriesId,
                browse_transferring_body_files[2].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_date_consignment_transferred_filter_using_date_range_option_multiple_results(
        self, client, mock_standard_user, browse_transferring_body_files
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with date range (date from and date to) filter
        Then it returns a Pagination object with 2 total results corresponding to the
            consignment transfer complete date between date from and date to value
            for the specific transferring body
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        filters = {
            "date_range": {"date_from": "01/03/2023", "date_to": "30/07/2023"}
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
                browse_transferring_body_files[
                    2
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[2].consignment.series.body.Name,
                browse_transferring_body_files[2].consignment.series.SeriesId,
                browse_transferring_body_files[2].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
            (
                browse_transferring_body_files[
                    4
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[4].consignment.series.body.Name,
                browse_transferring_body_files[4].consignment.series.SeriesId,
                browse_transferring_body_files[4].consignment.series.Name,
                "07/07/2023",
                1,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_series_and_date_consignment_transferred_filter(
        self, client, mock_standard_user, browse_transferring_body_files
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function  with browse_view as 'transferring body' and
            with date range (date from and date to) filter
        Then it returns a Pagination object with 1 total results corresponding to the
            consignment transfer complete date between date from and date to value
            for the specific transferring body
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        filters = {
            "series": "third_series",
            "date_range": {"date_from": "01/07/2023", "date_to": "25/07/2023"},
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
                browse_transferring_body_files[
                    4
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[4].consignment.series.body.Name,
                browse_transferring_body_files[4].consignment.series.SeriesId,
                browse_transferring_body_files[4].consignment.series.Name,
                "07/07/2023",
                1,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_series_sorting_a_to_z(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'transferring body' and
            sort by 'series' ascending
        Then it returns a Paginate object returning 3 items
            for the specific transferring body
            ordered by series name alphabetically in ascending order (A to Z)
        """

        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )
        transferring_body = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        sorting_orders = {"series": "asc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            transferring_body_id=transferring_body,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                browse_transferring_body_files[
                    0
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[0].consignment.series.body.Name,
                browse_transferring_body_files[0].consignment.series.SeriesId,
                browse_transferring_body_files[0].consignment.series.Name,
                "14/10/2023",
                1,
                1,
            ),
            (
                browse_transferring_body_files[
                    2
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[2].consignment.series.body.Name,
                browse_transferring_body_files[2].consignment.series.SeriesId,
                browse_transferring_body_files[2].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
            (
                browse_transferring_body_files[
                    4
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[4].consignment.series.body.Name,
                browse_transferring_body_files[4].consignment.series.SeriesId,
                browse_transferring_body_files[4].consignment.series.Name,
                "07/07/2023",
                1,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_series_sorting_z_to_a(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'transferring body' and
            sort by 'series' descending
        Then it returns a Paginate object returning 3 items
            for the specific transferring body
            ordered by series name alphabetically in descending order (Z to A)
        """

        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )
        transferring_body = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        sorting_orders = {"series": "desc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            transferring_body_id=transferring_body,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                browse_transferring_body_files[
                    4
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[4].consignment.series.body.Name,
                browse_transferring_body_files[4].consignment.series.SeriesId,
                browse_transferring_body_files[4].consignment.series.Name,
                "07/07/2023",
                1,
                3,
            ),
            (
                browse_transferring_body_files[
                    2
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[2].consignment.series.body.Name,
                browse_transferring_body_files[2].consignment.series.SeriesId,
                browse_transferring_body_files[2].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
            (
                browse_transferring_body_files[
                    0
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[0].consignment.series.body.Name,
                browse_transferring_body_files[0].consignment.series.SeriesId,
                browse_transferring_body_files[0].consignment.series.Name,
                "14/10/2023",
                1,
                1,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_date_last_transferred_sorting_oldest_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'transferring body' and
            sort by 'date last transferred' ascending
        Then it returns a Paginate object returning 3 items
            for the specific transferring body
            ordered by consignment transfer complete date in ascending order (oldest first)
        """

        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )
        transferring_body = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        sorting_orders = {"last_record_transferred": "asc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            transferring_body_id=transferring_body,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                browse_transferring_body_files[
                    2
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[2].consignment.series.body.Name,
                browse_transferring_body_files[2].consignment.series.SeriesId,
                browse_transferring_body_files[2].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
            (
                browse_transferring_body_files[
                    4
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[4].consignment.series.body.Name,
                browse_transferring_body_files[4].consignment.series.SeriesId,
                browse_transferring_body_files[4].consignment.series.Name,
                "07/07/2023",
                1,
                3,
            ),
            (
                browse_transferring_body_files[
                    0
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[0].consignment.series.body.Name,
                browse_transferring_body_files[0].consignment.series.SeriesId,
                browse_transferring_body_files[0].consignment.series.Name,
                "14/10/2023",
                1,
                1,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_date_last_transferred_sorting_most_recent_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'transferring body' and
            sort by 'date last transferred' descending
        Then it returns a Paginate object returning 3 items
            for the specific transferring body
            ordered by consignment transfer complete date in descending order (most recent first)
        """

        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )
        transferring_body = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        sorting_orders = {"last_record_transferred": "desc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            transferring_body_id=transferring_body,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                browse_transferring_body_files[
                    0
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[0].consignment.series.body.Name,
                browse_transferring_body_files[0].consignment.series.SeriesId,
                browse_transferring_body_files[0].consignment.series.Name,
                "14/10/2023",
                1,
                1,
            ),
            (
                browse_transferring_body_files[
                    4
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[4].consignment.series.body.Name,
                browse_transferring_body_files[4].consignment.series.SeriesId,
                browse_transferring_body_files[4].consignment.series.Name,
                "07/07/2023",
                1,
                3,
            ),
            (
                browse_transferring_body_files[
                    2
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[2].consignment.series.body.Name,
                browse_transferring_body_files[2].consignment.series.SeriesId,
                browse_transferring_body_files[2].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_records_held_sorting_least_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given 6 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'transferring body' and
            sort by records held in consignment ascending
        Then it returns a Paginate object returning 3 items
            for the specific transferring body
            ordered by records held in consignment count in ascending order (least first)
        """

        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )
        transferring_body = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        sorting_orders = {"records_held": "asc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            transferring_body_id=transferring_body,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                browse_transferring_body_files[
                    0
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[0].consignment.series.body.Name,
                browse_transferring_body_files[0].consignment.series.SeriesId,
                browse_transferring_body_files[0].consignment.series.Name,
                "14/10/2023",
                1,
                1,
            ),
            (
                browse_transferring_body_files[
                    2
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[2].consignment.series.body.Name,
                browse_transferring_body_files[2].consignment.series.SeriesId,
                browse_transferring_body_files[2].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
            (
                browse_transferring_body_files[
                    4
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[4].consignment.series.body.Name,
                browse_transferring_body_files[4].consignment.series.SeriesId,
                browse_transferring_body_files[4].consignment.series.Name,
                "07/07/2023",
                1,
                3,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_transferring_body_with_records_held_sorting_most_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given 5 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'transferring body' and
            sort by records held in consignment descending
        Then it returns a Paginate object returning 3 items
            for the specific transferring body
            ordered by records held in consignment count in descending order (most first)
        """

        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )
        transferring_body = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        sorting_orders = {"records_held": "desc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            transferring_body_id=transferring_body,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                browse_transferring_body_files[
                    4
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[4].consignment.series.body.Name,
                browse_transferring_body_files[4].consignment.series.SeriesId,
                browse_transferring_body_files[4].consignment.series.Name,
                "07/07/2023",
                1,
                3,
            ),
            (
                browse_transferring_body_files[
                    2
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[2].consignment.series.body.Name,
                browse_transferring_body_files[2].consignment.series.SeriesId,
                browse_transferring_body_files[2].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
            (
                browse_transferring_body_files[
                    0
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[0].consignment.series.body.Name,
                browse_transferring_body_files[0].consignment.series.SeriesId,
                browse_transferring_body_files[0].consignment.series.Name,
                "14/10/2023",
                1,
                1,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results


class TestBrowseSeries:
    def test_browse_series_without_filter(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series'
        Then it returns a Paginate object returning the first 2 items
            for a specific series
            ordered by transferring body, series and consignment reference
        """
        mock_standard_user(client, browse_files[6].consignment.series.body.Name)
        series_id = browse_files[6].consignment.series.SeriesId

        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[6].consignment.series.body.BodyId,
                browse_files[6].consignment.series.body.Name,
                browse_files[6].consignment.series.SeriesId,
                browse_files[6].consignment.series.Name,
                "26/04/2023",
                4,
                browse_files[6].consignment.ConsignmentId,
                browse_files[6].consignment.ConsignmentReference,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "15/03/2023",
                3,
                browse_files[3].consignment.ConsignmentId,
                browse_files[3].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_date_consignment_transferred_filter_using_date_from_option(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            'date from' as filter
        Then it returns a Paginate object returning the first 1 item
            for a specific series
            consignment transfer complete date which is greater than or equal to the date from value
        """
        mock_standard_user(client, browse_files[6].consignment.series.body.Name)
        series_id = browse_files[6].consignment.series.SeriesId

        filters = {"date_range": {"date_from": "20/04/2023"}}
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
                browse_files[6].consignment.series.body.BodyId,
                browse_files[6].consignment.series.body.Name,
                browse_files[6].consignment.series.SeriesId,
                browse_files[6].consignment.series.Name,
                "26/04/2023",
                4,
                browse_files[6].consignment.ConsignmentId,
                browse_files[6].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_date_consignment_transferred_filter_using_date_to_option(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            'date to' as filter
        Then it returns a Paginate object returning the first 1 item
            for a specific series
            consignment transfer complete date which is less than or equal to the date to value
        """
        mock_standard_user(client, browse_files[6].consignment.series.body.Name)
        series_id = browse_files[6].consignment.series.SeriesId

        filters = {"date_range": {"date_to": "30/03/2023"}}
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
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "15/03/2023",
                3,
                browse_files[3].consignment.ConsignmentId,
                browse_files[3].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_date_consignment_transferred_filter_using_date_from_and_date_to_option(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            'date from' and 'date to' as filter
        Then it returns a Paginate object returning the first 1 item
            for a specific series
            consignment transfer complete date which is greater than or equal to date from
            and less than or equal to the date to value
        """
        mock_standard_user(client, browse_files[6].consignment.series.body.Name)
        series_id = browse_files[6].consignment.series.SeriesId

        filters = {
            "date_range": {"date_from": "01/03/2023", "date_to": "30/03/2023"}
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
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "15/03/2023",
                3,
                browse_files[3].consignment.ConsignmentId,
                browse_files[3].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_date_consignment_transferred_filter_using_date_from_and_date_to_option_no_result(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            'date from' and 'date to' as filter
        Then if date range not matched to any records
            it returns empty list containing multiple dictionary
        """
        mock_standard_user(client, browse_files[6].consignment.series.body.Name)
        series_id = browse_files[6].consignment.series.SeriesId

        filters = {
            "date_range": {"date_from": "01/02/2023", "date_to": "28/02/2023"}
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
            filters=filters,
        )

        assert pagination_object.total == 0

    def test_browse_series_with_date_last_transferred_sorting_oldest_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            sort by 'date last transferred' ascending
        Then it returns a Paginate object returning the first 2 items
            for a specific series
            ordered by consignment transfer complete date in ascending order (oldest first)
        """
        mock_standard_user(client, browse_files[6].consignment.series.body.Name)
        series_id = browse_files[6].consignment.series.SeriesId

        sorting_orders = {"last_record_transferred": "asc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "15/03/2023",
                3,
                browse_files[3].consignment.ConsignmentId,
                browse_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_files[6].consignment.series.body.BodyId,
                browse_files[6].consignment.series.body.Name,
                browse_files[6].consignment.series.SeriesId,
                browse_files[6].consignment.series.Name,
                "26/04/2023",
                4,
                browse_files[6].consignment.ConsignmentId,
                browse_files[6].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_date_last_transferred_sorting_most_recent_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            sort by 'date last transferred' descending
        Then it returns a Paginate object returning the first 2 items
            for a specific series
            ordered by consignment transfer complete date in descending order (most recent first)
        """
        mock_standard_user(client, browse_files[6].consignment.series.body.Name)
        series_id = browse_files[6].consignment.series.SeriesId

        sorting_orders = {"last_record_transferred": "desc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[6].consignment.series.body.BodyId,
                browse_files[6].consignment.series.body.Name,
                browse_files[6].consignment.series.SeriesId,
                browse_files[6].consignment.series.Name,
                "26/04/2023",
                4,
                browse_files[6].consignment.ConsignmentId,
                browse_files[6].consignment.ConsignmentReference,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "15/03/2023",
                3,
                browse_files[3].consignment.ConsignmentId,
                browse_files[3].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_consignment_reference_sorting_most_recent_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            sort by 'consignment reference' descending
        Then it returns a Paginate object returning the first 2 items
            for a specific series
            ordered by consignment reference in reverse alphabetic order (most recent first)
        """
        mock_standard_user(client, browse_files[6].consignment.series.body.Name)
        series_id = browse_files[6].consignment.series.SeriesId

        sorting_orders = {"consignment_reference": "desc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "15/03/2023",
                3,
                browse_files[3].consignment.ConsignmentId,
                browse_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_files[6].consignment.series.body.BodyId,
                browse_files[6].consignment.series.body.Name,
                browse_files[6].consignment.series.SeriesId,
                browse_files[6].consignment.series.Name,
                "26/04/2023",
                4,
                browse_files[6].consignment.ConsignmentId,
                browse_files[6].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_consignment_reference_sorting_oldest_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            sort by 'consignment reference' ascending
        Then it returns a Paginate object returning the first 2 items
            for a specific series
            ordered by consignment reference in alphabetic order (oldest first)
        """
        mock_standard_user(client, browse_files[6].consignment.series.body.Name)
        series_id = browse_files[6].consignment.series.SeriesId

        sorting_orders = {"consignment_reference": "asc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[6].consignment.series.body.BodyId,
                browse_files[6].consignment.series.body.Name,
                browse_files[6].consignment.series.SeriesId,
                browse_files[6].consignment.series.Name,
                "26/04/2023",
                4,
                browse_files[6].consignment.ConsignmentId,
                browse_files[6].consignment.ConsignmentReference,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "15/03/2023",
                3,
                browse_files[3].consignment.ConsignmentId,
                browse_files[3].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_records_held_sorting_least_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            sort by 'records held in consignment' ascending
        Then it returns a Paginate object returning the first 2 items
            for a specific series
            ordered by records held in consignment count in ascending order (least first)
        """
        mock_standard_user(client, browse_files[6].consignment.series.body.Name)
        series_id = browse_files[6].consignment.series.SeriesId

        sorting_orders = {"records_held": "asc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "15/03/2023",
                3,
                browse_files[3].consignment.ConsignmentId,
                browse_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_files[6].consignment.series.body.BodyId,
                browse_files[6].consignment.series.body.Name,
                browse_files[6].consignment.series.SeriesId,
                browse_files[6].consignment.series.Name,
                "26/04/2023",
                4,
                browse_files[6].consignment.ConsignmentId,
                browse_files[6].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_series_with_records_held_sorting_most_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given 27 file objects with all file type as 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with browse_view as 'series' and
            sort by 'records held in consignment' descending
        Then it returns a Paginate object returning the first 2 items
            for a specific series
            ordered by records held in consignment count in descending order (most first)
        """
        mock_standard_user(client, browse_files[6].consignment.series.body.Name)
        series_id = browse_files[6].consignment.series.SeriesId

        sorting_orders = {"records_held": "desc"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="series",
            series_id=series_id,
            sorting_orders=sorting_orders,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_files[6].consignment.series.body.BodyId,
                browse_files[6].consignment.series.body.Name,
                browse_files[6].consignment.series.SeriesId,
                browse_files[6].consignment.series.Name,
                "26/04/2023",
                4,
                browse_files[6].consignment.ConsignmentId,
                browse_files[6].consignment.ConsignmentReference,
            ),
            (
                browse_files[3].consignment.series.body.BodyId,
                browse_files[3].consignment.series.body.Name,
                browse_files[3].consignment.series.SeriesId,
                browse_files[3].consignment.series.Name,
                "15/03/2023",
                3,
                browse_files[3].consignment.ConsignmentId,
                browse_files[3].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results


class TestBrowseConsignment:
    def test_browse_consignment_without_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
        Then it returns a Pagination object with 5 total results corresponding to the
            five files, ordered by their names and with the expected metadata values
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
        )

        assert pagination_object.total == 5

        expected_results = [
            (
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                "20/05/2023",
                "Open",
                None,
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                "12/04/2023",
                "Closed",
                "12/04/2023",
                browse_consignment_files[3].consignment.series.body.BodyId,
                browse_consignment_files[3].consignment.series.body.Name,
                browse_consignment_files[3].consignment.series.SeriesId,
                browse_consignment_files[3].consignment.series.Name,
                browse_consignment_files[3].consignment.ConsignmentId,
                browse_consignment_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                "Open",
                None,
                browse_consignment_files[1].consignment.series.body.BodyId,
                browse_consignment_files[1].consignment.series.body.Name,
                browse_consignment_files[1].consignment.series.SeriesId,
                browse_consignment_files[1].consignment.series.Name,
                browse_consignment_files[1].consignment.ConsignmentId,
                browse_consignment_files[1].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[2].FileId,
                "third_file.docx",
                "10/03/2023",
                "Closed",
                "10/03/2023",
                browse_consignment_files[2].consignment.series.body.BodyId,
                browse_consignment_files[2].consignment.series.body.Name,
                browse_consignment_files[2].consignment.series.SeriesId,
                browse_consignment_files[2].consignment.series.Name,
                browse_consignment_files[2].consignment.ConsignmentId,
                browse_consignment_files[2].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_record_status_open_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and record status filter as 'Open'
        Then it returns a Pagination object with 2 total results corresponding to the
            closure_type file metadata value set to 'Open' ( 2 files),
            ordered by their names and with the expected metadata values
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        filters = {"record_status": "open"}

        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            filters=filters,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                "20/05/2023",
                "Open",
                None,
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                "Open",
                None,
                browse_consignment_files[1].consignment.series.body.BodyId,
                browse_consignment_files[1].consignment.series.body.Name,
                browse_consignment_files[1].consignment.series.SeriesId,
                browse_consignment_files[1].consignment.series.Name,
                browse_consignment_files[1].consignment.ConsignmentId,
                browse_consignment_files[1].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_record_status_closed_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and record status filter as 'Closed'
        Then it returns a Pagination object with 3 total results corresponding to the
            closure_type file metadata value set to 'Closed' ( 3 files),
            ordered by their names and with the expected metadata values
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        filters = {"record_status": "closed"}

        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            filters=filters,
        )

        assert pagination_object.total == 3

        expected_results = [
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                "12/04/2023",
                "Closed",
                "12/04/2023",
                browse_consignment_files[3].consignment.series.body.BodyId,
                browse_consignment_files[3].consignment.series.body.Name,
                browse_consignment_files[3].consignment.series.SeriesId,
                browse_consignment_files[3].consignment.series.Name,
                browse_consignment_files[3].consignment.ConsignmentId,
                browse_consignment_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[2].FileId,
                "third_file.docx",
                "10/03/2023",
                "Closed",
                "10/03/2023",
                browse_consignment_files[2].consignment.series.body.BodyId,
                browse_consignment_files[2].consignment.series.body.Name,
                browse_consignment_files[2].consignment.series.SeriesId,
                browse_consignment_files[2].consignment.series.Name,
                browse_consignment_files[2].consignment.ConsignmentId,
                browse_consignment_files[2].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_record_status_all_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and record status filter as 'all'
        Then it returns a Pagination object with 3 total results corresponding to the
            closure_type file metadata value set to 'Open' or 'Closed' ( 3 files),
            ordered by their names and with the expected metadata values
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        filters = {"record_status": "all"}
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            filters=filters,
        )

        assert pagination_object.total == 5

        expected_results = [
            (
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                "20/05/2023",
                "Open",
                None,
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                "12/04/2023",
                "Closed",
                "12/04/2023",
                browse_consignment_files[3].consignment.series.body.BodyId,
                browse_consignment_files[3].consignment.series.body.Name,
                browse_consignment_files[3].consignment.series.SeriesId,
                browse_consignment_files[3].consignment.series.Name,
                browse_consignment_files[3].consignment.ConsignmentId,
                browse_consignment_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                "Open",
                None,
                browse_consignment_files[1].consignment.series.body.BodyId,
                browse_consignment_files[1].consignment.series.body.Name,
                browse_consignment_files[1].consignment.series.SeriesId,
                browse_consignment_files[1].consignment.series.Name,
                browse_consignment_files[1].consignment.ConsignmentId,
                browse_consignment_files[1].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[2].FileId,
                "third_file.docx",
                "10/03/2023",
                "Closed",
                "10/03/2023",
                browse_consignment_files[2].consignment.series.body.BodyId,
                browse_consignment_files[2].consignment.series.body.Name,
                browse_consignment_files[2].consignment.series.SeriesId,
                browse_consignment_files[2].consignment.series.Name,
                browse_consignment_files[2].consignment.ConsignmentId,
                browse_consignment_files[2].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_date_from_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and date_from filter in a data range
        Then it returns a Pagination object with 2 total results corresponding to the
            date_last_modified greater than or equal date_from filter value ( 2 files),
            ordered by their names and with the expected metadata values
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        filters = {
            "date_range": {"date_from": "10/04/2023"},
            "date_filter_field": "date_last_modified",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            filters=filters,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                "20/05/2023",
                "Open",
                None,
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                "12/04/2023",
                "Closed",
                "12/04/2023",
                browse_consignment_files[3].consignment.series.body.BodyId,
                browse_consignment_files[3].consignment.series.body.Name,
                browse_consignment_files[3].consignment.series.SeriesId,
                browse_consignment_files[3].consignment.series.Name,
                browse_consignment_files[3].consignment.ConsignmentId,
                browse_consignment_files[3].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_date_to_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and date_to filter in a data range
        Then it returns a Pagination object with 2 total results corresponding to the
            date_last_modified less than or equal date_from filter value ( 2 files),
            ordered by their names and with the expected metadata values
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        filters = {
            "date_range": {"date_to": "28/02/2023"},
            "date_filter_field": "date_last_modified",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            filters=filters,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                "Open",
                None,
                browse_consignment_files[1].consignment.series.body.BodyId,
                browse_consignment_files[1].consignment.series.body.Name,
                browse_consignment_files[1].consignment.series.SeriesId,
                browse_consignment_files[1].consignment.series.Name,
                browse_consignment_files[1].consignment.ConsignmentId,
                browse_consignment_files[1].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_date_from_and_date_to_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and date_from and date_to filter in a date range
        Then it returns a Pagination object with 2 total results corresponding to the
            date_last_modified greater than or equal to date_from filter value and
            date_last_modified less than or equal date_to filter value ( 2 file),
            ordered by their names and with the expected metadata values
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        filters = {
            "date_range": {"date_from": "01/01/2023", "date_to": "28/02/2023"},
            "date_filter_field": "date_last_modified",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            filters=filters,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                "Open",
                None,
                browse_consignment_files[1].consignment.series.body.BodyId,
                browse_consignment_files[1].consignment.series.body.Name,
                browse_consignment_files[1].consignment.series.SeriesId,
                browse_consignment_files[1].consignment.series.Name,
                browse_consignment_files[1].consignment.ConsignmentId,
                browse_consignment_files[1].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_record_status_and_date_range_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and record_status filter as 'Closed'
            and date_range between from and to date
        Then it returns a Pagination object with 2 total results corresponding to the
            closure_type metadata value set to 'Closed' and
            date_last_modified metadata value match between date_from and date_to filter (2 file),
            ordered by their names and with the expected metadata values
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        filters = {
            "record_status": "Closed",
            "date_range": {"date_from": "01/01/2023", "date_to": "15/03/2023"},
            "date_filter_field": "date_last_modified",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            filters=filters,
        )

        assert pagination_object.total == 2

        expected_results = [
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[2].FileId,
                "third_file.docx",
                "10/03/2023",
                "Closed",
                "10/03/2023",
                browse_consignment_files[2].consignment.series.body.BodyId,
                browse_consignment_files[2].consignment.series.body.Name,
                browse_consignment_files[2].consignment.series.SeriesId,
                browse_consignment_files[2].consignment.series.Name,
                browse_consignment_files[2].consignment.ConsignmentId,
                browse_consignment_files[2].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_record_status_sorting_closed_first(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and record_status as sorting in ascending
        Then it returns a Pagination object with 5 total results
            ordered by their closure_type 'Closed' first and then 'Open' in ascending orders
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        sorting_orders = {
            "closure_type": "asc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            sorting_orders=sorting_orders,
        )
        assert pagination_object.total == 5

        expected_results = [
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                "12/04/2023",
                "Closed",
                "12/04/2023",
                browse_consignment_files[3].consignment.series.body.BodyId,
                browse_consignment_files[3].consignment.series.body.Name,
                browse_consignment_files[3].consignment.series.SeriesId,
                browse_consignment_files[3].consignment.series.Name,
                browse_consignment_files[3].consignment.ConsignmentId,
                browse_consignment_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[2].FileId,
                "third_file.docx",
                "10/03/2023",
                "Closed",
                "10/03/2023",
                browse_consignment_files[2].consignment.series.body.BodyId,
                browse_consignment_files[2].consignment.series.body.Name,
                browse_consignment_files[2].consignment.series.SeriesId,
                browse_consignment_files[2].consignment.series.Name,
                browse_consignment_files[2].consignment.ConsignmentId,
                browse_consignment_files[2].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                "20/05/2023",
                "Open",
                None,
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                "Open",
                None,
                browse_consignment_files[1].consignment.series.body.BodyId,
                browse_consignment_files[1].consignment.series.body.Name,
                browse_consignment_files[1].consignment.series.SeriesId,
                browse_consignment_files[1].consignment.series.Name,
                browse_consignment_files[1].consignment.ConsignmentId,
                browse_consignment_files[1].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_record_status_sorting_open_first(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and record_status as sorting in descending
        Then it returns a Pagination object with 5 total results
            ordered by their closure_type 'Open' first and then 'Closed' in descending orders
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        sorting_orders = {
            "closure_type": "desc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            sorting_orders=sorting_orders,
        )
        assert pagination_object.total == 5

        expected_results = [
            (
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                "20/05/2023",
                "Open",
                None,
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                "Open",
                None,
                browse_consignment_files[1].consignment.series.body.BodyId,
                browse_consignment_files[1].consignment.series.body.Name,
                browse_consignment_files[1].consignment.series.SeriesId,
                browse_consignment_files[1].consignment.series.Name,
                browse_consignment_files[1].consignment.ConsignmentId,
                browse_consignment_files[1].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                "12/04/2023",
                "Closed",
                "12/04/2023",
                browse_consignment_files[3].consignment.series.body.BodyId,
                browse_consignment_files[3].consignment.series.body.Name,
                browse_consignment_files[3].consignment.series.SeriesId,
                browse_consignment_files[3].consignment.series.Name,
                browse_consignment_files[3].consignment.ConsignmentId,
                browse_consignment_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[2].FileId,
                "third_file.docx",
                "10/03/2023",
                "Closed",
                "10/03/2023",
                browse_consignment_files[2].consignment.series.body.BodyId,
                browse_consignment_files[2].consignment.series.body.Name,
                browse_consignment_files[2].consignment.series.SeriesId,
                browse_consignment_files[2].consignment.series.Name,
                browse_consignment_files[2].consignment.ConsignmentId,
                browse_consignment_files[2].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_file_name_sorting_a_to_z(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and file_name as sorting in ascending
        Then it returns a Pagination object with 5 total results
            ordered by their file name in ascending orders (A to Z)
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        sorting_orders = {
            "file_name": "asc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            sorting_orders=sorting_orders,
        )
        assert pagination_object.total == 5

        expected_results = [
            (
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                "20/05/2023",
                "Open",
                None,
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                "12/04/2023",
                "Closed",
                "12/04/2023",
                browse_consignment_files[3].consignment.series.body.BodyId,
                browse_consignment_files[3].consignment.series.body.Name,
                browse_consignment_files[3].consignment.series.SeriesId,
                browse_consignment_files[3].consignment.series.Name,
                browse_consignment_files[3].consignment.ConsignmentId,
                browse_consignment_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                "Open",
                None,
                browse_consignment_files[1].consignment.series.body.BodyId,
                browse_consignment_files[1].consignment.series.body.Name,
                browse_consignment_files[1].consignment.series.SeriesId,
                browse_consignment_files[1].consignment.series.Name,
                browse_consignment_files[1].consignment.ConsignmentId,
                browse_consignment_files[1].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[2].FileId,
                "third_file.docx",
                "10/03/2023",
                "Closed",
                "10/03/2023",
                browse_consignment_files[2].consignment.series.body.BodyId,
                browse_consignment_files[2].consignment.series.body.Name,
                browse_consignment_files[2].consignment.series.SeriesId,
                browse_consignment_files[2].consignment.series.Name,
                browse_consignment_files[2].consignment.ConsignmentId,
                browse_consignment_files[2].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_file_name_sorting_z_to_a(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and file_name as sorting in descending
        Then it returns a Pagination object with 5 total results
            ordered by their file name in descending order (Z to A)
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        sorting_orders = {
            "file_name": "desc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            sorting_orders=sorting_orders,
        )
        assert pagination_object.total == 5

        expected_results = [
            (
                browse_consignment_files[2].FileId,
                "third_file.docx",
                "10/03/2023",
                "Closed",
                "10/03/2023",
                browse_consignment_files[2].consignment.series.body.BodyId,
                browse_consignment_files[2].consignment.series.body.Name,
                browse_consignment_files[2].consignment.series.SeriesId,
                browse_consignment_files[2].consignment.series.Name,
                browse_consignment_files[2].consignment.ConsignmentId,
                browse_consignment_files[2].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                "Open",
                None,
                browse_consignment_files[1].consignment.series.body.BodyId,
                browse_consignment_files[1].consignment.series.body.Name,
                browse_consignment_files[1].consignment.series.SeriesId,
                browse_consignment_files[1].consignment.series.Name,
                browse_consignment_files[1].consignment.ConsignmentId,
                browse_consignment_files[1].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                "12/04/2023",
                "Closed",
                "12/04/2023",
                browse_consignment_files[3].consignment.series.body.BodyId,
                browse_consignment_files[3].consignment.series.body.Name,
                browse_consignment_files[3].consignment.series.SeriesId,
                browse_consignment_files[3].consignment.series.Name,
                browse_consignment_files[3].consignment.ConsignmentId,
                browse_consignment_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                "20/05/2023",
                "Open",
                None,
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_date_last_modified_sorting_oldest_first(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and sort by date last modified ascending
        Then it returns a Pagination object with 5 total results
            ordered by their date last modified as oldest first(ascending)
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        sorting_orders = {
            "date_last_modified": "asc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            sorting_orders=sorting_orders,
        )
        assert pagination_object.total == 5

        expected_results = [
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                "Open",
                None,
                browse_consignment_files[1].consignment.series.body.BodyId,
                browse_consignment_files[1].consignment.series.body.Name,
                browse_consignment_files[1].consignment.series.SeriesId,
                browse_consignment_files[1].consignment.series.Name,
                browse_consignment_files[1].consignment.ConsignmentId,
                browse_consignment_files[1].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[2].FileId,
                "third_file.docx",
                "10/03/2023",
                "Closed",
                "10/03/2023",
                browse_consignment_files[2].consignment.series.body.BodyId,
                browse_consignment_files[2].consignment.series.body.Name,
                browse_consignment_files[2].consignment.series.SeriesId,
                browse_consignment_files[2].consignment.series.Name,
                browse_consignment_files[2].consignment.ConsignmentId,
                browse_consignment_files[2].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                "12/04/2023",
                "Closed",
                "12/04/2023",
                browse_consignment_files[3].consignment.series.body.BodyId,
                browse_consignment_files[3].consignment.series.body.Name,
                browse_consignment_files[3].consignment.series.SeriesId,
                browse_consignment_files[3].consignment.series.Name,
                browse_consignment_files[3].consignment.ConsignmentId,
                browse_consignment_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                "20/05/2023",
                "Open",
                None,
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
            ),
        ]

        results = pagination_object.items

        assert results == expected_results

    def test_browse_consignment_with_date_last_modified_sorting_most_recent_first(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given five file objects with associated metadata part of 1 consignment,
            where 5 file types is 'file'
        And the session contains user info for a standard user with access to the consignment's
            associated transferring body
        When I call the 'browse_data' function with the consignment id
            and sort by date last modified descending
        Then it returns a Pagination object with 5 total results
            ordered by their date last modified as most recent first(descending)
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        sorting_orders = {
            "date_last_modified": "desc",
        }
        pagination_object = browse_data(
            page=1,
            per_page=per_page,
            browse_type="consignment",
            consignment_id=consignment_id,
            sorting_orders=sorting_orders,
        )
        assert pagination_object.total == 5

        expected_results = [
            (
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                "20/05/2023",
                "Open",
                None,
                browse_consignment_files[4].consignment.series.body.BodyId,
                browse_consignment_files[4].consignment.series.body.Name,
                browse_consignment_files[4].consignment.series.SeriesId,
                browse_consignment_files[4].consignment.series.Name,
                browse_consignment_files[4].consignment.ConsignmentId,
                browse_consignment_files[4].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                "12/04/2023",
                "Closed",
                "12/04/2023",
                browse_consignment_files[3].consignment.series.body.BodyId,
                browse_consignment_files[3].consignment.series.body.Name,
                browse_consignment_files[3].consignment.series.SeriesId,
                browse_consignment_files[3].consignment.series.Name,
                browse_consignment_files[3].consignment.ConsignmentId,
                browse_consignment_files[3].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[2].FileId,
                "third_file.docx",
                "10/03/2023",
                "Closed",
                "10/03/2023",
                browse_consignment_files[2].consignment.series.body.BodyId,
                browse_consignment_files[2].consignment.series.body.Name,
                browse_consignment_files[2].consignment.series.SeriesId,
                browse_consignment_files[2].consignment.series.Name,
                browse_consignment_files[2].consignment.ConsignmentId,
                browse_consignment_files[2].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[0].FileId,
                "first_file.docx",
                "25/02/2023",
                "Closed",
                "25/02/2023",
                browse_consignment_files[0].consignment.series.body.BodyId,
                browse_consignment_files[0].consignment.series.body.Name,
                browse_consignment_files[0].consignment.series.SeriesId,
                browse_consignment_files[0].consignment.series.Name,
                browse_consignment_files[0].consignment.ConsignmentId,
                browse_consignment_files[0].consignment.ConsignmentReference,
            ),
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                "Open",
                None,
                browse_consignment_files[1].consignment.series.body.BodyId,
                browse_consignment_files[1].consignment.series.body.Name,
                browse_consignment_files[1].consignment.series.SeriesId,
                browse_consignment_files[1].consignment.series.Name,
                browse_consignment_files[1].consignment.ConsignmentId,
                browse_consignment_files[1].consignment.ConsignmentReference,
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
                file=file,
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
            "consignment": file.consignment.ConsignmentReference,
            "consignment_id": file.ConsignmentId,
            "transferring_body": file.consignment.series.body.Name,
            "transferring_body_id": file.consignment.series.body.BodyId,
            "series": file.consignment.series.Name,
            "series_id": file.consignment.series.SeriesId,
        }

    def test_valid_uuid_returns_none_for_any_metadata(
        self, client: FlaskClient
    ):
        """
        Given a file with no associatedf file metadata,
        When get_file_metadata is called with its UUID,
        Then a dict of metadata for the file is returned
            and all the file metadata fields are None
        """
        file = FileFactory(
            FileName="test_file.txt",
            FilePath="data/content/test_file.txt",
            FileType="file",
        )

        assert get_file_metadata(file_id=file.FileId) == {
            "file_id": file.FileId,
            "file_name": "test_file.txt",
            "file_path": "data/content/test_file.txt",
            "status": None,
            "description": None,
            "date_last_modified": None,
            "held_by": None,
            "legal_status": None,
            "rights_copyright": None,
            "language": None,
            "consignment": file.consignment.ConsignmentReference,
            "consignment_id": file.ConsignmentId,
            "transferring_body": file.consignment.series.body.Name,
            "transferring_body_id": file.consignment.series.body.BodyId,
            "series": file.consignment.series.Name,
            "series_id": file.consignment.series.SeriesId,
        }
