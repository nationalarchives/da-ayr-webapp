import uuid

import pytest
from marshmallow import ValidationError

from app.main.util.schemas import (
    BrowseConsignmentRequestSchema,
    BrowseRequestSchema,
    BrowseSeriesRequestSchema,
    BrowseTransferringBodyRequestSchema,
    DownloadRequestSchema,
    GenerateManifestRequestSchema,
    RecordRequestSchema,
    SearchRequestSchema,
    SearchResultsSummaryRequestSchema,
    SearchTransferringBodyRequestSchema,
)


class TestRecordRequestSchema:
    """Tests for RecordRequestSchema."""

    def test_valid_record_request(self):
        schema = RecordRequestSchema()
        record_id = str(uuid.uuid4())
        data = schema.load({"record_id": record_id})
        assert isinstance(data["record_id"], uuid.UUID)
        assert str(data["record_id"]) == record_id

    def test_missing_record_id(self):
        schema = RecordRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({})
        assert "record_id" in exc_info.value.messages

    def test_invalid_record_id_format(self):
        schema = RecordRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"record_id": "invalid-uuid"})
        assert "record_id" in exc_info.value.messages

    def test_unknown_fields_excluded(self):
        schema = RecordRequestSchema()
        record_id = str(uuid.uuid4())
        data = schema.load({"record_id": record_id, "unknown_field": "value"})
        assert "unknown_field" not in data


class TestGenerateManifestRequestSchema:
    """Tests for GenerateManifestRequestSchema."""

    def test_valid_manifest_request(self):
        schema = GenerateManifestRequestSchema()
        record_id = str(uuid.uuid4())
        data = schema.load({"record_id": record_id})
        assert isinstance(data["record_id"], uuid.UUID)
        assert str(data["record_id"]) == record_id

    def test_missing_record_id(self):
        schema = GenerateManifestRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({})
        assert "record_id" in exc_info.value.messages

    def test_invalid_record_id_format(self):
        schema = GenerateManifestRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"record_id": "not-a-uuid"})
        assert "record_id" in exc_info.value.messages

    def test_unknown_fields_excluded(self):
        schema = GenerateManifestRequestSchema()
        record_id = str(uuid.uuid4())
        data = schema.load({"record_id": record_id, "extra": "ignored"})
        assert "extra" not in data


class TestDownloadRequestSchema:
    """Tests for DownloadRequestSchema."""

    def test_valid_download_request(self):
        schema = DownloadRequestSchema()
        record_id = str(uuid.uuid4())
        data = schema.load({"record_id": record_id})
        assert isinstance(data["record_id"], uuid.UUID)

    def test_missing_record_id(self):
        schema = DownloadRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({})
        assert "record_id" in exc_info.value.messages

    def test_invalid_record_id(self):
        schema = DownloadRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"record_id": "invalid"})
        assert "record_id" in exc_info.value.messages


class TestBrowseRequestSchema:
    """Tests for BrowseRequestSchema."""

    def test_empty_request(self):
        schema = BrowseRequestSchema()
        data = schema.load({})
        # Should have defaults
        assert data["page"] == 1
        assert "per_page" in data  # Default from config

    def test_valid_pagination(self):
        schema = BrowseRequestSchema()
        data = schema.load({"page": 2, "per_page": 50})
        assert data["page"] == 2
        assert data["per_page"] == 50

    def test_invalid_page_negative(self):
        schema = BrowseRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"page": 0})
        assert "page" in exc_info.value.messages

    def test_invalid_page_too_large(self):
        schema = BrowseRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"page": 10001})
        assert "page" in exc_info.value.messages

    def test_invalid_per_page_negative(self):
        schema = BrowseRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"per_page": 0})
        assert "per_page" in exc_info.value.messages

    def test_invalid_per_page_too_large(self):
        schema = BrowseRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"per_page": 101})
        assert "per_page" in exc_info.value.messages

    def test_date_filters(self):
        schema = BrowseRequestSchema()
        data = schema.load(
            {
                "date_from_day": 1,
                "date_from_month": 1,
                "date_from_year": 2020,
                "date_to_day": 31,
                "date_to_month": 12,
                "date_to_year": 2023,
            }
        )
        assert data["date_from_day"] == 1
        assert data["date_from_year"] == 2020

    def test_invalid_date_values(self):
        schema = BrowseRequestSchema()
        with pytest.raises(ValidationError):
            schema.load({"date_from_day": 32})
        with pytest.raises(ValidationError):
            schema.load({"date_from_month": 13})
        with pytest.raises(ValidationError):
            schema.load({"date_from_year": 1800})

    def test_browse_filters(self):
        schema = BrowseRequestSchema()
        data = schema.load(
            {
                "transferring_body_filter": "Ministry of Defence",
                "series_filter": "ADM 1",
                "consignment_reference": "TDR-2023-ABC",
                "file_name": "test.pdf",
                "description": "Test document",
                "record_status": "open",
                "sort": "file_name",
            }
        )
        assert data["transferring_body_filter"] == "Ministry of Defence"
        assert data["record_status"] == "open"

    def test_invalid_record_status(self):
        schema = BrowseRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"record_status": "invalid"})
        assert "record_status" in exc_info.value.messages

    def test_invalid_sort_field(self):
        schema = BrowseRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"sort": "invalid_sort"})
        assert "sort" in exc_info.value.messages

    def test_string_length_validation(self):
        schema = BrowseRequestSchema()
        # Test max length validation
        with pytest.raises(ValidationError):
            schema.load({"transferring_body_filter": "x" * 201})
        with pytest.raises(ValidationError):
            schema.load({"file_name": "x" * 501})


class TestBrowseTransferringBodyRequestSchema:
    """Tests for BrowseTransferringBodyRequestSchema."""

    def test_valid_request_with_id(self):
        schema = BrowseTransferringBodyRequestSchema()
        test_id = str(uuid.uuid4())
        data = schema.load({"_id": test_id})
        assert isinstance(data["_id"], uuid.UUID)
        assert str(data["_id"]) == test_id

    def test_missing_required_id(self):
        schema = BrowseTransferringBodyRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({})
        assert "_id" in exc_info.value.messages

    def test_invalid_uuid_format(self):
        schema = BrowseTransferringBodyRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"_id": "not-a-uuid"})
        assert "_id" in exc_info.value.messages

    def test_with_pagination_and_filters(self):
        schema = BrowseTransferringBodyRequestSchema()
        test_id = str(uuid.uuid4())
        data = schema.load(
            {
                "_id": test_id,
                "page": 2,
                "per_page": 25,
                "series_filter": "Test Series",
            }
        )
        assert data["page"] == 2
        assert data["series_filter"] == "Test Series"


class TestBrowseSeriesRequestSchema:
    """Tests for BrowseSeriesRequestSchema."""

    def test_valid_series_request(self):
        schema = BrowseSeriesRequestSchema()
        test_id = str(uuid.uuid4())
        data = schema.load({"_id": test_id, "page": 1})
        assert isinstance(data["_id"], uuid.UUID)
        assert data["page"] == 1

    def test_missing_series_id(self):
        schema = BrowseSeriesRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"page": 1})
        assert "_id" in exc_info.value.messages


class TestBrowseConsignmentRequestSchema:
    """Tests for BrowseConsignmentRequestSchema."""

    def test_valid_consignment_request(self):
        schema = BrowseConsignmentRequestSchema()
        test_id = str(uuid.uuid4())
        data = schema.load({"_id": test_id})
        assert isinstance(data["_id"], uuid.UUID)

    def test_missing_consignment_id(self):
        schema = BrowseConsignmentRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({})
        assert "_id" in exc_info.value.messages


class TestSearchRequestSchema:
    """Tests for SearchRequestSchema."""

    def test_empty_search_request(self):
        schema = SearchRequestSchema()
        data = schema.load({})
        assert data["query"] == ""
        assert data["search_area"] == "everywhere"

    def test_valid_search_parameters(self):
        schema = SearchRequestSchema()
        data = schema.load(
            {
                "query": "test query",
                "search_area": "metadata",
                "sort": "file_name",
                "open_all": "true",
                "search_filter": "filter text",
                "transferring_body_id": "test-id",
            }
        )
        assert data["query"] == "test query"
        assert data["search_area"] == "metadata"
        assert data["transferring_body_id"] == "test-id"

    def test_invalid_search_area(self):
        schema = SearchRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"search_area": "invalid"})
        assert "search_area" in exc_info.value.messages

    def test_invalid_open_all_value(self):
        schema = SearchRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"open_all": "invalid"})
        assert "open_all" in exc_info.value.messages

    def test_query_length_validation(self):
        schema = SearchRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"query": "x" * 1001})
        assert "query" in exc_info.value.messages

    def test_search_filter_length_validation(self):
        schema = SearchRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"search_filter": "x" * 501})
        assert "search_filter" in exc_info.value.messages

    def test_transferring_body_id_length_validation(self):
        schema = SearchRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"transferring_body_id": "x" * 201})
        assert "transferring_body_id" in exc_info.value.messages


class TestSearchResultsSummaryRequestSchema:
    """Tests for SearchResultsSummaryRequestSchema."""

    def test_valid_summary_request(self):
        schema = SearchResultsSummaryRequestSchema()
        data = schema.load({"query": "test", "page": 1, "per_page": 20})
        assert data["query"] == "test"
        assert data["page"] == 1

    def test_defaults_applied(self):
        schema = SearchResultsSummaryRequestSchema()
        data = schema.load({})
        assert data["query"] == ""
        assert data["page"] == 1


class TestSearchTransferringBodyRequestSchema:
    """Tests for SearchTransferringBodyRequestSchema."""

    def test_valid_request_with_id(self):
        schema = SearchTransferringBodyRequestSchema()
        test_id = str(uuid.uuid4())
        data = schema.load({"_id": test_id, "query": "search term"})
        assert isinstance(data["_id"], uuid.UUID)
        assert data["query"] == "search term"

    def test_optional_id_field(self):
        schema = SearchTransferringBodyRequestSchema()
        data = schema.load({"query": "test"})
        assert data["_id"] is None
        assert data["query"] == "test"

    def test_invalid_uuid_in_id(self):
        schema = SearchTransferringBodyRequestSchema()
        with pytest.raises(ValidationError) as exc_info:
            schema.load({"_id": "invalid-uuid"})
        assert "_id" in exc_info.value.messages

    def test_with_pagination(self):
        schema = SearchTransferringBodyRequestSchema()
        data = schema.load({"query": "test", "page": 3, "per_page": 10})
        assert data["page"] == 3
        assert data["per_page"] == 10
