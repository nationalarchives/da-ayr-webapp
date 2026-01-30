"""
Security tests for parameter pollution vulnerabilities.

Tests that Flask reserved parameters (_external, _anchor, _scheme, _method)
cannot be injected by users to cause errors or security issues.

Note: Marshmallow schemas with `unknown = EXCLUDE` handle filtering of
unknown parameters, including Flask reserved params.
"""


class TestParameterPollutionSecurity:
    """Security tests for parameter pollution attack prevention."""

    def test_search_endpoint_prevents_typeerror_from_duplicate_anchor(
        self, client, mock_standard_user
    ):
        """
        Test that duplicate _anchor parameter doesn't cause errors.

        Marshmallow schemas with `unknown = EXCLUDE` filter out unknown
        parameters like _anchor, preventing them from reaching url_for().
        """
        # Set up authenticated session
        mock_standard_user(client)

        # This should NOT crash with TypeError
        response = client.get("/search?query=test&_anchor=exploit")

        assert response.status_code in [200, 302]
        assert response.status_code != 500
