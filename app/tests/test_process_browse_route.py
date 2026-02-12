from flask import Response
from flask.testing import FlaskClient

from app.main.process_routes.browse_route import process_browse_request
from app.tests.test_browse import (
    TestBrowse,
)


class TestProcessBrowseRoute(TestBrowse):

    def test_browse_filter_no_results(
        self, client: FlaskClient, mock_all_access_user
    ):
        mock_validated_data = {
            "date_from_day": None,
            "date_from_month": None,
            "date_from_year": None,
            "date_to_day": None,
            "date_to_month": None,
            "date_to_year": None,
            "transferring_body_filter": "",
            "series_filter": "",
            "consignment_reference": "",
            "file_name": "",
            "description": "",
            "date_filter_field": "",
            "record_status": "all",
            "sort": "transferring_body",
            "page": 1,
            "per_page": None,
        }

        result = process_browse_request(
            validated_data=mock_validated_data,
            default_page_size=10,
            transferring_bodies=["body1", "body2"],
        )
        assert result["current_page"] == 1
        assert result["results"].items == []
        assert result["date_validation_errors"] == {
            "date_from": [],
            "date_to": [],
        }
        assert result["date_error_fields"] == ""
        assert result["transferring_bodies"] == ["body1", "body2"]
        assert result["pagination"] is None
        assert result["filters"] == {}
        assert result["date_filters"] == {}
        assert result["sorting_orders"] == {"transferring_body": "asc"}
        assert result["num_records_found"] == 0
        assert result["query_string_parameters"] == {
            "date_from_day": None,
            "date_from_month": None,
            "date_from_year": None,
            "date_to_day": None,
            "date_to_month": None,
            "date_to_year": None,
            "transferring_body_filter": "",
            "series_filter": "",
            "consignment_reference": "",
            "file_name": "",
            "description": "",
            "date_filter_field": "",
            "record_status": "all",
            "sort": "transferring_body",
            "page": 1,
            "per_page": None,
        }

    def test_browse_display_first_page(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        mock_validated_data = {
            "date_from_day": None,
            "date_from_month": None,
            "date_from_year": None,
            "date_to_day": None,
            "date_to_month": None,
            "date_to_year": None,
            "transferring_body_filter": "",
            "series_filter": "",
            "consignment_reference": "",
            "file_name": "",
            "description": "",
            "date_filter_field": "",
            "record_status": "all",
            "sort": "transferring_body",
            "page": 1,
            "per_page": 2,
        }

        result = process_browse_request(
            validated_data=mock_validated_data,
            default_page_size=10,
            transferring_bodies=["body1", "body2"],
        )
        assert result["current_page"] == 1
        assert len(result["results"].items) == 2
        assert result["date_validation_errors"] == {
            "date_from": [],
            "date_to": [],
        }
        assert result["date_error_fields"] == ""
        assert result["transferring_bodies"] == ["body1", "body2"]
        assert result["pagination"] is not None
        assert result["filters"] == {}
        assert result["date_filters"] == {}
        assert result["sorting_orders"] == {"transferring_body": "asc"}
        assert result["num_records_found"] == 27
        assert result["query_string_parameters"] == {
            "consignment_reference": "",
            "date_filter_field": "",
            "date_from_day": None,
            "date_from_month": None,
            "date_from_year": None,
            "date_to_day": None,
            "date_to_month": None,
            "date_to_year": None,
            "description": "",
            "file_name": "",
            "page": 1,
            "per_page": 2,
            "record_status": "all",
            "series_filter": "",
            "sort": "transferring_body",
            "transferring_body_filter": "",
        }

    def test_browse_display_middle_page(
        self, client: FlaskClient, app, mock_all_access_user, browse_files
    ):
        mock_validated_data = {
            "date_from_day": None,
            "date_from_month": None,
            "date_from_year": None,
            "date_to_day": None,
            "date_to_month": None,
            "date_to_year": None,
            "transferring_body_filter": "",
            "series_filter": "",
            "consignment_reference": "",
            "file_name": "",
            "description": "",
            "date_filter_field": "",
            "record_status": "all",
            "sort": "transferring_body",
            "page": 2,
            "per_page": 2,
        }

        result = process_browse_request(
            validated_data=mock_validated_data,
            default_page_size=10,
            transferring_bodies=["body1", "body2"],
        )
        assert result["current_page"] == 2
        assert len(result["results"].items) == 2
        assert result["date_validation_errors"] == {
            "date_from": [],
            "date_to": [],
        }
        assert result["date_error_fields"] == ""
        assert result["transferring_bodies"] == ["body1", "body2"]
        assert result["pagination"] is not None
        assert result["filters"] == {}
        assert result["date_filters"] == {}
        assert result["sorting_orders"] == {"transferring_body": "asc"}
        assert result["num_records_found"] == 27
        assert result["query_string_parameters"] == {
            "consignment_reference": "",
            "date_filter_field": "",
            "date_from_day": None,
            "date_from_month": None,
            "date_from_year": None,
            "date_to_day": None,
            "date_to_month": None,
            "date_to_year": None,
            "description": "",
            "file_name": "",
            "page": 2,
            "per_page": 2,
            "record_status": "all",
            "series_filter": "",
            "sort": "transferring_body",
            "transferring_body_filter": "",
        }

    def test_browse_display_last_page(
        self, client: FlaskClient, app, mock_all_access_user, browse_files
    ):
        mock_validated_data = {
            "date_from_day": None,
            "date_from_month": None,
            "date_from_year": None,
            "date_to_day": None,
            "date_to_month": None,
            "date_to_year": None,
            "transferring_body_filter": "",
            "series_filter": "",
            "consignment_reference": "",
            "file_name": "",
            "description": "",
            "date_filter_field": "",
            "record_status": "all",
            "sort": "transferring_body",
            "page": 3,
            "per_page": 2,
        }
        result = process_browse_request(
            validated_data=mock_validated_data,
            default_page_size=10,
            transferring_bodies=["body1", "body2"],
        )
        assert result["current_page"] == 3
        assert len(result["results"].items) == 2
        assert result["date_validation_errors"] == {
            "date_from": [],
            "date_to": [],
        }
        assert result["date_error_fields"] == ""
        assert result["transferring_bodies"] == ["body1", "body2"]
        assert result["pagination"] is not None
        assert result["filters"] == {}
        assert result["date_filters"] == {}
        assert result["sorting_orders"] == {"transferring_body": "asc"}
        assert result["num_records_found"] == 27
        assert result["query_string_parameters"] == {
            "consignment_reference": "",
            "date_filter_field": "",
            "date_from_day": None,
            "date_from_month": None,
            "date_from_year": None,
            "date_to_day": None,
            "date_to_month": None,
            "date_to_year": None,
            "description": "",
            "file_name": "",
            "page": 3,
            "per_page": 2,
            "record_status": "all",
            "series_filter": "",
            "sort": "transferring_body",
            "transferring_body_filter": "",
        }

    def test_browse_display_multiple_pages(
        self, client: FlaskClient, app, mock_all_access_user, browse_files
    ):
        mock_validated_data = {
            "date_from_day": None,
            "date_from_month": None,
            "date_from_year": None,
            "date_to_day": None,
            "date_to_month": None,
            "date_to_year": None,
            "transferring_body_filter": "",
            "series_filter": "",
            "consignment_reference": "",
            "file_name": "",
            "description": "",
            "date_filter_field": "",
            "record_status": "all",
            "sort": "transferring_body",
            "page": 1,
            "per_page": 2,
        }
        result = process_browse_request(
            validated_data=mock_validated_data,
            default_page_size=10,
            transferring_bodies=["body1", "body2"],
        )
        assert result["current_page"] == 1
        assert len(result["results"].items) == 2
        assert result["date_validation_errors"] == {
            "date_from": [],
            "date_to": [],
        }
        assert result["date_error_fields"] == ""
        assert result["transferring_bodies"] == ["body1", "body2"]
        assert result["pagination"] is not None
        assert result["filters"] == {}
        assert result["date_filters"] == {}
        assert result["sorting_orders"] == {"transferring_body": "asc"}
        assert result["num_records_found"] == 27
        assert result["query_string_parameters"] == {
            "consignment_reference": "",
            "date_filter_field": "",
            "date_from_day": None,
            "date_from_month": None,
            "date_from_year": None,
            "date_to_day": None,
            "date_to_month": None,
            "date_to_year": None,
            "description": "",
            "file_name": "",
            "page": 1,
            "per_page": 2,
            "record_status": "all",
            "series_filter": "",
            "sort": "transferring_body",
            "transferring_body_filter": "",
        }

    def test_browse_submit_search_query(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given an all_access_user accessing the browse page
        When they make a POST request
        Then they should see results in content.
        """
        mock_all_access_user(client)

        query = "test"
        response = client.get(f"{self.route_url}", data={"query": query})

        assert response.status_code == 200

        assert b"Search for digital records" in response.data
        assert b"Browse records 27" in response.data

    def test_browse_invalid_page_redirects_to_default(
        self,
        client: FlaskClient,
    ):
        mock_validated_data = {
            "date_from_day": None,
            "date_from_month": None,
            "date_from_year": None,
            "date_to_day": None,
            "date_to_month": None,
            "date_to_year": None,
            "transferring_body_filter": "",
            "series_filter": "",
            "consignment_reference": "",
            "file_name": "",
            "description": "",
            "date_filter_field": "",
            "record_status": "all",
            "sort": "transferring_body",
            "page": 10,  # Invalid page
            "per_page": 2,
        }

        result = process_browse_request(
            validated_data=mock_validated_data,
            default_page_size=10,
            transferring_bodies=["body1", "body2"],
        )
        if isinstance(result, Response):
            # Assert it's a redirect to page=1
            assert result.status_code == 302
            assert "page=1" in result.location
        else:
            assert result["current_page"] == 1
