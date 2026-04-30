"""
Validation utilities and decorators.

Contains helper functions and decorators for request validation,
including the main validation decorator used across endpoints.
"""

import functools
from typing import Callable, Type

from flask import redirect, url_for
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
                request.validated_args = _filter_non_defaults(
                    request.validated_data, schema, data
                )
            except ValidationError as e:
                current_app.logger.warning(
                    f"Validation error in {f.__name__}: {e.messages}"
                )
                # Set default_data based on incoming data, fallback to hardcoded defaults
                default_data = {
                    "query": data.get("query", ""),
                    "search_area": data.get("search_area", "everywhere"),
                    "date_from_day": data.get("date_from_day", None),
                    "date_from_month": data.get("date_from_month", None),
                    "date_from_year": data.get("date_from_year", None),
                    "date_to_day": data.get("date_to_day", None),
                    "date_to_month": data.get("date_to_month", None),
                    "date_to_year": data.get("date_to_year", None),
                    "transferring_body_filter": data.get(
                        "transferring_body_filter", ""
                    ),
                    "series_filter": data.get("series_filter", ""),
                    "consignment_reference": data.get(
                        "consignment_reference", ""
                    ),
                    "file_name": data.get("file_name", ""),
                    "description": data.get("description", ""),
                    "date_filter_field": data.get("date_filter_field", ""),
                    "record_status": data.get("record_status", "all"),
                    "sort": data.get("sort", "transferring_body"),
                    "page": None,
                    "per_page": data.get("per_page", None),
                    "_id": data.get("_id", None),
                }
                # Validate and handle 'page' param
                page_val = data.get("page")
                try:
                    page_val = int(page_val)
                    if page_val < 1:
                        raise ValueError
                except (TypeError, ValueError):
                    # Use current endpoint and args, but set page=1
                    args = request.args.to_dict()
                    args["page"] = 1
                    return redirect(url_for(request.endpoint, **args))
                default_data["page"] = page_val
                request.validated_data = schema.load(default_data)
                request.validated_args = _filter_non_defaults(
                    request.validated_data, schema, default_data
                )
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


def _filter_non_defaults(
    validated_data: dict, schema: Schema, original_data: dict
) -> dict:
    """
    Filter out fields that have default values to keep redirect URLs clean.
    Only returns fields that were explicitly provided in the original request.
    """
    filtered = {}

    for field_name, value in validated_data.items():
        field = schema.fields.get(field_name)
        if field is None:
            continue

        # Only include if the field was explicitly provided in original data
        # (regardless of whether it matches the default value)
        if field_name in original_data and value is not None and value != "":
            filtered[field_name] = value
    return filtered
