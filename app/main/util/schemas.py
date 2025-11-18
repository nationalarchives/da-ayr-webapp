"""
Request validation schemas using Marshmallow.

Defines validation schemas for route parameters and query strings
to prevent vulnerabilities from invalid input data.
"""

from marshmallow import (
    EXCLUDE,
    Schema,
    fields,
    validate,
)

from app.main.util.base_schemas import (
    BrowseFilterSchema,
    PaginationSchema,
    SearchQuerySchema,
    UUIDField,
)


class CallbackRequestSchema(Schema):
    """OIDC callback request validation schema."""

    code = fields.String(
        allow_none=True,
        load_default=None,
        validate=validate.Length(min=1, max=500),
    )

    class Meta:
        unknown = EXCLUDE


class BrowseRequestSchema(PaginationSchema, BrowseFilterSchema):
    """Browse request validation schema."""

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

    _id = UUIDField(required=True, data_key="_id")

    class Meta:
        unknown = EXCLUDE


class RecordRequestSchema(Schema):
    """Record detail request validation schema."""

    record_id = UUIDField(required=True)

    class Meta:
        unknown = EXCLUDE


class DownloadRequestSchema(Schema):
    """Download request validation schema."""

    record_id = UUIDField(required=True)

    class Meta:
        unknown = EXCLUDE


class GenerateManifestRequestSchema(Schema):
    """Schema for manifest generation parameters."""

    record_id = UUIDField(required=True)

    class Meta:
        unknown = EXCLUDE
