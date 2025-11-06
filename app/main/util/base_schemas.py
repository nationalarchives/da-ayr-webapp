"""
Base validation schemas and reusable components.

Contains custom fields, base schemas, and common validation patterns
that can be composed into endpoint-specific schemas.
"""

import uuid

from marshmallow import (
    EXCLUDE,
    Schema,
    ValidationError,
    fields,
    validate,
)


class UUIDField(fields.Field):
    """Custom UUID field for Marshmallow validation."""

    def _serialize(self, value, attr, obj, **kwargs):
        return str(value) if value is not None else None

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return None
        try:
            return value if isinstance(value, uuid.UUID) else uuid.UUID(value)
        except (ValueError, TypeError):
            raise ValidationError("Invalid UUID format")


class PaginationSchema(Schema):
    """Base pagination validation schema."""

    page = fields.Integer(
        allow_none=True,
        load_default=1,
        validate=validate.Range(min=1, max=10000),
    )
    per_page = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, max=100),
    )


class SearchQuerySchema(Schema):
    """Search query validation schema."""

    query = fields.String(
        allow_none=True, load_default="", validate=validate.Length(max=1000)
    )
    search_area = fields.String(
        allow_none=True,
        load_default="everywhere",
        validate=validate.OneOf(["everywhere", "metadata", "record"]),
    )
    sort = fields.String(allow_none=True, load_default="file_name")
    open_all = fields.String(
        allow_none=True,
        load_default="",
        validate=validate.OneOf(["true", "false", "", "open_all"]),
    )
    search_filter = fields.String(
        allow_none=True, load_default="", validate=validate.Length(max=500)
    )

    class Meta:
        unknown = EXCLUDE


class DateFilterSchema(Schema):
    """Date filter validation schema."""

    date_from_day = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, max=31),
    )
    date_from_month = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, max=12),
    )
    date_from_year = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1900, max=2100),
    )
    date_to_day = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, max=31),
    )
    date_to_month = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1, max=12),
    )
    date_to_year = fields.Integer(
        allow_none=True,
        load_default=None,
        validate=validate.Range(min=1900, max=2100),
    )

    def validate_date_range(self, data, **kwargs):
        from_date = data.get("from_date")
        to_date = data.get("to_date")
        if from_date and to_date and from_date > to_date:
            raise ValidationError("from_date must be before to_date")


class BrowseFilterSchema(DateFilterSchema):
    """Browse filter validation schema."""

    transferring_body_filter = fields.String(
        allow_none=True, load_default="", validate=validate.Length(max=200)
    )
    series_filter = fields.String(
        allow_none=True, load_default="", validate=validate.Length(max=200)
    )
    consignment_reference = fields.String(
        allow_none=True, load_default="", validate=validate.Length(max=100)
    )
    file_name = fields.String(
        allow_none=True, load_default="", validate=validate.Length(max=500)
    )
    description = fields.String(
        allow_none=True, load_default="", validate=validate.Length(max=1000)
    )
    date_filter_field = fields.String(
        allow_none=True,
        load_default="",
        validate=validate.OneOf(["date_last_modified", "opening_date", ""]),
    )
    record_status = fields.String(
        allow_none=True,
        load_default="all",
        validate=validate.OneOf(["all", "open", "closed"]),
    )
    sort = fields.String(
        allow_none=True,
        load_default="transferring_body",
        validate=validate.OneOf(
            [
                "transferring_body",
                "series",
                "consignment_reference",
                "date_last_modified",
                "file_name",
                "description",
                "date_of_record-desc",
                "date_of_record-asc",
                "file_name-asc",
                "file_name-desc",
                "opening_date-asc",
                "opening_date-desc",
                "closure_type-asc",
                "closure_type-desc",
                "transferring_body-asc",
                "transferring_body-desc",
                "series-asc",
                "series-desc",
                "last_record_transferred-asc",
                "last_record_transferred-desc",
                "records_held-asc",
                "records_held-desc",
                "date_last_modified-asc",
                "date_last_modified-desc",
                "consignment_reference-asc",
                "consignment_reference-desc",
            ]
        ),
    )
