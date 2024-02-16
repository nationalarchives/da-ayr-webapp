from flask.testing import FlaskClient

from app.main.db.queries import build_browse_all_query


class TestBrowse:
    def test_build_browse_all_query_with_results(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a filter value that does match transferring body in the database
        When build_browse_all_query is called with it and is executed
        Then matching list results rows is returned
        """
        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        filters = {
            "transferring_body": browse_files[0].consignment.series.body.Name
        }
        query = build_browse_all_query(filters)
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

    def test_build_browse_all_query_no_results(self, client: FlaskClient):
        """
        Given a filter value that does not match transferring body in the database
        When build_browse_all_query is called with it and is executed
        Then an empty list is returned
        """
        filters = {"transferring_body": "junk"}
        query = build_browse_all_query(filters)
        results = query.all()
        assert results == []
