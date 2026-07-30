from flask import abort
from sqlalchemy import func

from app.main.authorize.ayr_user import AYRUser
from app.main.db.models import Body, Consignment, File, Series, db


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
    if selected_transferring_body:
        return selected_transferring_body
    if accessible_body_names and len(accessible_body_names) == 1:
        return accessible_body_names[0]
    return selected_transferring_body


def get_options_rows(accessible_body_names):
    options_query = (
        db.session.query(
            Body.Name.label("transferring_body"),
            Series.Name.label("series"),
            Consignment.ConsignmentReference.label("consignment_reference"),
        )
        .join(Series, Series.BodyId == Body.BodyId)
        .join(Consignment, Consignment.SeriesId == Series.SeriesId)
        .join(File, File.ConsignmentId == Consignment.ConsignmentId)
        .filter(func.lower(File.FileType) == "file")
    )
    if accessible_body_names is not None:
        options_query = options_query.filter(
            Body.Name.in_(accessible_body_names)
        )
    return options_query.distinct().all()


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
                row.transferring_body
                for row in options_rows
                if row.transferring_body
                and (row.series or "").lower() == selected_series_lower
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
            if row.consignment_reference
            and selected_consignment_lower in row.consignment_reference.lower()
        ]

        if not selected_transferring_body:
            matching_transferring_bodies = sorted(
                {
                    row.transferring_body
                    for row in matching_rows
                    if row.transferring_body
                }
            )
            if len(matching_transferring_bodies) == 1:
                selected_transferring_body = matching_transferring_bodies[0]

        if not selected_series:
            matching_series = sorted(
                {row.series for row in matching_rows if row.series}
            )
            if len(matching_series) == 1:
                selected_series = matching_series[0]

    return selected_transferring_body, selected_series


def build_transferring_body_options(options_rows):
    return sorted(
        {row.transferring_body for row in options_rows if row.transferring_body}
    )


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


def build_browse_records_filter_data(
    validated_data,
    accessible_body_names,
    filters,
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

    options_rows = get_options_rows(accessible_body_names)

    selected_transferring_body, selected_series = autofill_selected_filters(
        selected_transferring_body,
        selected_series,
        selected_consignment,
        options_rows,
    )

    transferring_bodies = build_transferring_body_options(options_rows)

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
