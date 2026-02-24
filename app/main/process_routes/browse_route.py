from flask import request
from sqlalchemy import func
from werkzeug.exceptions import NotFound

from app.main.db.models import db
from app.main.db.queries import build_browse_query
from app.main.util.date_filters_validator import validate_date_filters
from app.main.util.filter_sort_builder import (
    build_filters,
    build_sorting_orders,
)
from app.main.util.page_utils import redirect_if_page_invalid
from app.main.util.pagination import get_pagination


def process_browse_request(
    validated_data, default_page_size, transferring_bodies
):
    """
    Process the browse request for all-access users.
    Args:
        validated_data: dict of validated request data
        default_page_size: int, default page size from config
        transferring_bodies: list of transferring body names
    Returns:
        dict of data for rendering browse.html
    """
    page = validated_data["page"]
    per_page = validated_data["per_page"] or default_page_size

    default_page = 1
    date_validation_errors = []
    from_date = None
    to_date = None
    date_filters = {}
    date_error_fields = []
    if len(validated_data) > 0:
        (
            date_validation_errors,
            from_date,
            to_date,
            date_filters,
            date_error_fields,
        ) = validate_date_filters(validated_data)
    filters = build_filters(
        validated_data,
        date_from=from_date,
        date_to=to_date,
    )
    sorting_orders = build_sorting_orders(validated_data)
    if len(sorting_orders) == 0:
        sorting_orders["transferring_body"] = "asc"
    query = build_browse_query(
        filters=filters,
        sorting_orders=sorting_orders,
    )
    try:
        browse_results = query.paginate(page=page, per_page=per_page)
    except NotFound:
        # Redirect to first page if page does not exist
        return redirect_if_page_invalid(page, default_page, "main.browse")
    total_records = db.session.query(
        func.sum(query.subquery().c.records_held)
    ).scalar()
    if total_records:
        num_records_found = total_records
    else:
        num_records_found = 0
    pagination = get_pagination(page, browse_results.pages)

    # Use validated_args if available, otherwise fallback to validated_data for query string parameters for testing purposes # noqa: E501
    if hasattr(request, "validated_args"):
        query_string_parameters = request.validated_args
    else:
        query_string_parameters = validated_data
    return {
        "current_page": page,
        "results": browse_results,
        "date_validation_errors": date_validation_errors,
        "date_error_fields": date_error_fields,
        "transferring_bodies": transferring_bodies,
        "pagination": pagination,
        "filters": filters,
        "date_filters": date_filters,
        "sorting_orders": sorting_orders,
        "num_records_found": num_records_found,
        "query_string_parameters": query_string_parameters,
    }
