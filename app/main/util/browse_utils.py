from flask import abort

from app.main.authorize.ayr_user import AYRUser
from app.main.util.search_utils import BROWSE_INDEX, execute_search_query


def get_accessible_body_names(ayr_user: AYRUser):
    if ayr_user.is_standard_user:
        body = ayr_user.transferring_body
        return [body.Name] if body else []
    if ayr_user.is_all_access_user:
        return None
    abort(403)


def get_selected_filters(validated_data):
    selected_transferring_body = (
        validated_data.get("transferring_body_filter") or ""
    ).strip()
    selected_series = (validated_data.get("series_filter") or "").strip()
    selected_consignment = (
        validated_data.get("consignment_reference") or ""
    ).strip()
    selected_record_status = (validated_data.get("record_status") or "").strip()
    selected_date_filter_field = (
        validated_data.get("date_filter_field") or ""
    ).strip()
    return (
        selected_transferring_body,
        selected_series,
        selected_consignment,
        selected_record_status,
        selected_date_filter_field,
    )


def prefill_transferring_body_for_single_scope(
    selected_transferring_body,
    accessible_body_names,
):
    if accessible_body_names and len(accessible_body_names) == 1:
        return accessible_body_names[0]
    return selected_transferring_body


def _get_browse_composite_buckets(
    open_search,
    aggregation_name,
    sources,
    query=None,
    index=BROWSE_INDEX,
):
    buckets = []
    after_key = None

    while True:
        composite = {"size": 1000, "sources": sources}
        if after_key:
            composite["after"] = after_key

        response = execute_search_query(
            open_search,
            {
                "size": 0,
                "track_total_hits": False,
                "query": query or {"match_all": {}},
                "aggs": {
                    aggregation_name: {
                        "composite": composite,
                    }
                },
            },
            index=index,
        )
        aggregation = response["aggregations"][aggregation_name]
        buckets.extend(aggregation["buckets"])

        next_after_key = aggregation.get("after_key")
        if not next_after_key or next_after_key == after_key:
            break
        after_key = next_after_key

    return buckets


def get_transferring_body_options_from_opensearch(
    open_search,
    index=BROWSE_INDEX,
):
    buckets = _get_browse_composite_buckets(
        open_search,
        "browse_transferring_bodies",
        [
            {
                "transferring_body": {
                    "terms": {"field": "transferring_body.keyword"}
                }
            }
        ],
        index=index,
    )
    return sorted(
        {
            bucket["key"].get("transferring_body")
            for bucket in buckets
            if bucket["key"].get("transferring_body")
        }
    )


def get_autofill_options_rows_from_opensearch(
    open_search,
    accessible_body_names,
    selected_series,
    selected_consignment,
    index=BROWSE_INDEX,
):
    if accessible_body_names == []:
        return []

    filter_clauses = []
    if accessible_body_names is not None:
        filter_clauses.append(
            {"terms": {"transferring_body.keyword": accessible_body_names}}
        )

    for value, field in (
        (selected_series, "series_name"),
        (selected_consignment, "consignment_reference"),
    ):
        if value:
            filter_clauses.append(
                {
                    "term": {
                        f"{field}.keyword": {
                            "value": value,
                            "case_insensitive": True,
                        }
                    }
                }
            )

    query = (
        {"bool": {"filter": filter_clauses}}
        if filter_clauses
        else {"match_all": {}}
    )
    buckets = _get_browse_composite_buckets(
        open_search,
        "browse_autofill_options",
        [
            {
                "transferring_body": {
                    "terms": {"field": "transferring_body.keyword"}
                }
            },
            {"series": {"terms": {"field": "series_name.keyword"}}},
        ],
        query=query,
        index=index,
    )

    return [
        {
            "transferring_body": bucket["key"].get("transferring_body"),
            "series": bucket["key"].get("series"),
            "consignment_reference": selected_consignment,
        }
        for bucket in buckets
    ]


def autofill_selected_filters(
    selected_transferring_body,
    selected_series,
    selected_consignment,
    options_rows,
):
    if selected_series and not selected_transferring_body:
        selected_series_lower = selected_series.lower()
        matching_transferring_bodies = sorted(
            {
                row["transferring_body"]
                for row in options_rows
                if row["transferring_body"]
                and selected_series_lower == (row["series"] or "").lower()
            }
        )
        if len(matching_transferring_bodies) == 1:
            selected_transferring_body = matching_transferring_bodies[0]

    if selected_consignment and (
        not selected_transferring_body or not selected_series
    ):
        selected_consignment_lower = selected_consignment.lower()
        matching_rows = [
            row
            for row in options_rows
            if row["consignment_reference"]
            and selected_consignment_lower
            == row["consignment_reference"].lower()
        ]

        if not selected_transferring_body:
            matching_transferring_bodies = sorted(
                {
                    row["transferring_body"]
                    for row in matching_rows
                    if row["transferring_body"]
                }
            )
            if len(matching_transferring_bodies) == 1:
                selected_transferring_body = matching_transferring_bodies[0]

        if not selected_series:
            matching_series = sorted(
                {row["series"] for row in matching_rows if row["series"]}
            )
            if len(matching_series) == 1:
                selected_series = matching_series[0]

    return selected_transferring_body, selected_series


def apply_selected_filters(
    filters,
    selected_transferring_body,
    selected_series,
    selected_consignment,
    selected_record_status,
    selected_date_filter_field,
):
    if selected_transferring_body:
        filters["transferring_body"] = selected_transferring_body
    if selected_series:
        filters["series"] = selected_series
    if selected_consignment:
        filters["consignment_reference"] = selected_consignment
    if selected_record_status:
        filters["record_status"] = selected_record_status
    if selected_date_filter_field:
        filters["date_filter_field"] = selected_date_filter_field


def build_browse_filter_data(
    validated_data,
    accessible_body_names,
    filters,
    open_search,
):
    (
        selected_transferring_body,
        selected_series,
        selected_consignment,
        selected_record_status,
        selected_date_filter_field,
    ) = get_selected_filters(validated_data)

    selected_transferring_body = prefill_transferring_body_for_single_scope(
        selected_transferring_body,
        accessible_body_names,
    )

    if accessible_body_names == []:
        transferring_bodies = []
    elif accessible_body_names and len(accessible_body_names) == 1:
        transferring_bodies = accessible_body_names
    else:
        transferring_bodies = get_transferring_body_options_from_opensearch(
            open_search
        )

    should_autofill_from_series = (
        selected_series and not selected_transferring_body
    )
    should_autofill_from_consignment = (
        selected_consignment and not selected_series
    )

    if should_autofill_from_series or should_autofill_from_consignment:
        options_rows = get_autofill_options_rows_from_opensearch(
            open_search,
            accessible_body_names,
            selected_series,
            selected_consignment,
        )

        selected_transferring_body, selected_series = autofill_selected_filters(
            selected_transferring_body,
            selected_series,
            selected_consignment,
            options_rows,
        )

    apply_selected_filters(
        filters,
        selected_transferring_body,
        selected_series,
        selected_consignment,
        selected_record_status,
        selected_date_filter_field,
    )

    return transferring_bodies


def count_selected_filters(
    filters,
    from_date,
    to_date,
    is_standard_user,
):
    filter_count = 0

    selected_transferring_body = (
        filters.get("transferring_body") or ""
    ).strip()
    if selected_transferring_body and not is_standard_user:
        filter_count += 1
    if (filters.get("series") or "").strip():
        filter_count += 1
    if (filters.get("consignment_reference") or "").strip():
        filter_count += 1

    selected_record_status = (filters.get("record_status") or "").strip()
    if selected_record_status and selected_record_status.lower() != "all":
        filter_count += 1

    selected_date_filter_field = (
        filters.get("date_filter_field") or ""
    ).strip()
    if (
        selected_date_filter_field
        and selected_date_filter_field.lower() != "date_last_modified"
    ):
        filter_count += 1

    if from_date:
        filter_count += 1
    if to_date:
        filter_count += 1

    return filter_count
