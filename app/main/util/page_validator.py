"""
Request validation schemas using Marshmallow.

This module defines validation schemas for all route parameters and query strings
to prevent security vulnerabilities from invalid input data.
"""

import uuid

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


class UUIDField(fields.Field):
    """Custom UUID field for Marshmallow validation."""

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return str(value)

    def _deserialize(self, value, attr, data, **kwargs):
        if not value:
            return None
        try:
            # Handle both string and UUID object inputs
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(value)
        except (ValueError, TypeError):
            raise MarshmallowValidationError("Invalid UUID format")


class PaginationSchema(Schema):
    """Base pagination validation schema."""

    page = fields.Integer(
        load_default=1, validate=validate.Range(min=1, max=10000)
    )
    per_page = fields.Integer(validate=validate.Range(min=1, max=100))

    @post_load
    def set_per_page_default(self, data, **kwargs):
        """Set per_page default from application config if not provided."""
        if "per_page" not in data:
            from flask import current_app

            data["per_page"] = int(
                current_app.config.get("DEFAULT_PAGE_SIZE", 20)
            )
        return data


class SearchQuerySchema(Schema):
    """Search query validation schema."""

    query = fields.String(load_default="", validate=validate.Length(max=1000))
    search_area = fields.String(
        load_default="everywhere",
        validate=validate.OneOf(["everywhere", "metadata", "record"]),
    )
    sort = fields.String(load_default="file_name")
    open_all = fields.String(
        load_default="",
        validate=validate.OneOf(["true", "false", "", "open_all"]),
    )
    search_filter = fields.String(
        load_default="", validate=validate.Length(max=500)
    )

    class Meta:
        unknown = EXCLUDE


class DateFilterSchema(Schema):
    """Date filter validation schema."""

    # Individual date components (used by browse forms)
    date_from_day = fields.Integer(
        load_default=None, validate=validate.Range(min=1, max=31)
    )
    date_from_month = fields.Integer(
        load_default=None, validate=validate.Range(min=1, max=12)
    )
    date_from_year = fields.Integer(
        load_default=None, validate=validate.Range(min=1900, max=2100)
    )
    date_to_day = fields.Integer(
        load_default=None, validate=validate.Range(min=1, max=31)
    )
    date_to_month = fields.Integer(
        load_default=None, validate=validate.Range(min=1, max=12)
    )
    date_to_year = fields.Integer(
        load_default=None, validate=validate.Range(min=1900, max=2100)
    )

    def validate_date_range(self, data, **kwargs):
        """Validate that from_date is before to_date."""
        from_date = data.get("from_date")
        to_date = data.get("to_date")

        if from_date and to_date and from_date > to_date:
            raise MarshmallowValidationError("from_date must be before to_date")


class BrowseFilterSchema(DateFilterSchema):
    """Browse filter validation schema."""

    transferring_body_filter = fields.String(
        load_default="", validate=validate.Length(max=200)
    )
    series_filter = fields.String(
        load_default="", validate=validate.Length(max=200)
    )
    consignment_reference = fields.String(
        load_default="", validate=validate.Length(max=100)
    )
    file_name = fields.String(
        load_default="", validate=validate.Length(max=500)
    )
    description = fields.String(
        load_default="", validate=validate.Length(max=1000)
    )

    # Consignment-specific fields
    date_filter_field = fields.String(
        load_default="",
        validate=validate.OneOf(["date_last_modified", "opening_date", ""]),
    )
    record_status = fields.String(
        load_default="all", validate=validate.OneOf(["all", "open", "closed"])
    )

    sort = fields.String(
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


class BrowseRequestSchema(PaginationSchema, BrowseFilterSchema):
    """Complete browse request validation schema."""

    class Meta:
        unknown = EXCLUDE


class SearchTransferringBodySchema(PaginationSchema, SearchQuerySchema):
    """Search transferring body request validation schema."""

    _id = UUIDField(
        required=False, data_key="_id", load_default=None
    )


class SearchRequestSchema(SearchQuerySchema):
    """General search request validation schema."""

    transferring_body_id = fields.String(
        load_default=None, validate=validate.Length(max=200)
    )

    class Meta:
        unknown = EXCLUDE


class SearchResultsSummarySchema(PaginationSchema, SearchQuerySchema):
    """Search results summary request validation schema."""

    pass


class BrowseTransferringBodySchema(PaginationSchema, BrowseFilterSchema):
    """Browse transferring body request validation schema."""

    _id = UUIDField(required=True, data_key="_id")


class BrowseSeriesSchema(PaginationSchema, BrowseFilterSchema):
    """Browse series request validation schema."""

    _id = UUIDField(required=True, data_key="_id")


class BrowseConsignmentSchema(PaginationSchema, BrowseFilterSchema):
    """Browse consignment request validation schema."""

    _id = UUIDField(required=True, data_key="_id")


class RecordRequestSchema(Schema):
    """Record detail request validation schema."""

    record_id = UUIDField(required=True)


class DownloadRequestSchema(Schema):
    """Download request validation schema."""

    record_id = UUIDField(required=True)


class ManifestRequestSchema(Schema):
    """Manifest request validation schema."""

    record_id = UUIDField(required=True)


class ValidationError(Exception):
    """Custom validation error for the application."""

    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(message)


class ManifestSchema(Schema):
    """Schema for manifest generation parameters."""

    record_id = UUIDField(
        required=True, error_messages={"required": "Record ID is required"}
    )

    class Meta:
        unknown = EXCLUDE


# Schema validation decorator
def validate_request(schema_class, location="args"):
    """
    Decorator to validate request data using Marshmallow schemas.

    Args:
        schema_class: The Marshmallow schema class to use for validation
        location: Where to get data from ('args', 'form', 'json', 'path')

    Returns:
        Decorated function with validated data available in request.validated_data
    """
    def decorator(f):
        import functools
        def wrapper(*args, **kwargs):
            from flask import abort, request

            # Get data based on location
            if location == "args":
                data = request.args.to_dict()
            elif location == "form":
                data = request.form.to_dict()
            elif location == "json":
                data = request.get_json() or {}
            elif location == "path":
                data = kwargs
            elif location == "combined":
                # Combine form and args data (args take precedence)
                data = {
                    **kwargs,
                    **request.form.to_dict(),
                    **request.args.to_dict(),
                }
            else:
                data = {}

            # Validate data
            schema = schema_class()
            try:
                validated_data = schema.load(data)
                request.validated_data = validated_data
            except MarshmallowValidationError as e:
                # Log validation error for security monitoring
                from flask import current_app

                current_app.logger.warning(
                    f"Validation error in {f.__name__}: {e.messages}"
                )
                abort(
                    400, description=f"Invalid request parameters: {e.messages}"
                )

            return f(*args, **kwargs)

        return functools.wraps(f)(wrapper)

    return decorator
