"""
Security tests for parameter pollution vulnerabilities.

Tests that Flask reserved parameters (_external, _anchor, _scheme, _method)
cannot be injected by users to cause errors or security issues.
"""

from app.main.util.request_validation_utils import (
    FLASK_RESERVED_PARAMS,
    _filter_non_defaults,
)


class TestParameterPollutionSecurity:
    """Security tests for parameter pollution attack prevention."""

    def test_filter_non_defaults_blocks_flask_reserved_parameters(self):
        """Test that _filter_non_defaults blocks Flask reserved parameters."""
        from marshmallow import Schema, fields

        class TestSchema(Schema):
            query = fields.Str()
            page = fields.Int(load_default=1)
            _external = fields.Str()  # Should be blocked
            _anchor = fields.Str()  # Should be blocked
            _scheme = fields.Str()  # Should be blocked
            _method = fields.Str()  # Should be blocked
            _id = fields.Str()  # Should NOT be blocked (legitimate path param)

        schema = TestSchema()
        validated_data = {
            "query": "test",
            "page": 2,
            "_external": "1",
            "_anchor": "malicious",
            "_scheme": "http",
            "_method": "POST",
            "_id": "abc123",
        }
        original_data = {
            "query": "test",
            "page": "2",
            "_external": "1",
            "_anchor": "malicious",
            "_scheme": "http",
            "_method": "POST",
            "_id": "abc123",
        }

        filtered = _filter_non_defaults(validated_data, schema, original_data)

        # Verify Flask reserved parameters are blocked
        for param in FLASK_RESERVED_PARAMS:
            assert param not in filtered

        # Verify legitimate parameters pass through
        assert filtered["query"] == "test"
        assert filtered["page"] == 2
        assert filtered["_id"] == "abc123"  # Path params should pass through

    def test_search_endpoint_prevents_typeerror_from_duplicate_anchor(
        self, client, mock_standard_user
    ):
        """
        Test that duplicate _anchor parameter doesn't cause errors.

        This was the original vulnerability: url_for() would receive
        _anchor both as explicit kwarg and in **redirect_params,
        causing TypeError: got multiple values for keyword argument '_anchor'
        """
        # Set up authenticated session
        mock_standard_user(client)

        # This should NOT crash with TypeError
        response = client.get("/search?query=test&_anchor=exploit")

        assert response.status_code in [200, 302]
        assert response.status_code != 500
