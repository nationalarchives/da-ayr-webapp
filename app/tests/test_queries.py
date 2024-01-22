import uuid
from datetime import datetime

import pytest
import werkzeug
from flask.testing import FlaskClient

from app.main.db.queries import (
    browse_data,
    build_fuzzy_search_query,
    get_file_metadata,
)
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    FileMetadataFactory,
    SeriesFactory,
)
from app.tests.mock_database import create_multiple_test_records

per_page = 5


class TestFuzzySearch:
    @pytest.mark.parametrize(
        "file_metadata_property",
        [
            "Value",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_file_metadata_properties(
        self, client: FlaskClient, file_metadata_property
    ):
        """
        Given a query string that matches one of the parametrized file_metadata_property
            on a FileMetadata object in the database
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file is returned
        """
        file_metadata_property_map = {file_metadata_property: "foo"}
        file = FileFactory(FileType="file")
        FileMetadataFactory(file=file, **file_metadata_property_map)
        query_string = "foo"

        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    @pytest.mark.parametrize(
        "file_property",
        [
            "FileName",
            "FileReference",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_file_properties(
        self, client: FlaskClient, file_property
    ):
        """
        Given a query string that matches one of the parametrized file_property
            on a File object in the database
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file is returned
        """
        file_property_map = {file_property: "foo"}
        file = FileFactory(FileType="file", **file_property_map)
        query_string = "foo"

        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    @pytest.mark.parametrize(
        "consignment_property",
        [
            "ConsignmentReference",
            "ConsignmentType",
            "ContactName",
            "ContactEmail",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_consignment_properties(
        self, client: FlaskClient, consignment_property
    ):
        """
        Given a query string that matches one of the parametrized consignment_property
            on a Consignment object in the database with 1 file
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file in the Consignment is returned
        """
        consignment_property_map = {consignment_property: "foo"}
        file = FileFactory(
            FileType="file",
            consignment=ConsignmentFactory(**consignment_property_map),
        )
        query_string = "foo"

        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    @pytest.mark.parametrize(
        "consignment_date_property",
        [
            "TransferStartDatetime",
            "TransferCompleteDatetime",
            "ExportDatetime",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_consignment_date_properties(
        self, client: FlaskClient, consignment_date_property
    ):
        """
        Given a query string that matches one of the parametrized consignment_date_property
            on a Consignment object in the database with 1 file
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file in the Consignment is returned
        """
        consignment_date_property_map = {
            consignment_date_property: datetime(2022, 2, 18)
        }
        file = FileFactory(
            FileType="file",
            consignment=ConsignmentFactory(**consignment_date_property_map),
        )
        query_string = "18/02/2022"
        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    @pytest.mark.parametrize(
        "body_property",
        [
            "Name",
            "Description",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_body_properties(
        self, client: FlaskClient, body_property
    ):
        """
        Given a query string that matches one of the parametrized body_property
            on a Body object in the database with 1 file
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file in the Body is returned
        """
        body_property_map = {body_property: "foo"}
        file = FileFactory(
            FileType="file",
            consignment=ConsignmentFactory(
                series=SeriesFactory(body=BodyFactory(**body_property_map))
            ),
        )
        query_string = "foo"

        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    @pytest.mark.parametrize(
        "series_property",
        [
            "Name",
            "Description",
        ],
    )
    def test_build_fuzzy_search_query_with_results_matching_series_properties(
        self, client: FlaskClient, series_property
    ):
        """
        Given a query string that matches one of the parametrized series_property
            on a Series object in the database with 1 file
        When build_fuzzy_search_query is called with it and is executed
        Then a list containing 1 tuple with information for the corresponding
            file in the Body is returned
        """
        series_property_map = {series_property: "foo"}
        file = FileFactory(
            FileType="file",
            consignment=ConsignmentFactory(
                series=SeriesFactory(**series_property_map)
            ),
        )
        query_string = "foo"

        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == [
            (
                file.consignment.series.body.Name,
                file.consignment.series.Name,
                file.consignment.ConsignmentReference,
                file.FileName,
                file.consignment.series.body.BodyId,
                file.consignment.series.SeriesId,
            )
        ]

    def test_build_fuzzy_search_query_no_results(self, client: FlaskClient):
        """
        Given a query string that does not match any field in any file object
            in the database
        When fuzzy_search is called with it and is executed
        Then an empty list is returned
        """
        FileFactory(FileName="foo", FileType="file")
        query_string = "bar"
        query = build_fuzzy_search_query(query_string)
        results = query.all()
        assert results == []


class TestBrowse:
    def test_browse_without_filters(self, client: FlaskClient):
        """
        Given multiple File objects in the database
        When browse_data is called with page=2, per_page=5, browse_type='browse'
        Then it returns a Paginate object returning the first 5 items
            ordered by Body name then Series name
        """
        files = create_multiple_test_records()
        result = browse_data(page=1, per_page=5, browse_type="browse")

        assert result.items == [
            (
                files[0].consignment.series.body.BodyId,
                "test body1",
                files[0].consignment.series.SeriesId,
                "test series1",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[1].consignment.series.body.BodyId,
                "test body2",
                files[1].consignment.series.SeriesId,
                "test series2",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[9].consignment.series.body.BodyId,
                "testing body10",
                files[9].consignment.series.SeriesId,
                "test series10",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[10].consignment.series.body.BodyId,
                "testing body11",
                files[10].consignment.series.SeriesId,
                "test series11",
                "01/01/2023",
                1,
                2,
            ),
            (
                files[2].consignment.series.body.BodyId,
                "testing body3",
                files[2].consignment.series.SeriesId,
                "test series3",
                "01/01/2023",
                1,
                1,
            ),
        ]

    def test_browse_get_specific_page_results(self, client: FlaskClient):
        """
        Given multiple File objects in the database
        When browse_data is called with page=2, per_page=5, browse_type='browse'
        Then it returns a Paginate object returning the second 5 items
            ordered by Body name then Series name
        """
        files = create_multiple_test_records()

        result = browse_data(page=2, per_page=per_page, browse_type="browse")
        assert result.items == [
            (
                files[3].consignment.series.body.BodyId,
                "testing body4",
                files[3].consignment.series.SeriesId,
                "test series4",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[4].consignment.series.body.BodyId,
                "testing body5",
                files[4].consignment.series.SeriesId,
                "test series5",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[5].consignment.series.body.BodyId,
                "testing body6",
                files[5].consignment.series.SeriesId,
                "test series6",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[6].consignment.series.body.BodyId,
                "testing body7",
                files[6].consignment.series.SeriesId,
                "test series7",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[7].consignment.series.body.BodyId,
                "testing body8",
                files[7].consignment.series.SeriesId,
                "test series8",
                "15/02/2023",
                1,
                1,
            ),
        ]
        assert result.pages > 0
        assert result.has_next is True
        assert result.has_prev is True

    def test_browse_with_date_from_filter(self, client: FlaskClient):
        """
        Given multiple File objects in the database and consignment transfer complete date
            that matches all of them
        When browse_data is called with date_from
        Then it returns a list containing multiple dictionary for the matching record with
            expected fields
        """
        files = create_multiple_test_records()

        filters = {"date_range": {"date_from": "12/02/2023"}}
        result = browse_data(page=1, per_page=per_page, filters=filters)

        assert result.items == [
            (
                files[4].consignment.series.body.BodyId,
                "testing body5",
                files[4].consignment.series.SeriesId,
                "test series5",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[5].consignment.series.body.BodyId,
                "testing body6",
                files[5].consignment.series.SeriesId,
                "test series6",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[6].consignment.series.body.BodyId,
                "testing body7",
                files[6].consignment.series.SeriesId,
                "test series7",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[7].consignment.series.body.BodyId,
                "testing body8",
                files[7].consignment.series.SeriesId,
                "test series8",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[8].consignment.series.body.BodyId,
                "testing body9",
                files[8].consignment.series.SeriesId,
                "test series9",
                "15/02/2023",
                1,
                1,
            ),
        ]

    def test_browse_with_date_to_filter(self, client: FlaskClient):
        """
        Given multiple File objects in the database and consignment transfer complete date
            that matches all of them
        When browse_data is called with date_to
        Then it returns a list containing multiple dictionary for the matching record with
            expected fields
        """
        files = create_multiple_test_records()

        filters = {"date_range": {"date_to": "28/02/2023"}}
        result = browse_data(page=1, per_page=per_page, filters=filters)

        assert result.items == [
            (
                files[0].consignment.series.body.BodyId,
                "test body1",
                files[0].consignment.series.SeriesId,
                "test series1",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[1].consignment.series.body.BodyId,
                "test body2",
                files[1].consignment.series.SeriesId,
                "test series2",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[9].consignment.series.body.BodyId,
                "testing body10",
                files[9].consignment.series.SeriesId,
                "test series10",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[10].consignment.series.body.BodyId,
                "testing body11",
                files[10].consignment.series.SeriesId,
                "test series11",
                "01/01/2023",
                1,
                2,
            ),
            (
                files[2].consignment.series.body.BodyId,
                "testing body3",
                files[2].consignment.series.SeriesId,
                "test series3",
                "01/01/2023",
                1,
                1,
            ),
        ]

    def test_browse_with_date_from_and_to_filter(self, client: FlaskClient):
        """
        Given multiple File objects in the database and consignment transfer complete date
            that matches all of them
        When browse_data is called with date_from and date_to
        Then it returns a list containing multiple dictionary for the matching record with
            date in between the range
        """
        files = create_multiple_test_records()

        filters = {
            "date_range": {"date_from": "01/02/2023", "date_to": "28/02/2023"}
        }
        result = browse_data(page=1, per_page=per_page, filters=filters)

        assert result.items == [
            (
                files[4].consignment.series.body.BodyId,
                "testing body5",
                files[4].consignment.series.SeriesId,
                "test series5",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[5].consignment.series.body.BodyId,
                "testing body6",
                files[5].consignment.series.SeriesId,
                "test series6",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[6].consignment.series.body.BodyId,
                "testing body7",
                files[6].consignment.series.SeriesId,
                "test series7",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[7].consignment.series.body.BodyId,
                "testing body8",
                files[7].consignment.series.SeriesId,
                "test series8",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[8].consignment.series.body.BodyId,
                "testing body9",
                files[8].consignment.series.SeriesId,
                "test series9",
                "15/02/2023",
                1,
                1,
            ),
        ]

    def test_browse_with_date_from_and_to_filter_no_result(
        self, client: FlaskClient
    ):
        """
        Given multiple File objects in the database and consignment transfer complete date
            that matches all of them
        When browse_data is called with date_from and date_to
        Then if date range not matched it returns empty list containing multiple dictionary
        """
        create_multiple_test_records()

        filters = {
            "date_range": {"date_from": "01/03/2023", "date_to": "31/05/2023"}
        }
        result = browse_data(page=1, per_page=per_page, filters=filters)

        assert result.items == []

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
    def test_browse_transferring_body_with_transferring_body_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given multiple File objects in the database and a transferring_body_id
            that matches only one of them
        And the session contains user info for a standard user with access to the
            transferring body
        When browse_data is called with transferring_body_id
        Then it returns a list containing 1 dictionary for the matching record with
            expected fields
        """
        files = create_multiple_test_records()

        file = files[0]

        mock_standard_user(client, file.consignment.series.body.Name)

        transferring_body_id = file.consignment.series.body.BodyId
        series_id = file.consignment.series.SeriesId
        result = browse_data(
            page=1,
            per_page=per_page,
            browse_type="transferring_body",
            transferring_body_id=transferring_body_id,
        )

        assert result.items == [
            (
                transferring_body_id,
                "test body1",
                series_id,
                "test series1",
                "01/01/2023",
                1,
                1,
            )
        ]

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
    def test_browse_series_with_series_filter(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given multiple File objects in the database and a series_id
            that matches only one of them
        And the session contains user info for a standard user with access to the series'
            associated transferring body
        When browse_data is called with series_id
        Then it returns a list containing 1 dictionary for the matching record with
            expected fields
        """
        files = create_multiple_test_records()

        file = files[0]
        mock_standard_user(client, file.consignment.series.body.Name)

        transferring_body_id = file.consignment.series.body.BodyId
        series_id = file.consignment.series.SeriesId
        consignment_id = file.consignment.ConsignmentId

        result = browse_data(
            page=1, per_page=per_page, browse_type="series", series_id=series_id
        )

        assert result.items == [
            (
                transferring_body_id,
                "test body1",
                series_id,
                "test series1",
                "01/01/2023",
                1,
                consignment_id,
                "test consignment1",
            )
        ]


class TestBrowseConsignment:
    def test_browse_consignment_with_consignment_filter(
        self, client: FlaskClient, mock_standard_user
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

        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment, FileName="file_1", FileType="file"
        )

        file_1_metadata = {
            "date_last_modified": "2023-02-25T10:12:47",
            "closure_type": "Closed",
            "closure_start_date": "2023-02-25T11:14:34",
            "closure_period": "50",
        }

        [
            FileMetadataFactory(
                file=file_1,
                PropertyName=property_name,
                Value=value,
            )
            for property_name, value in file_1_metadata.items()
        ]

        file_2 = FileFactory(
            consignment=consignment, FileName="file_2", FileType="file"
        )

        file_2_metadata = {
            "date_last_modified": "2023-02-27T12:28:08",
            "closure_type": "Open",
            "closure_start_date": None,
            "closure_period": None,
        }

        [
            FileMetadataFactory(
                file=file_2,
                PropertyName=property_name,
                Value=value,
            )
            for property_name, value in file_2_metadata.items()
        ]

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment,
            FileName="file_1.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment,
            FileName="file_2.ppt",
            FileType="file",
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            consignment=consignment,
            FileName="file_3.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment,
            FileName="file_1.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment,
            FileName="file_2.ppt",
            FileType="file",
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            consignment=consignment,
            FileName="file_3.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_start_date",
            Value=None,
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_period",
            Value=None,
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment,
            FileName="file_1.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment,
            FileName="file_2.ppt",
            FileType="file",
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            consignment=consignment,
            FileName="file_3.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-28T10:12:47",
        )

        FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-28T10:12:47",
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment,
            FileName="file_1.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment,
            FileName="file_2.ppt",
            FileType="file",
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            consignment=consignment,
            FileName="file_3.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-28T10:12:47",
        )

        FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-28T10:12:47",
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        FileFactory(consignment=consignment, FileType="folder")

        FileFactory(FileType="file")

        mock_standard_user(client, file_1.consignment.series.body.Name)
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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            consignment=consignment, FileName="file_3", FileType="file"
        )

        FileMetadataFactory(
            file=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            consignment=consignment, FileName="file_3", FileType="file"
        )

        FileMetadataFactory(
            file=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            consignment=consignment, FileName="file_3", FileType="file"
        )

        FileMetadataFactory(
            file=file_3,
            PropertyName="date_last_modified",
            Value="2023-01-23T10:12:47",
        )

        FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_start_date",
            Value="2023-01-23T10:12:47",
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment, FileName="file_1", FileType="file"
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment, FileName="file_2", FileType="file"
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            consignment=consignment, FileName="file_3", FileType="file"
        )

        FileMetadataFactory(
            file=file_3,
            PropertyName="date_last_modified",
            Value="2023-01-23T10:12:47",
        )

        FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_start_date",
            Value="2023-01-23T10:12:47",
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment,
            FileName="first_file.txt",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment,
            FileName="fourth_file.pdf",
            FileType="file",
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            consignment=consignment,
            FileName="fifth_file.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(consignment=consignment, FileType="folder")

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
        mock_standard_user(client, consignment.series.body.Name)

        file_1 = FileFactory(
            consignment=consignment,
            FileName="first_file.txt",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_1,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_1, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_1,
            PropertyName="closure_period",
            Value="1",
        )

        file_2 = FileFactory(
            consignment=consignment,
            FileName="fourth_file.pdf",
            FileType="file",
        )
        FileMetadataFactory(
            file=file_2,
            PropertyName="date_last_modified",
            Value="2023-02-27T12:28:08",
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_type", Value="Open"
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_start_date", Value=None
        )
        FileMetadataFactory(
            file=file_2, PropertyName="closure_period", Value=None
        )

        file_3 = FileFactory(
            consignment=consignment,
            FileName="fifth_file.docx",
            FileType="file",
        )

        FileMetadataFactory(
            file=file_3,
            PropertyName="date_last_modified",
            Value="2023-02-25T10:12:47",
        )

        FileMetadataFactory(
            file=file_3, PropertyName="closure_type", Value="Closed"
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_start_date",
            Value="2023-02-25T11:14:34",
        )
        FileMetadataFactory(
            file=file_3,
            PropertyName="closure_period",
            Value="1",
        )

        FileFactory(consignment=consignment, FileType="folder")

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
