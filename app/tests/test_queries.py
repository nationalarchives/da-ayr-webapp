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
                files[0].file_consignments.consignment_bodies.BodyId,
                "test body1",
                files[0].file_consignments.consignment_series.SeriesId,
                "test series1",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[1].file_consignments.consignment_bodies.BodyId,
                "test body2",
                files[1].file_consignments.consignment_series.SeriesId,
                "test series2",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[9].file_consignments.consignment_bodies.BodyId,
                "testing body10",
                files[9].file_consignments.consignment_series.SeriesId,
                "test series10",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[10].file_consignments.consignment_bodies.BodyId,
                "testing body11",
                files[10].file_consignments.consignment_series.SeriesId,
                "test series11",
                "01/01/2023",
                1,
                2,
            ),
            (
                files[2].file_consignments.consignment_bodies.BodyId,
                "testing body3",
                files[2].file_consignments.consignment_series.SeriesId,
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
                files[3].file_consignments.consignment_bodies.BodyId,
                "testing body4",
                files[3].file_consignments.consignment_series.SeriesId,
                "test series4",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[4].file_consignments.consignment_bodies.BodyId,
                "testing body5",
                files[4].file_consignments.consignment_series.SeriesId,
                "test series5",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[5].file_consignments.consignment_bodies.BodyId,
                "testing body6",
                files[5].file_consignments.consignment_series.SeriesId,
                "test series6",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[6].file_consignments.consignment_bodies.BodyId,
                "testing body7",
                files[6].file_consignments.consignment_series.SeriesId,
                "test series7",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[7].file_consignments.consignment_bodies.BodyId,
                "testing body8",
                files[7].file_consignments.consignment_series.SeriesId,
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
                files[4].file_consignments.consignment_bodies.BodyId,
                "testing body5",
                files[4].file_consignments.consignment_series.SeriesId,
                "test series5",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[5].file_consignments.consignment_bodies.BodyId,
                "testing body6",
                files[5].file_consignments.consignment_series.SeriesId,
                "test series6",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[6].file_consignments.consignment_bodies.BodyId,
                "testing body7",
                files[6].file_consignments.consignment_series.SeriesId,
                "test series7",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[7].file_consignments.consignment_bodies.BodyId,
                "testing body8",
                files[7].file_consignments.consignment_series.SeriesId,
                "test series8",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[8].file_consignments.consignment_bodies.BodyId,
                "testing body9",
                files[8].file_consignments.consignment_series.SeriesId,
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
                files[0].file_consignments.consignment_bodies.BodyId,
                "test body1",
                files[0].file_consignments.consignment_series.SeriesId,
                "test series1",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[1].file_consignments.consignment_bodies.BodyId,
                "test body2",
                files[1].file_consignments.consignment_series.SeriesId,
                "test series2",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[9].file_consignments.consignment_bodies.BodyId,
                "testing body10",
                files[9].file_consignments.consignment_series.SeriesId,
                "test series10",
                "01/01/2023",
                1,
                1,
            ),
            (
                files[10].file_consignments.consignment_bodies.BodyId,
                "testing body11",
                files[10].file_consignments.consignment_series.SeriesId,
                "test series11",
                "01/01/2023",
                1,
                2,
            ),
            (
                files[2].file_consignments.consignment_bodies.BodyId,
                "testing body3",
                files[2].file_consignments.consignment_series.SeriesId,
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
                files[4].file_consignments.consignment_bodies.BodyId,
                "testing body5",
                files[4].file_consignments.consignment_series.SeriesId,
                "test series5",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[5].file_consignments.consignment_bodies.BodyId,
                "testing body6",
                files[5].file_consignments.consignment_series.SeriesId,
                "test series6",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[6].file_consignments.consignment_bodies.BodyId,
                "testing body7",
                files[6].file_consignments.consignment_series.SeriesId,
                "test series7",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[7].file_consignments.consignment_bodies.BodyId,
                "testing body8",
                files[7].file_consignments.consignment_series.SeriesId,
                "test series8",
                "15/02/2023",
                1,
                1,
            ),
            (
                files[8].file_consignments.consignment_bodies.BodyId,
                "testing body9",
                files[8].file_consignments.consignment_series.SeriesId,
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

        mock_standard_user(
            client, [file.file_consignments.consignment_bodies.Name]
        )

        transferring_body_id = file.file_consignments.consignment_bodies.BodyId
        series_id = file.file_consignments.consignment_series.SeriesId
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
        mock_standard_user(
            client, [file.file_consignments.consignment_bodies.Name]
        )
        transferring_body_id = file.file_consignments.consignment_bodies.BodyId
        series_id = file.file_consignments.consignment_series.SeriesId
        consignment_id = file.file_consignments.ConsignmentId

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

        mock_standard_user(client, [consignment.consignment_bodies.Name])

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
        mock_standard_user(client, [consignment.consignment_bodies.Name])

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
        mock_standard_user(client, [consignment.consignment_bodies.Name])

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
        mock_standard_user(client, [consignment.consignment_bodies.Name])

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
        mock_standard_user(client, [consignment.consignment_bodies.Name])

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
        mock_standard_user(client, [consignment.consignment_bodies.Name])

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
        mock_standard_user(client, [consignment.consignment_bodies.Name])

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
        mock_standard_user(client, [consignment.consignment_bodies.Name])

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
        mock_standard_user(client, [consignment.consignment_bodies.Name])

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
            client, [file_1.file_consignments.consignment_bodies.Name]
        )
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
        mock_standard_user(client, [consignment.consignment_bodies.Name])

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
            client, [file_1.file_consignments.consignment_bodies.Name]
        )

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
        mock_standard_user(client, [consignment.consignment_bodies.Name])

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
            client, [file_1.file_consignments.consignment_bodies.Name]
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
