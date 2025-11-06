import pytest
from marshmallow import Schema, ValidationError, fields

from app.main.util.base_schemas import (
    BrowseFilterSchema,
    DateFilterSchema,
    PaginationSchema,
    SearchQuerySchema,
    UUIDField,
)


def test_pagination_schema_defaults():
    schema = PaginationSchema()
    data = schema.load({})
    assert data["page"] == 1
    assert (
        data["per_page"] is None
    )  # Should be None, services handle the config fallback


def test_pagination_schema_custom_values():
    schema = PaginationSchema()
    data = schema.load({"page": 5, "per_page": 10})
    assert data["page"] == 5
    assert data["per_page"] == 10


def test_search_query_schema_defaults():
    schema = SearchQuerySchema()
    data = schema.load({})
    assert data == {
        "query": "",
        "search_area": "everywhere",
        "sort": "file_name",
        "open_all": "",
        "search_filter": "",
    }


def test_search_query_schema_invalid_search_area():
    schema = SearchQuerySchema()
    with pytest.raises(ValidationError):
        schema.load({"search_area": "invalid"})


def test_date_filter_schema_valid_dates():
    schema = DateFilterSchema()
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
    schema = DateFilterSchema()
    with pytest.raises(
        ValidationError, match="from_date must be before to_date"
    ):
        schema.validate_date_range(data)


def test_date_filter_schema_invalid_day():
    schema = DateFilterSchema()
    with pytest.raises(ValidationError):
        schema.load({"date_from_day": 32})


def test_browse_filter_schema_defaults():
    schema = BrowseFilterSchema()
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
    schema = BrowseFilterSchema()
    with pytest.raises(ValidationError):
        schema.load({"sort": "invalid_sort"})


def test_uuidfield_serialize_none():
    field = UUIDField()
    result = field._serialize(None, attr=None, obj=None)
    assert result is None


def test_uuidfield_deserialize_invalid():
    field = UUIDField()
    with pytest.raises(ValidationError, match="Invalid UUID format"):
        field._deserialize("not-a-uuid", attr=None, data=None)


class DummySchema(Schema):
    field = fields.String(required=True)
