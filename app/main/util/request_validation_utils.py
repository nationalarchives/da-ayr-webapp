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
                    request.validated_data, schema, data
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

        # Block Flask reserved parameters that start with underscore
        # These are special parameters for url_for() and could be used for attacks:
        # _external, _scheme, _anchor, _method, etc.
        if field_name.startswith("_"):
            continue

        # Only include if the field was explicitly provided in original data
        # (regardless of whether it matches the default value)
        if field_name in original_data and value is not None and value != "":
            filtered[field_name] = value

    return filtered


def sanitize_url_params(params: dict) -> dict:
    """
    Remove Flask reserved parameters from a dict to prevent parameter pollution.

    Flask's url_for() accepts special parameters starting with underscore:
    - _external: Generate absolute URL
    - _scheme: URL scheme (http/https)
    - _anchor: URL fragment
    - _method: HTTP method

    Args:
        params: Dictionary of URL parameters

    Returns:
        Sanitised dictionary with Flask reserved parameters removed
    """
    return {k: v for k, v in params.items() if not k.startswith("_")}
