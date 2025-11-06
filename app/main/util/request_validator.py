"""
Request validation schemas using Marshmallow.

Defines validation schemas for route parameters and query strings
to prevent vulnerabilities from invalid input data.
"""

import functools
import uuid
from typing import Callable, Type

from marshmallow import (
    EXCLUDE,
    Schema,
)
from marshmallow import ValidationError as MarshmallowValidationError
from marshmallow import (
    fields,
    post_load,
    validate,
)


# Custom UUID field
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
            raise MarshmallowValidationError("Invalid UUID format")


class PaginationSchema(Schema):
    """Base pagination validation schema."""

    page = fields.Integer(
        allow_none=True,
        load_default=1,
        validate=validate.Range(min=1, max=10000),
    )
    per_page = fields.Integer(
        allow_none=True, validate=validate.Range(min=1, max=100)
    )

    @post_load
    def set_per_page_default(self, data, **kwargs):
        if "per_page" not in data:
            from flask import current_app

            data["per_page"] = int(
                current_app.config.get("DEFAULT_PAGE_SIZE", 20)
            )
        return data


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
            raise MarshmallowValidationError("from_date must be before to_date")


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


# Endpoint schemas


class BrowseRequestSchema(PaginationSchema, BrowseFilterSchema):
    """Complete browse request validation schema."""

    class Meta:
        unknown = EXCLUDE


class BrowseTransferringBodyRequestSchema(PaginationSchema, BrowseFilterSchema):
    """Browse transferring body request validation schema."""

    _id = UUIDField(required=True, data_key="_id")

    class Meta:
        unknown = EXCLUDE


class BrowseSeriesRequestSchema(PaginationSchema, BrowseFilterSchema):
    """Browse series request validation schema."""

    _id = UUIDField(required=True, data_key="_id")

    class Meta:
        unknown = EXCLUDE


class BrowseConsignmentRequestSchema(PaginationSchema, BrowseFilterSchema):
    """Browse consignment request validation schema."""

    _id = UUIDField(required=True, data_key="_id")

    class Meta:
        unknown = EXCLUDE


class SearchRequestSchema(SearchQuerySchema):
    """General search request validation schema."""

    transferring_body_id = fields.String(
        allow_none=True, load_default=None, validate=validate.Length(max=200)
    )

    class Meta:
        unknown = EXCLUDE


class SearchResultsSummaryRequestSchema(PaginationSchema, SearchQuerySchema):
    """Search results summary request validation schema."""

    class Meta:
        unknown = EXCLUDE


class SearchTransferringBodyRequestSchema(PaginationSchema, SearchQuerySchema):
    """Search transferring body request validation schema."""

    _id = UUIDField(required=False, data_key="_id", load_default=None)

    class Meta:
        unknown = EXCLUDE


class RecordRequestSchema(Schema):
    """Record detail request validation schema."""

    record_id = UUIDField(required=True)


class DownloadRequestSchema(Schema):
    """Download request validation schema."""

    record_id = UUIDField(required=True)


class GenerateManifestRequestSchema(Schema):
    """Schema for manifest generation parameters."""

    record_id = UUIDField(
        required=True, error_messages={"required": "Record ID is required"}
    )

    class Meta:
        unknown = EXCLUDE


class ValidationError(Exception):
    """Custom validation error for the application."""

    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)


def _clean_empty_strings(data: dict) -> dict:
    """
    Converts empty string values in a dict to None.
    Useful for query/form data before Marshmallow validation.
    """
    return {k: (None if v == "" else v) for k, v in data.items()}


def validate_request(
    schema_class: Type[Schema], location: str = "args"
) -> Callable:
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            from flask import abort, current_app, request

            if location == "args":
                data = _clean_empty_strings(request.args.to_dict())
            elif location == "form":
                data = _clean_empty_strings(request.form.to_dict())
            elif location == "json":
                data = request.get_json() or {}
            elif location == "path":
                data = kwargs
            elif location == "combined":
                combined = {
                    **kwargs,
                    **request.form.to_dict(),
                    **request.args.to_dict(),
                }
                data = _clean_empty_strings(combined)
            else:
                data = {}

            schema = schema_class()
            try:
                request.validated_data = schema.load(data)
            except MarshmallowValidationError as e:
                current_app.logger.warning(
                    f"Validation error in {f.__name__}: {e.messages}"
                )
                abort(
                    400, description=f"Invalid request parameters: {e.messages}"
                )

            return f(*args, **kwargs)

        return wrapper

    return decorator
