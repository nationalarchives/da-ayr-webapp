"""
Security tests for parameter pollution vulnerabilities.

Tests that Flask reserved parameters (_external, _anchor, _scheme, _method)
cannot be injected by users to cause errors or security issues.

Note: Marshmallow schemas with `unknown = EXCLUDE` handle filtering of
unknown parameters, including Flask reserved params.
"""

from unittest.mock import Mock, patch


class TestParameterPollutionSecurity:
    """Security tests for parameter pollution attack prevention."""

    @patch("app.main.routes.setup_opensearch")
    def test_search_endpoint_prevents_typeerror_from_duplicate_anchor(
        self, mock_setup_opensearch, client, mock_standard_user
    ):
        """
        Test that duplicate _anchor parameter doesn't cause errors.

        Marshmallow schemas with `unknown = EXCLUDE` filter out unknown
        parameters like _anchor, preventing them from reaching url_for().
        """
        # Set up authenticated session
        mock_standard_user(client)
        open_search = Mock()
        open_search.search.return_value = {
            "aggregations": {
                "browse_series_options": {"buckets": []},
            }
        }
        mock_setup_opensearch.return_value = open_search

        response = client.get("/search/results?_anchor=exploit")

        assert response.status_code == 200
