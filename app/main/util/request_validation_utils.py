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
                # Store validated data without defaults for cleaner redirect URLs
                request.validated_data_non_defaults = _filter_non_defaults(
                    request.validated_data, schema
                )
            except ValidationError as e:
                current_app.logger.warning(
                    f"Validation error in {f.__name__}: {e.messages}"
                )
                abort(
                    400, description=f"Invalid request parameters: {e.messages}"
                )

            return f(*args, **kwargs)

        return wrapper

    return decorator


def _clean_empty_strings(data: dict) -> dict:
    """
    Converts empty string values in a dict to None.
    Useful for query/form data before Marshmallow validation.
    """
    return {k: (None if v == "" else v) for k, v in data.items()}


def _filter_non_defaults(validated_data: dict, schema: Schema) -> dict:
    """
    Filter out fields that have default values to keep redirect URLs clean.
    Only returns fields that were explicitly provided and differ from defaults.
    """
    filtered = {}

    for field_name, value in validated_data.items():
        field = schema.fields.get(field_name)
        if field is None:
            continue

        # Get the default value for this field
        default_value = getattr(field, "load_default", None)

        # Only include if value differs from default and isn't None/empty
        if value != default_value and value is not None and value != "":
            filtered[field_name] = value

    return filtered
