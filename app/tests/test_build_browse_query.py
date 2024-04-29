from flask.testing import FlaskClient

from app.main.db.queries import build_browse_query


class TestBrowse:
    def test_build_browse_query_without_transferring_body_filter_with_results(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a filter value that does match transferring body in the database
        When build_browse_query is called with it and is executed
        Then matching list results rows is returned
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        filters = {
            "transferring_body": browse_files[0].consignment.series.body.Name
        }
        query = build_browse_query(filters=filters)
        results = query.all()
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
        assert results == expected_results

    def test_build_browse_query_without_transferring_body_filter_no_results(
        self, client: FlaskClient
    ):
        """
        Given a filter value that does not match transferring body in the database
        When build_browse_query is called with it and is executed
        Then an empty list is returned
        """
        filters = {"transferring_body": "junk"}
        query = build_browse_query(filters=filters)
        results = query.all()
        assert results == []

    def test_build_browse_query_with_transferring_body_filter_with_results(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a filter value that does match transferring body in the database
        When build_browse_query is called with transferring body filter executed
        Then list of rows matching to transferring body results returned
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        query = build_browse_query(transferring_body_id=transferring_body_id)

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
                1,
            ),
            (
                browse_transferring_body_files[
                    0
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[0].consignment.series.body.Name,
                browse_transferring_body_files[1].consignment.series.SeriesId,
                browse_transferring_body_files[1].consignment.series.Name,
                "30/03/2023",
                1,
                2,
            ),
            (
                browse_transferring_body_files[
                    0
                ].consignment.series.body.BodyId,
                browse_transferring_body_files[0].consignment.series.body.Name,
                browse_transferring_body_files[3].consignment.series.SeriesId,
                browse_transferring_body_files[3].consignment.series.Name,
                "07/07/2023",
                1,
                3,
            ),
        ]
        assert results == expected_results

    def test_build_browse_query_with_transferring_body_filter_with_no_results(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a filter value that does not match series in the database
        When build_browse_query is called with transferring body filter executed
        Then an empty list is returned
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId
        filters = {"series": "junk"}

        query = build_browse_query(
            transferring_body_id=transferring_body_id, filters=filters
        )
        results = query.all()
        assert results == []
