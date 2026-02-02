
import pytest
from unittest.mock import patch, MagicMock
from app.main.process_routes import browse_route


class TestBrowseRoute:


    @pytest.fixture
    def validated_data(self):
        return {
            "page": 1,
            "per_page": 10,
            "some_filter": "value"
        }

    @pytest.fixture
    def transferring_bodies(self):
        return ["Body1", "Body2"]

    @patch("app.main.process_routes.browse_route.get_pagination")
    @patch("app.main.process_routes.browse_route.db")
    @patch("app.main.process_routes.browse_route.build_browse_query")
    @patch("app.main.process_routes.browse_route.build_sorting_orders")
    @patch("app.main.process_routes.browse_route.build_filters")
    @patch("app.main.process_routes.browse_route.validate_date_filters")
    def test_process_browse_request_basic(
        self,
        mock_validate_date_filters,
        mock_build_filters,
        mock_build_sorting_orders,
        mock_build_browse_query,
        mock_db,
        mock_get_pagination,
        validated_data,
        transferring_bodies
    ):
        # Setup mocks
        mock_validate_date_filters.return_value = ([], None, None, {}, [])
        mock_build_filters.return_value = {"some_filter": "value"}
        mock_build_sorting_orders.return_value = {}
        mock_query = MagicMock()
        mock_paginate = MagicMock()
        mock_paginate.pages = 5
        mock_query.paginate.return_value = mock_paginate
        mock_build_browse_query.return_value = mock_query
        mock_db.session.query.return_value.scalar.return_value = 42
        mock_get_pagination.return_value = {"page": 1, "pages": 5}

        result = browse_route.process_browse_request(
            validated_data, 10, transferring_bodies
        )

        assert result["current_page"] == 1
        assert result["results"] == mock_paginate
        assert result["date_validation_errors"] == []
        assert result["date_error_fields"] == []
        assert result["transferring_bodies"] == transferring_bodies
        assert result["pagination"] == {"page": 1, "pages": 5}
        assert result["filters"] == {"some_filter": "value"}
        assert result["date_filters"] == {}
        assert result["sorting_orders"]["transferring_body"] == "asc"
        assert result["num_records_found"] == 42
        assert result["query_string_parameters"] == validated_data
    
    @patch("app.main.process_routes.browse_route.get_pagination")
    @patch("app.main.process_routes.browse_route.db")
    @patch("app.main.process_routes.browse_route.build_browse_query")
    @patch("app.main.process_routes.browse_route.build_sorting_orders")
    @patch("app.main.process_routes.browse_route.build_filters")
    @patch("app.main.process_routes.browse_route.validate_date_filters")
    def test_process_browse_request_pagination(
        self,
        mock_validate_date_filters,
        mock_build_filters,
        mock_build_sorting_orders,
        mock_build_browse_query,
        mock_db,
        mock_get_pagination,
        validated_data,
        transferring_bodies
    ):
        # Setup mocks for pagination
        mock_validate_date_filters.return_value = ([], None, None, {}, [])
        mock_build_filters.return_value = {"some_filter": "value"}
        mock_build_sorting_orders.return_value = {}
        mock_query = MagicMock()
        mock_paginate = MagicMock()
        mock_paginate.pages = 7
        mock_query.paginate.return_value = mock_paginate
        mock_build_browse_query.return_value = mock_query
        mock_db.session.query.return_value.scalar.return_value = 100
        mock_get_pagination.return_value = {"page": 3, "pages": 7}

        # Use a different page to check current page logic
        validated_data["page"] = 3

        result = browse_route.process_browse_request(
            validated_data, 10, transferring_bodies
        )

        assert result["pagination"]["page"] == 3
        assert result["pagination"]["pages"] == 7
        assert result["current_page"] == 3


    @patch("app.main.process_routes.browse_route.get_pagination")
    @patch("app.main.process_routes.browse_route.db")
    @patch("app.main.process_routes.browse_route.build_browse_query")
    @patch("app.main.process_routes.browse_route.build_sorting_orders")
    @patch("app.main.process_routes.browse_route.build_filters")
    @patch("app.main.process_routes.browse_route.validate_date_filters")
    def test_process_browse_request_no_total_records(
        self,
        mock_validate_date_filters,
        mock_build_filters,
        mock_build_sorting_orders,
        mock_build_browse_query,
        mock_db,
        mock_get_pagination,
        validated_data,
        transferring_bodies
    ):
        mock_validate_date_filters.return_value = ([], None, None, {}, [])
        mock_build_filters.return_value = {"some_filter": "value"}
        mock_build_sorting_orders.return_value = {}
        mock_query = MagicMock()
        mock_paginate = MagicMock()
        mock_paginate.pages = 3
        mock_query.paginate.return_value = mock_paginate
        mock_build_browse_query.return_value = mock_query
        mock_db.session.query.return_value.scalar.return_value = None
        mock_get_pagination.return_value = {"page": 1, "pages": 3}

        result = browse_route.process_browse_request(
            validated_data, 10, transferring_bodies
        )

        assert result["num_records_found"] == 0


    @patch("app.main.process_routes.browse_route.get_pagination")
    @patch("app.main.process_routes.browse_route.db")
    @patch("app.main.process_routes.browse_route.build_browse_query")
    @patch("app.main.process_routes.browse_route.build_sorting_orders")
    @patch("app.main.process_routes.browse_route.build_filters")
    @patch("app.main.process_routes.browse_route.validate_date_filters")
    def test_process_browse_request_with_date_errors(
        self,
        mock_validate_date_filters,
        mock_build_filters,
        mock_build_sorting_orders,
        mock_build_browse_query,
        mock_db,
        mock_get_pagination,
        validated_data,
        transferring_bodies
    ):
        mock_validate_date_filters.return_value = (["error"], "2020-01-01", "2020-12-31", {"from": "2020-01-01", "to": "2020-12-31"}, ["from", "to"])
        mock_build_filters.return_value = {"date": "2020-01-01"}
        mock_build_sorting_orders.return_value = {"transferring_body": "desc"}
        mock_query = MagicMock()
        mock_paginate = MagicMock()
        mock_paginate.pages = 2
        mock_query.paginate.return_value = mock_paginate
        mock_build_browse_query.return_value = mock_query
        mock_db.session.query.return_value.scalar.return_value = 10
        mock_get_pagination.return_value = {"page": 1, "pages": 2}

        result = browse_route.process_browse_request(
            validated_data, 10, transferring_bodies
        )

        assert result["date_validation_errors"] == ["error"]
        assert result["date_error_fields"] == ["from", "to"]
        assert result["date_filters"] == {"from": "2020-01-01", "to": "2020-12-31"}
        assert result["filters"] == {"date": "2020-01-01"}
        assert result["sorting_orders"]["transferring_body"] == "desc"
