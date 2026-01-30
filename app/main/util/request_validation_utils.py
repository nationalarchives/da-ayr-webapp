"""
Validation utilities and decorators.

Contains helper functions and decorators for request validation,
including the main validation decorator used across endpoints.
"""

import functools
from typing import Callable, Type

from marshmallow import Schema, ValidationError


def validate_request(
    schema_class: Type[Schema], location: str = "args"
) -> Callable:
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            from flask import current_app, request

            data = _get_request_data(location, request, kwargs)
            schema = schema_class()
            try:
                request.validated_data = schema.load(data)
                # Store validated data without defaults for cleaner redirect URLs
                request.validated_args = _filter_non_defaults(
                    request.validated_data, schema, data
                )
            except ValidationError as e:
                current_app.logger.warning(
                    f"Validation error in {f.__name__}: {e.messages}"
                )
                request.validated_data = _fallback_to_defaults(schema, data)
            return f(*args, **kwargs)

        return wrapper

    return decorator


def _get_request_data(location, request, kwargs):
    if location == "args":
        return _clean_empty_strings(request.args.to_dict())
    elif location == "form":
        return _clean_empty_strings(request.form.to_dict())
    elif location == "json":
        return request.get_json() or {}
    elif location == "path":
        return kwargs
    elif location == "combined":
        combined = {
            **kwargs,
            **request.form.to_dict(),
            **request.args.to_dict(),
        }
        return _clean_empty_strings(combined)
    else:
        return {}


def _fallback_to_defaults(schema, data):
    valid_data = {}
    for field_name, field in schema.fields.items():
        if field_name in data:
            try:
                valid_data[field_name] = field.deserialize(data[field_name])
            except Exception:
                valid_data[field_name] = (
                    field.load_default
                    if hasattr(field, "load_default")
                    else None
                )
        else:
            valid_data[field_name] = (
                field.load_default if hasattr(field, "load_default") else None
            )
    return valid_data


def _clean_empty_strings(data: dict) -> dict:
    """
    Converts empty string values in a dict to None.
    Useful for query/form data before Marshmallow validation.
    """
    return {k: (None if v == "" else v) for k, v in data.items()}


# Flask reserved parameters that could be exploited in url_for() calls
# These should never be passed through from user input
FLASK_RESERVED_PARAMS = frozenset(
    {"_external", "_anchor", "_scheme", "_method", "_netloc"}
)


def _filter_non_defaults(
    validated_data: dict, schema: Schema, original_data: dict
) -> dict:
    """
    Filter out fields that have default values to keep redirect URLs clean.
    Only returns fields that were explicitly provided in the original request.

    Filters out Flask reserved parameters to prevent parameter
    pollution attacks in url_for() calls.
    """
    filtered = {}

    for field_name, value in validated_data.items():
        field = schema.fields.get(field_name)
        if field is None:
            continue

        # Block Flask reserved parameters that could be used for attacks
        if field_name in FLASK_RESERVED_PARAMS:
            continue

        # Only include if the field was explicitly provided in original data
        # (regardless of whether it matches the default value)
        if field_name in original_data and value is not None and value != "":
            filtered[field_name] = value
    return filtered
