from flask.testing import FlaskClient

from app.main.db.queries import build_browse_records_query


class TestBrowseRecords:
    def test_build_browse_records_query_with_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a body name the user can access
        When build_browse_records_query is called and executed
        Then it returns flattened records for that body ordered by date_of_record desc
        """
        body_name = browse_consignment_files[0].consignment.series.body.Name

        mock_standard_user(client, body_name)

        query = build_browse_records_query(
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
                "20/05/2023",
                None,
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
                browse_consignment_files[3].FileId,
                "fourth_file.xls",
                browse_consignment_files[3].FilePath,
                "12/04/2023",
                None,
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
                browse_consignment_files[2].FileId,
                "third_file.docx",
                browse_consignment_files[2].FilePath,
                "10/03/2023",
                None,
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
                browse_consignment_files[0].FileId,
                "first_file.docx",
                browse_consignment_files[0].FilePath,
                "25/02/2023",
                None,
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
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                browse_consignment_files[1].FilePath,
                "15/01/2023",
                None,
                "Open",
                None,
                "15/01/2023",
            ),
        ]

        assert results == expected_results

    def test_build_browse_records_query_no_results_for_unknown_body(
        self, client: FlaskClient
    ):
        """
        Given a body name that does not exist
        When build_browse_records_query is called
        Then it returns no rows
        """
        query = build_browse_records_query(
            accessible_transferring_body_names=["unknown_body"]
        )
        results = query.all()

        assert results == []

    def test_build_browse_records_query_all_access_user_sees_all_rows(
        self, client: FlaskClient, browse_files
    ):
        """
        Given an all-access query with no body restriction
        When build_browse_records_query is executed
        Then all accessible file rows are returned
        """
        query = build_browse_records_query(
            accessible_transferring_body_names=None
        )
        results = query.all()

        assert len(results) == len(browse_files)
