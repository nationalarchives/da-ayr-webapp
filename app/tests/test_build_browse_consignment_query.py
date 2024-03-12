from flask.testing import FlaskClient

from app.main.db.queries import build_browse_consignment_query


class TestBrowseConsignment:
    def test_build_browse_consignment_query_with_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a filter value that does match consignment in the database
        When build_browse_consignment_query is called with it and is executed
        Then list of rows matching to consignment results returned
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        consignment_id = browse_consignment_files[0].consignment.ConsignmentId
        filters = {"record_status": "open"}
        query = build_browse_consignment_query(
            consignment_id=consignment_id, filters=filters
        )

        results = query.all()

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
        assert results == expected_results

    def test_build_browse_consignment_query_no_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a filter value that does not match consignment in the database
        When build_browse_consignment_query is called with it and is executed
        Then an empty list is returned
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        filters = {
            "date_filter_field": "date_last_modified",
            "date_from": "2023-06-01",
        }

        query = build_browse_consignment_query(
            consignment_id=consignment_id, filters=filters
        )
        results = query.all()
        assert results == []
