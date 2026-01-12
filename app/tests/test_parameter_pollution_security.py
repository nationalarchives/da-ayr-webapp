"""
Security tests for parameter pollution vulnerabilities.

Tests that Flask reserved parameters (_external, _anchor, _scheme, _method)
cannot be injected by users to cause errors or security issues.
"""

import pytest

from app.main.util.request_validation_utils import (
    _filter_non_defaults,
    sanitize_url_params,
)


class TestParameterPollutionSecurity:
    """Security tests for parameter pollution attack prevention."""

    def test_sanitize_url_params_removes_flask_reserved_parameters(self):
        """Test that sanitize_url_params removes all Flask reserved parameters."""
        malicious_params = {
            "query": "test search",
            "_external": "1",  # Could enable open redirect
            "_anchor": "malicious",  # Could cause TypeError
            "_scheme": "http",  # Could downgrade HTTPS
            "_method": "POST",  # Could manipulate HTTP method
            "page": "2",
            "_netloc": "evil.com",  # Could enable open redirect
        }

        sanitized = sanitize_url_params(malicious_params)

        # Verify Flask reserved parameters are removed
        assert "_external" not in sanitized
        assert "_anchor" not in sanitized
        assert "_scheme" not in sanitized
        assert "_method" not in sanitized
        assert "_netloc" not in sanitized

        # Verify legitimate parameters are kept
        assert sanitized["query"] == "test search"
        assert sanitized["page"] == "2"

    def test_filter_non_defaults_blocks_underscore_parameters(self):
        """Test that _filter_non_defaults blocks parameters starting with underscore."""
        from marshmallow import Schema, fields

        class TestSchema(Schema):
            query = fields.Str()
            page = fields.Int(load_default=1)
            _external = fields.Str()  # Should be blocked even if in schema
            _anchor = fields.Str()  # Should be blocked even if in schema

        schema = TestSchema()
        validated_data = {
            "query": "test",
            "page": 2,
            "_external": "1",
            "_anchor": "malicious",
        }
        original_data = {
            "query": "test",
            "page": "2",
            "_external": "1",
            "_anchor": "malicious",
        }

        filtered = _filter_non_defaults(validated_data, schema, original_data)

        # Verify underscore parameters are blocked
        assert "_external" not in filtered
        assert "_anchor" not in filtered

        # Verify legitimate parameters pass through
        assert filtered["query"] == "test"
        assert filtered["page"] == 2

    def test_search_endpoint_prevents_typeerror_from_duplicate_anchor(
        self, client, standard_user
    ):
        """
        Test that duplicate _anchor parameter doesn't cause errors.

        This was the original vulnerability: url_for() would receive
        _anchor both as explicit kwarg and in **redirect_params,
        causing TypeError: got multiple values for keyword argument '_anchor'
        """
        # This should NOT crash with TypeError
        response = client.get(
            "/search?query=test&_anchor=exploit",
            headers={"Cookie": f"session={standard_user}"},
        )

        assert response.status_code in [200, 302]
        assert response.status_code != 500


@pytest.fixture
def standard_user(authenticated_client):
    """Fixture providing a standard user session."""
    from unittest.mock import MagicMock

    mock_user = MagicMock()
    mock_user.body_id = "123e4567-e89b-12d3-a456-426614174000"
    return mock_user
