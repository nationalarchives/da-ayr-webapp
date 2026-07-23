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


def build_browse_records_filter_data(
    validated_data,
    accessible_body_names,
    filters,
):
    selected_transferring_body = (
        validated_data.get("transferring_body_filter") or ""
    ).strip()
    selected_series = (validated_data.get("series_filter") or "").strip()
    selected_consignment = (
        validated_data.get("consignment_reference") or ""
    ).strip()

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
    options_rows = options_query.distinct().all()

    if selected_consignment and (
        not selected_transferring_body or not selected_series
    ):
        matching_rows = [
            row
            for row in options_rows
            if row.consignment_reference
            and row.consignment_reference.lower()
            == selected_consignment.lower()
        ]
        matching_transferring_bodies = sorted(
            {
                row.transferring_body
                for row in matching_rows
                if row.transferring_body
            }
        )
        matching_series = sorted(
            {row.series for row in matching_rows if row.series}
        )

        if (
            len(matching_transferring_bodies) == 1
            and not selected_transferring_body
        ):
            selected_transferring_body = matching_transferring_bodies[0]
        if len(matching_series) == 1 and not selected_series:
            selected_series = matching_series[0]

    def matches_selection(candidate: str | None, selected_value: str) -> bool:
        if not selected_value:
            return True
        return (candidate or "").lower() == selected_value.lower()

    transferring_bodies = sorted(
        {row.transferring_body for row in options_rows if row.transferring_body}
    )
    series_options = sorted(
        {
            row.series
            for row in options_rows
            if row.series
            and matches_selection(
                row.transferring_body, selected_transferring_body
            )
        }
    )
    consignment_options = sorted(
        {
            row.consignment_reference
            for row in options_rows
            if row.consignment_reference
            and matches_selection(
                row.transferring_body, selected_transferring_body
            )
            and matches_selection(row.series, selected_series)
        }
    )

    if selected_transferring_body:
        filters["transferring_body"] = selected_transferring_body
    if selected_series:
        filters["series"] = selected_series
    if selected_consignment:
        filters["consignment_reference"] = selected_consignment

    return transferring_bodies, series_options, consignment_options
