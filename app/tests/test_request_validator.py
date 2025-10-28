import uuid

import pytest
from flask import Flask
from marshmallow import ValidationError as MarshmallowValidationError

import app.main.util.request_validator as rv


@pytest.fixture
def dummy_app(monkeypatch):
    class DummyApp:
        config = {"DEFAULT_PAGE_SIZE": 42}

    monkeypatch.setattr("flask.current_app", DummyApp())


def test_pagination_schema_defaults(dummy_app):
    schema = rv.PaginationSchema()
    data = schema.load({})
    assert data["page"] == 1
    assert data["per_page"] == 42


@pytest.fixture
def dummy_app_custom(monkeypatch):
    class DummyApp:
        config = {"DEFAULT_PAGE_SIZE": 99}

    monkeypatch.setattr("flask.current_app", DummyApp())


def test_pagination_schema_custom_values(dummy_app_custom):
    schema = rv.PaginationSchema()
    data = schema.load({"page": 5, "per_page": 10})
    assert data["page"] == 5
    assert data["per_page"] == 10


def test_search_query_schema_defaults():
    schema = rv.SearchQuerySchema()
    data = schema.load({})
    assert data == {
        "query": "",
        "search_area": "everywhere",
        "sort": "file_name",
        "open_all": "",
        "search_filter": "",
    }


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


@pytest.mark.parametrize(
    "data",
    [
        {
            "date_from_day": 2,
            "date_from_month": 1,
            "date_from_year": 2021,
            "date_to_day": 1,
            "date_to_month": 1,
            "date_to_year": 2021,
            "from_date": "2021-01-02",
            "to_date": "2021-01-01",
        },
        {
            "from_date": "2021-01-02",
            "to_date": "2021-01-01",
        },
    ],
)
def test_date_filter_schema_invalid_date_range(data):
    schema = rv.DateFilterSchema()
    with pytest.raises(
        MarshmallowValidationError, match="from_date must be before to_date"
    ):
        schema.validate_date_range(data)


def test_date_filter_schema_invalid_day():
    schema = rv.DateFilterSchema()
    with pytest.raises(MarshmallowValidationError):
        schema.load({"date_from_day": 32})


def test_browse_filter_schema_defaults():
    schema = rv.BrowseFilterSchema()
    data = schema.load({})
    assert data == {
        "transferring_body_filter": "",
        "series_filter": "",
        "consignment_reference": "",
        "file_name": "",
        "description": "",
        "date_filter_field": "",
        "record_status": "all",
        "sort": "transferring_body",
        "date_from_day": None,
        "date_from_month": None,
        "date_from_year": None,
        "date_to_day": None,
        "date_to_month": None,
        "date_to_year": None,
    }


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


def test_uuidfield_serialize_none():
    field = rv.UUIDField()
    result = field._serialize(None, attr=None, obj=None)
    assert result is None


def test_uuidfield_deserialize_invalid():
    field = rv.UUIDField()
    with pytest.raises(
        rv.MarshmallowValidationError, match="Invalid UUID format"
    ):
        field._deserialize("not-a-uuid", attr=None, data=None)


class DummySchema(rv.Schema):
    field = rv.fields.String(required=True)


def make_app_with_route(location, schema_class=DummySchema, data=None):
    """Helper to create Flask app and test client for request validation."""
    app = Flask(__name__)

    @app.route("/test", methods=["GET", "POST"])
    @rv.validate_request(schema_class, location=location)
    def test_route(**kwargs):
        return "ok"

    client = app.test_client()
    if location == "args":
        resp = client.get("/test", query_string=data or {"field": "value"})
    elif location == "form":
        resp = client.post("/test", data=data or {"field": "value"})
    elif location == "json":
        resp = client.post("/test", json=data or {"field": "value"})
    elif location == "path":
        # Flask path params need a real route, skip direct test
        return None
    elif location == "combined":
        resp = client.post("/test?field=value", data=data or {"field": "value"})
    else:
        resp = client.get("/test")
    return resp


def test_validate_request_args():
    resp = make_app_with_route("args")
    assert resp.status_code == 200


def test_validate_request_form():
    resp = make_app_with_route("form")
    assert resp.status_code == 200


def test_validate_request_json():
    resp = make_app_with_route("json")
    assert resp.status_code == 200


def test_validate_request_combined():
    resp = make_app_with_route("combined")
    assert resp.status_code == 200


def test_validate_request_invalid_request():
    resp = make_app_with_route("unknown", data={})
    assert resp.status_code == 400
    assert b"Invalid request parameters" in resp.data
