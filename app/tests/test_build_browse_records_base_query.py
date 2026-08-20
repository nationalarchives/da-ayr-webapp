from app.main.db.queries import (
    build_browse_records_base_query,
    get_browse_records_metadata_for_files,
)
from app.tests.factories import FileMetadataFactory


class TestBrowseRecordsBaseQuery:
    def test_build_browse_records_base_query_with_results(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given a body name the user can access
        When build_browse_records_base_query is called and executed
        Then it returns flattened records for that body ordered by date_of_record desc
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_base_query(
            accessible_transferring_body_names=[body_name]
        )
        results = query.all()

        body = browse_consignment_files[0].consignment.series.body
        series = browse_consignment_files[0].consignment.series
        consignment = browse_consignment_files[0].consignment

        expected_results = [
            (
                body.BodyId,
                body.Name,
                series.SeriesId,
                series.Name,
                consignment.ConsignmentId,
                consignment.ConsignmentReference,
                browse_consignment_files[4].FileId,
                "fifth_file.doc",
                browse_consignment_files[4].FilePath,
            ),
            (
                body.BodyId,
                body.Name,
                series.SeriesId,
                series.Name,
                consignment.ConsignmentId,
                consignment.ConsignmentReference,
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                browse_consignment_files[3].FilePath,
            ),
            (
                body.BodyId,
                body.Name,
                series.SeriesId,
                series.Name,
                consignment.ConsignmentId,
                consignment.ConsignmentReference,
                browse_consignment_files[2].FileId,
                "third_file.docx",
                browse_consignment_files[2].FilePath,
            ),
            (
                body.BodyId,
                body.Name,
                series.SeriesId,
                series.Name,
                consignment.ConsignmentId,
                consignment.ConsignmentReference,
                browse_consignment_files[0].FileId,
                "first_file.docx",
                browse_consignment_files[0].FilePath,
            ),
            (
                body.BodyId,
                body.Name,
                series.SeriesId,
                series.Name,
                consignment.ConsignmentId,
                consignment.ConsignmentReference,
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                browse_consignment_files[1].FilePath,
            ),
        ]

        assert results == expected_results

    def test_build_browse_records_base_query_none_sorting_orders_uses_default_sort(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given sorting_orders is None
        When build_browse_records_base_query is executed
        Then the default date_of_record descending sort is applied
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

        assert "ORDER BY" in sql.upper()

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

        assert [result[7] for result in results] == [
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

        assert [result[7] for result in results] == [
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

        assert [result[7] for result in results] == [
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

        assert [result[7] for result in results] == [
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

        series_values = [result[3] for result in results]

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
        assert all(result[3] == series_name for result in results)

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
        assert all(result[5] == "TDR-2023-TH3" for result in results)

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

        assert [result[7] for result in results] == [
            "fourth_file.xls",
            "third_file.docx",
            "first_file.docx",
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

        assert [result[7] for result in results] == [
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

        assert [result[7] for result in results] == [
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
        assert all(result[1] == "second_body" for result in results)


class TestBrowseRecordsMetadataQuery:
    def test_get_browse_records_metadata_for_files_empty_file_ids_returns_empty_dict(
        self, client
    ):
        """
        Given no file IDs are supplied
        When get_browse_records_metadata_for_files is called
        Then an empty metadata mapping is returned
        """
        assert get_browse_records_metadata_for_files([]) == {}

    def test_get_browse_records_metadata_for_files_returns_expected_metadata(
        self, client, browse_consignment_files
    ):
        """
        Given a set of file IDs with browse metadata
        When get_browse_records_metadata_for_files is called
        Then metadata is returned per file with date values formatted for display
        """
        file_one = browse_consignment_files[0]
        file_two = browse_consignment_files[1]

        FileMetadataFactory(
            file=file_one,
            PropertyName="end_date",
            Value="2023-09-30",
        )

        metadata = get_browse_records_metadata_for_files(
            [file_one.FileId, file_two.FileId]
        )

        assert set(metadata.keys()) == {file_one.FileId, file_two.FileId}

        assert metadata[file_one.FileId]["date_last_modified"] == "25/02/2023"
        assert metadata[file_one.FileId]["end_date"] == "30/09/2023"
        assert metadata[file_one.FileId]["closure_type"] == "Closed"
        assert metadata[file_one.FileId]["opening_date"] == "25/02/2023"

        assert metadata[file_two.FileId]["date_last_modified"] == "15/01/2023"
        assert metadata[file_two.FileId]["closure_type"] == "Open"
        assert metadata[file_two.FileId]["opening_date"] is None
        assert "end_date" not in metadata[file_two.FileId]
