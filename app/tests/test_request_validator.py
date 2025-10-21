import uuid

import pytest
from marshmallow import ValidationError as MarshmallowValidationError

import app.main.util.request_validator as rv


def test_pagination_schema_defaults(monkeypatch):
    class DummyApp:
        config = {"DEFAULT_PAGE_SIZE": 42}

    monkeypatch.setattr("flask.current_app", DummyApp())
    schema = rv.PaginationSchema()
    data = schema.load({})
    assert data["page"] == 1
    assert data["per_page"] == 42


def test_pagination_schema_custom_values(monkeypatch):
    class DummyApp:
        config = {"DEFAULT_PAGE_SIZE": 99}

    monkeypatch.setattr("flask.current_app", DummyApp())
    schema = rv.PaginationSchema()
    data = schema.load({"page": 5, "per_page": 10})
    assert data["page"] == 5
    assert data["per_page"] == 10


def test_search_query_schema_defaults():
    schema = rv.SearchQuerySchema()
    data = schema.load({})
    assert data["query"] == ""
    assert data["query"] != "test"
    assert data["search_area"] == "everywhere"
    assert data["sort"] == "file_name"
    assert data["open_all"] == ""
    assert data["search_filter"] == ""


def test_search_query_schema_invalid_search_area():
    schema = rv.SearchQuerySchema()
    with pytest.raises(MarshmallowValidationError):
        schema.load({"search_area": "invalid"})


def test_date_filter_schema_valid_dates():
    schema = rv.DateFilterSchema()
    data = schema.load(
        {
            "date_from_day": 1,
            "date_from_month": 1,
            "date_from_year": 2000,
            "date_to_day": 31,
            "date_to_month": 12,
            "date_to_year": 2020,
        }
    )
    assert data["date_from_day"] == 1
    assert data["date_to_year"] == 2020
    assert data["date_to_year"] != 2323


def test_date_filter_schema_invalid_day():
    schema = rv.DateFilterSchema()
    with pytest.raises(MarshmallowValidationError):
        schema.load({"date_from_day": 32})


def test_browse_filter_schema_defaults():
    schema = rv.BrowseFilterSchema()
    data = schema.load({})
    assert data["transferring_body_filter"] == ""
    assert data["series_filter"] == ""
    assert data["consignment_reference"] == ""
    assert data["consignment_reference"] != "cons123"
    assert data["file_name"] == ""
    assert data["file_name"] != "file.pdf"
    assert data["description"] == ""
    assert data["date_filter_field"] == ""
    assert data["record_status"] == "all"
    assert data["sort"] == "transferring_body"


def test_browse_filter_schema_invalid_sort():
    schema = rv.BrowseFilterSchema()
    with pytest.raises(MarshmallowValidationError):
        schema.load({"sort": "invalid_sort"})


def test_record_request_schema_valid():
    schema = rv.RecordRequestSchema()
    record_id = str(uuid.uuid4())
    data = schema.load({"record_id": record_id})
    assert isinstance(data["record_id"], uuid.UUID)


def test_record_request_schema_missing():
    schema = rv.RecordRequestSchema()
    with pytest.raises(MarshmallowValidationError):
        schema.load({})


def test_manifest_schema_valid():
    schema = rv.ManifestSchema()
    record_id = str(uuid.uuid4())
    data = schema.load({"record_id": record_id})
    assert isinstance(data["record_id"], uuid.UUID)


def test_manifest_schema_missing():
    schema = rv.ManifestSchema()
    with pytest.raises(MarshmallowValidationError):
        schema.load({})


def test_validation_error_custom_message():
    err = rv.ValidationError("Custom error", field="field_name")
    assert err.message == "Custom error"
    assert err.field == "field_name"
