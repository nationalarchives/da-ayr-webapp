from flask import render_template


class TestPaginationTemplate:
    """Test the pagination template by rendering it and checking actual HTML output."""

    def test_template_filters_out_page_and_id_from_query_params(self, app):
        """Test that page=999 and _id=bad-id are filtered out of pagination links."""
        with app.test_request_context("/browse"):
            rendered = render_template(
                "main/pagination.html",
                pagination={"previous": 1, "next": 3, "pages": [1, 2, 3]},
                current_page=2,
                view_name="main.browse",
                id=None,
                query_string_parameters={
                    "search": "documents",
                    "sort": "date",
                    "page": 999,  # This should be filtered out
                    "_id": "bad-id",  # This should be filtered out
                    "filter": "pdf",
                },
            )

            # Should contain pagination HTML
            assert "govuk-pagination" in rendered

            # Should contain our preserved parameters
            assert "search=documents" in rendered
            assert "sort=date" in rendered
            assert "filter=pdf" in rendered

            # Should NOT contain the filtered parameters
            assert "page=999" not in rendered
            assert "_id=bad-id" not in rendered

            # Should contain explicit pagination page numbers (1 and 3)
            assert "page=1" in rendered  # Previous page
            assert "page=3" in rendered  # Next page

    def test_template_uses_explicit_id_not_query_param_id(self, app):
        """Test that explicit id parameter overrides _id in query_string_parameters."""
        explicit_id = "f47ac10b-58cc-4372-a567-0e02b2c3d479"

        with app.test_request_context("/browse"):
            rendered = render_template(
                "main/pagination.html",
                pagination={"previous": 1, "next": 3, "pages": [1, 2, 3]},
                current_page=2,
                view_name="main.browse_transferring_body",
                id=explicit_id,  # This should be used
                query_string_parameters={
                    "search": "test",
                    "_id": "wrong-id-from-params",  # This should be ignored
                    "page": 42,  # This should be ignored
                },
            )

            # Should use the explicit ID in the URL path (not as _id query param)
            assert f"/transferring_body/{explicit_id}" in rendered

            # Should NOT use the query param ID
            assert "_id=wrong-id-from-params" not in rendered
            assert "page=42" not in rendered

            # Should preserve other query params
            assert "search=test" in rendered

    def test_template_works_with_empty_query_params(self, app):
        """Test template renders correctly with no query parameters."""
        with app.test_request_context("/browse"):
            rendered = render_template(
                "main/pagination.html",
                pagination={"previous": None, "next": 2, "pages": [1, 2]},
                current_page=1,
                view_name="main.browse",
                id=None,
                query_string_parameters={},
            )

            assert "govuk-pagination" in rendered
            assert "page=2" in rendered  # Next page link

    def test_template_renders_nothing_when_no_pagination(self, app):
        """Test template renders empty when pagination is None."""
        with app.test_request_context("/browse"):
            rendered = render_template(
                "main/pagination.html",
                pagination=None,
                current_page=1,
                view_name="main.browse",
                id=None,
                query_string_parameters={"search": "test"},
            )

            # Should be empty - no pagination HTML
            assert rendered.strip() == ""
