from datetime import datetime

from app.main.db.models import db
from app.main.db.queries import build_browse_records_base_query
from app.tests.factories import FileFactory


def _row_mapping(row):
    return row._mapping


def _file_names(rows):
    return [_row_mapping(row)["file_name"] for row in rows]


class TestBrowseRecordsBaseQuery:
    def test_build_browse_records_base_query_with_results(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given a body name the user can access
        When build_browse_records_base_query is called and executed
        Then it returns flattened records for that body
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name
        consignment = browse_consignment_files[0].consignment
        transfer_complete_datetime = datetime(2024, 5, 1, 13, 45, 0)
        expected_transfer_complete_date = "01/05/2024"

        consignment.TransferCompleteDatetime = transfer_complete_datetime
        db.session.flush()

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name]
        )
        results = query.all()

        body = browse_consignment_files[0].consignment.series.body
        series = browse_consignment_files[0].consignment.series

        expected_results = {
            (
                body.BodyId,
                body.Name,
                series.SeriesId,
                series.Name,
                consignment.ConsignmentId,
                consignment.ConsignmentReference,
                expected_transfer_complete_date,
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                browse_consignment_files[4].FilePath,
                "Open",
                None,
                "20/05/2023",
            ),
            (
                body.BodyId,
                body.Name,
                series.SeriesId,
                series.Name,
                consignment.ConsignmentId,
                consignment.ConsignmentReference,
                expected_transfer_complete_date,
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                browse_consignment_files[3].FilePath,
                "Closed",
                "25/03/2070",
                "12/04/2023",
            ),
            (
                body.BodyId,
                body.Name,
                series.SeriesId,
                series.Name,
                consignment.ConsignmentId,
                consignment.ConsignmentReference,
                expected_transfer_complete_date,
                browse_consignment_files[2].FileId,
                "third_file.docx",
                browse_consignment_files[2].FilePath,
                "Closed",
                "10/03/2090",
                "10/03/2023",
            ),
            (
                body.BodyId,
                body.Name,
                series.SeriesId,
                series.Name,
                consignment.ConsignmentId,
                consignment.ConsignmentReference,
                expected_transfer_complete_date,
                browse_consignment_files[0].FileId,
                "first_file.docx",
                browse_consignment_files[0].FilePath,
                "Closed",
                "25/02/2023",
                "25/02/2023",
            ),
            (
                body.BodyId,
                body.Name,
                series.SeriesId,
                series.Name,
                consignment.ConsignmentId,
                consignment.ConsignmentReference,
                expected_transfer_complete_date,
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                browse_consignment_files[1].FilePath,
                "Open",
                None,
                "15/01/2023",
            ),
        }

        assert len(results) == len(expected_results)
        assert set(results) == expected_results

    def test_build_browse_records_base_query_none_sorting_orders_leaves_query_unsorted(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given sorting_orders is None
        When build_browse_records_base_query is executed
        Then the helper leaves ordering to the caller
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name],
            sorting_orders=None,
        )

        sql = str(
            query.statement.compile(compile_kwargs={"literal_binds": True})
        )

        assert "ORDER BY" not in sql.upper()

    def test_build_browse_records_base_query_sorts_by_opening_date_asc(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given an explicit ascending opening-date sort order
        When build_browse_records_base_query is executed
        Then records are returned in ascending opening date order
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name],
            sorting_orders={"opening_date": "asc"},
        )
        results = query.all()

        assert _file_names(results) == [
            "first_file.docx",
            "fourth_file.xls",
            "third_file.docx",
            "fifth_file.doc",
            "second_file.ppt",
        ]

    def test_build_browse_records_base_query_sorts_by_opening_date_desc(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given an explicit descending opening-date sort order
        When build_browse_records_base_query is executed
        Then records are returned in descending opening date order
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name],
            sorting_orders={"opening_date": "desc"},
        )
        results = query.all()

        assert _file_names(results) == [
            "fifth_file.doc",
            "second_file.ppt",
            "third_file.docx",
            "fourth_file.xls",
            "first_file.docx",
        ]

    def test_build_browse_records_base_query_sorts_date_of_record_desc(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given an explicit descending date-of-record sort order
        When build_browse_records_base_query is executed
        Then records are returned in descending date order
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name],
            sorting_orders={"date_of_record": "desc"},
        )
        results = query.all()

        assert _file_names(results) == [
            "fifth_file.doc",
            "fourth_file.xls",
            "third_file.docx",
            "first_file.docx",
            "second_file.ppt",
        ]

    def test_build_browse_records_base_query_sorts_date_of_record_asc(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given an explicit ascending date-of-record sort order
        When build_browse_records_base_query is executed
        Then records are returned in ascending date order
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name],
            sorting_orders={"date_of_record": "asc"},
        )
        results = query.all()

        assert _file_names(results) == [
            "second_file.ppt",
            "first_file.docx",
            "third_file.docx",
            "fourth_file.xls",
            "fifth_file.doc",
        ]

    def test_build_browse_records_base_query_sorts_by_series_desc(
        self, client, browse_files
    ):
        """
        Given a descending series sort order
        When build_browse_records_base_query is executed
        Then rows are ordered by series in descending order
        """
        query = build_browse_records_base_query(
            accessible_transferring_body_names=None,
            sorting_orders={"series": "desc"},
        )
        results = query.all()

        series_values = [_row_mapping(result)["series"] for result in results]

        assert series_values == sorted(series_values, reverse=True)

    def test_build_browse_records_base_query_filters_by_series(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given a series filter
        When build_browse_records_base_query is executed
        Then only records matching the series are returned
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name
        series_name = browse_consignment_files[0].consignment.series.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name],
            filters={"series": series_name},
        )
        results = query.all()

        assert len(results) == len(browse_consignment_files)
        assert all(
            _row_mapping(result)["series"] == series_name for result in results
        )

    def test_build_browse_records_base_query_filters_by_consignment_reference(
        self, client, browse_files
    ):
        """
        Given a consignment reference filter
        When build_browse_records_base_query is executed
        Then only records matching that consignment reference are returned
        """
        query = build_browse_records_base_query(
            accessible_transferring_body_names=None,
            filters={"consignment_reference": "TDR-2023-TH3"},
        )
        results = query.all()

        assert len(results) == 3
        assert all(
            _row_mapping(result)["consignment_reference"] == "TDR-2023-TH3"
            for result in results
        )

    def test_build_browse_records_base_query_filters_by_record_status_closed(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given the record status filter value closed
        When build_browse_records_base_query is executed
        Then only closed records are returned
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name],
            filters={"record_status": "closed"},
        )
        results = query.all()

        assert sorted(_file_names(results)) == [
            "first_file.docx",
            "fourth_file.xls",
            "third_file.docx",
        ]

    def test_build_browse_records_base_query_filters_by_record_status_closed_includes_retained_for_security(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given a record retained for security and records closed for other reasons
        When build_browse_records_base_query is executed with record_status closed
        Then both are returned, since retained-for-security records are a kind of closed record
        """
        consignment = browse_consignment_files[0].consignment
        body_name = consignment.series.body.Name

        FileFactory(
            consignment=consignment,
            FileName="retained_file.docx",
            FileType="file",
            ClosureType="Retained for security",
        )

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name],
            filters={"record_status": "closed"},
        )
        results = query.all()

        assert sorted(_file_names(results)) == [
            "first_file.docx",
            "fourth_file.xls",
            "retained_file.docx",
            "third_file.docx",
        ]

    def test_build_browse_records_base_query_filters_by_last_modified_date_range(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given a last-modified date filter field and date range
        When build_browse_records_base_query is executed
        Then records are filtered using date_last_modified
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name],
            filters={
                "date_filter_field": "date_last_modified",
                "date_from": "2023-04-01",
                "date_to": "2023-05-31",
            },
        )
        results = query.all()

        assert sorted(_file_names(results)) == [
            "fifth_file.doc",
            "fourth_file.xls",
        ]

    def test_build_browse_records_base_query_filters_by_transferred_date_range(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given a transferred date filter field and date range
        When build_browse_records_base_query is executed
        Then records are filtered using end_date
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name],
            filters={
                "date_filter_field": "transferred",
                "date_from": "2023-04-01",
                "date_to": "2023-05-31",
            },
        )
        results = query.all()

        assert results == []

    def test_build_browse_records_base_query_filters_by_date_range_without_field(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given a date range with no date filter field selected
        When build_browse_records_base_query is executed
        Then records are filtered using date of record
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name],
            filters={"date_from": "2023-04-01", "date_to": "2023-05-31"},
        )
        results = query.all()

        assert sorted(_file_names(results)) == [
            "fifth_file.doc",
            "fourth_file.xls",
        ]

    def test_build_browse_records_base_query_filters_by_transferring_body_name(
        self, client, browse_files
    ):
        """
        Given a transferring body name filter
        When build_browse_records_base_query is executed
        Then only records under matching transferring body are returned
        """
        query = build_browse_records_base_query(
            accessible_transferring_body_names=None,
            filters={"transferring_body": "second_body"},
        )
        results = query.all()

        assert len(results) == 7
        assert all(
            _row_mapping(result)["transferring_body"] == "second_body"
            for result in results
        )

    def test_build_browse_records_base_query_transferring_body_requires_exact_match(
        self, client, browse_files
    ):
        """
        Given a partial transferring body filter
        When build_browse_records_base_query is executed
        Then no rows are returned because matching is exact
        """
        query = build_browse_records_base_query(
            accessible_transferring_body_names=None,
            filters={"transferring_body": "second"},
        )
        results = query.all()

        assert results == []

    def test_build_browse_records_base_query_series_requires_exact_match(
        self, client, browse_files
    ):
        """
        Given a partial series filter
        When build_browse_records_base_query is executed
        Then no rows are returned because matching is exact
        """
        query = build_browse_records_base_query(
            accessible_transferring_body_names=None,
            filters={"series": "second"},
        )
        results = query.all()

        assert results == []

    def test_build_browse_records_base_query_consignment_requires_exact_match(
        self, client, browse_files
    ):
        """
        Given a partial consignment reference filter
        When build_browse_records_base_query is executed
        Then no rows are returned because matching is exact
        """
        query = build_browse_records_base_query(
            accessible_transferring_body_names=None,
            filters={"consignment_reference": "TDR-2023-TH"},
        )
        results = query.all()

        assert results == []


class TestBrowseRecordsBaseQueryMetadataFields:
    def test_build_browse_records_base_query_returns_browse_metadata_fields(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given files with closure_type, opening_date and date_last_modified/end_date set
        When build_browse_records_base_query is executed
        Then closure_type, opening_date and date_of_record are returned directly
        on each row, formatted for display, without a separate metadata fetch
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name
        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name]
        )
        results = {
            _row_mapping(row)["file_name"]: _row_mapping(row)
            for row in query.all()
        }

        assert results["first_file.docx"]["closure_type"] == "Closed"
        assert results["first_file.docx"]["opening_date"] == "25/02/2023"
        assert results["first_file.docx"]["date_of_record"] == "25/02/2023"

        assert results["second_file.ppt"]["closure_type"] == "Open"
        assert results["second_file.ppt"]["opening_date"] is None
        assert results["second_file.ppt"]["date_of_record"] == "15/01/2023"

    def test_build_browse_records_base_query_does_not_query_file_metadata(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given the browse records base query
        When its SQL is compiled
        Then it does not reference the FileMetadata table
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name
        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name]
        )
        sql = str(
            query.statement.compile(compile_kwargs={"literal_binds": True})
        )

        assert "FileMetadata" not in sql
