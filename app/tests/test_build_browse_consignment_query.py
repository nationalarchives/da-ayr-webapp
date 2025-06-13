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
                None,
                "Open",
                None,
            ),
            (
                browse_consignment_files[1].FileId,
                "second_file.ppt",
                "15/01/2023",
                None,
                "Open",
                None,
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

    def test_build_browse_consignment_query_sorts_by_end_date_when_available(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a consignment with files that have both end_date and date_last_modified
        When build_browse_consignment_query is called with date_last_modified sorting
        Then the results should be sorted by end_date when available, falling back to date_last_modified
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        consignment_id = browse_consignment_files[0].consignment.ConsignmentId
        sorting_orders = {"date_last_modified": "desc"}

        query = build_browse_consignment_query(
            consignment_id=consignment_id, sorting_orders=sorting_orders
        )

        results = query.all()

        # Verify that files with end_date are sorted by end_date
        # and files without end_date are sorted by date_last_modified
        dates = [r[2] for r in results]
        assert dates == sorted(dates, reverse=True)

    def test_build_browse_consignment_query_filters_by_end_date_when_available(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a consignment with files that have both end_date and date_last_modified
        When build_browse_consignment_query is called with date_last_modified filtering
        Then the results should be filtered using end_date when available, falling back to date_last_modified
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        consignment_id = browse_consignment_files[0].consignment.ConsignmentId
        filters = {
            "date_filter_field": "date_last_modified",
            "date_from": "2023-01-01",
            "date_to": "2023-12-31",
        }

        query = build_browse_consignment_query(
            consignment_id=consignment_id, filters=filters
        )

        results = query.all()

        for result in results:
            date = result[2]
            assert "2023" in date
