from flask.testing import FlaskClient

from app.main.db.queries import build_browse_series_query


class TestBrowseSeries:
    def test_build_browse_series_query_with_results(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a filter value that does match series in the database
        When build_browse_series_query is called with it and is executed
        Then list of rows matching to series results returned
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        series_id = browse_transferring_body_files[
            0
        ].consignment.series.SeriesId

        query = build_browse_series_query(series_id=series_id)

        results = query.all()

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
                browse_transferring_body_files[0].consignment.ConsignmentId,
                browse_transferring_body_files[
                    0
                ].consignment.ConsignmentReference,
            ),
        ]
        assert results == expected_results

    def test_build_browse_series_query_no_results(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a filter value that does not match series in the database
        When build_browse_series_query is called with it and is executed
        Then an empty list is returned
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        series_id = browse_transferring_body_files[
            0
        ].consignment.series.SeriesId

        filters = {
            "date_from": "2024-01-01",
        }

        query = build_browse_series_query(series_id=series_id, filters=filters)
        results = query.all()
        assert results == []
