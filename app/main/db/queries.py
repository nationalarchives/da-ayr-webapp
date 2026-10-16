import uuid
from datetime import timedelta
from typing import Any, Callable, Optional

from flask import current_app
from sqlalchemy import DATE, and_, bindparam, desc, func, select, true
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Query
from sqlalchemy.sql.elements import ColumnElement

from app.main.db.models import Body, Consignment, File, FileMetadata, Series, db
from app.main.util.closure_status import closure_types_for_record_status


def build_browse_query(
    transferring_body_id=None, filters=None, sorting_orders=None
):
    sub_query = (
        db.session.query(
            Body.BodyId.label("transferring_body_id"),
            Body.Name.label("transferring_body"),
            Series.SeriesId.label("series_id"),
            Series.Name.label("series"),
            func.max(Consignment.TransferCompleteDatetime).label(
                "last_record_transferred"
            ),
            func.count(func.distinct(Consignment.ConsignmentReference)).label(
                "consignment_in_series"
            ),
            func.count(func.distinct(File.FileId)).label("records_held"),
        )
        .join(File.consignment)
        .join(Consignment.series)
        .join(Series.body)
        .where(func.lower(File.FileType) == "file")
        .group_by(Body.BodyId, Series.SeriesId)
    ).subquery()

    query = db.session.query(
        sub_query.c.transferring_body_id,
        sub_query.c.transferring_body,
        sub_query.c.series_id,
        sub_query.c.series,
        func.to_char(
            sub_query.c.last_record_transferred,
            current_app.config["DEFAULT_DATE_FORMAT"],
        ).label("last_record_transferred"),
        sub_query.c.consignment_in_series,
        sub_query.c.records_held,
    )

    if transferring_body_id:
        query = query.filter(
            sub_query.c.transferring_body_id == transferring_body_id
        )

    if filters:
        query = _build_browse_filters(query, sub_query, filters)

    if sorting_orders:
        query = _build_sorting_orders(query, sub_query, sorting_orders)
    else:
        query = query.order_by(
            sub_query.c.transferring_body, sub_query.c.series
        )

    return query


def build_browse_series_query(series_id, filters=None, sorting_orders=None):
    sub_query = (
        db.session.query(
            Body.Name.label("transferring_body"),
            Series.Name.label("series"),
            func.max(Consignment.TransferCompleteDatetime).label(
                "last_record_transferred"
            ),
            func.count(func.distinct(File.FileId)).label("records_held"),
            Consignment.ConsignmentId.label("consignment_id"),
            Consignment.ConsignmentReference.label("consignment_reference"),
        )
        .join(File.consignment)
        .join(Consignment.series)
        .join(Series.body)
        .where(
            (func.lower(File.FileType) == "file")
            & (Series.SeriesId == series_id)
        )
        .group_by(Body.BodyId, Series.SeriesId, Consignment.ConsignmentId)
    ).subquery()

    query = db.session.query(
        sub_query.c.transferring_body,
        sub_query.c.series,
        func.to_char(
            sub_query.c.last_record_transferred,
            current_app.config["DEFAULT_DATE_FORMAT"],
        ).label("last_record_transferred"),
        sub_query.c.records_held,
        sub_query.c.consignment_id,
        sub_query.c.consignment_reference,
    )

    if filters:
        query = _build_browse_filters(query, sub_query, filters)

    if sorting_orders:
        query = _build_sorting_orders(query, sub_query, sorting_orders)
    else:
        query = query.order_by(
            sub_query.c.transferring_body,
            sub_query.c.series,
            desc(sub_query.c.last_record_transferred),
        )

    return query


def build_browse_consignment_query(
    consignment_id: uuid.UUID, filters=None, sorting_orders=None
):
    select = db.session.query(
        File.FileId.label("file_id"),
        File.FileName.label("file_name"),
        File.DateLastModified.label("date_last_modified"),
        File.EndDate.label("end_date"),
        File.ClosureType.label("closure_type"),
        File.OpeningDate.label("opening_date"),
        # Add coalesced date column for sorting
        func.coalesce(File.EndDate, File.DateLastModified).label("sort_date"),
    )

    query_filters = [
        File.ConsignmentId == consignment_id,
        func.lower(File.FileType) == "file",
    ]

    sub_query = (
        select.join(File.consignment)
        .filter(*query_filters)
        .order_by(File.FileName)
    ).subquery()

    query = db.session.query(
        sub_query.c.file_id,
        sub_query.c.file_name,
        func.to_char(
            sub_query.c.date_last_modified,
            current_app.config["DEFAULT_DATE_FORMAT"],
        ).label("date_last_modified"),
        func.to_char(
            sub_query.c.end_date,
            current_app.config["DEFAULT_DATE_FORMAT"],
        ).label("end_date"),
        sub_query.c.closure_type,
        func.to_char(
            sub_query.c.opening_date,
            current_app.config["DEFAULT_DATE_FORMAT"],
        ).label("opening_date"),
        func.to_char(
            func.coalesce(sub_query.c.end_date, sub_query.c.date_last_modified),
            current_app.config["DEFAULT_DATE_FORMAT"],
        ).label("date_of_record"),
    )

    if filters:
        record_status = filters.get("record_status")
        if record_status and record_status.lower() != "all":
            closure_values = [
                value.lower()
                for value in closure_types_for_record_status(record_status)
            ]
            query = query.filter(
                func.lower(sub_query.c.closure_type).in_(closure_values)
            )

        date_filter = None
        date_filter_field = filters.get("date_filter_field")
        if (
            date_filter_field
            and date_filter_field.lower() == "date_last_modified"
        ):
            date_filter = _build_date_range_filter(
                sub_query.c.sort_date,
                filters.get("date_from"),
                filters.get("date_to"),
            )
        elif date_filter_field and date_filter_field.lower() == "opening_date":
            date_filter = _build_date_range_filter(
                sub_query.c.opening_date,
                filters.get("date_from"),
                filters.get("date_to"),
            )

        if date_filter is not None:
            query = query.filter(date_filter)

    if sorting_orders:
        if "date_of_record" in sorting_orders:
            sort_field = sub_query.c.sort_date
            if sorting_orders["date_of_record"] == "desc":
                query = query.order_by(desc(sort_field))
            else:
                query = query.order_by(sort_field)
        else:
            query = _build_sorting_orders(query, sub_query, sorting_orders)
    else:
        query = query.order_by(sub_query.c.file_name)

    return query


def _build_records_hierarchy_filters(
    accessible_transferring_body_names, filters
):
    query_filters = []
    if accessible_transferring_body_names is not None:
        query_filters.append(Body.Name.in_(accessible_transferring_body_names))

    if not filters:
        return query_filters

    transferring_body = (filters.get("transferring_body") or "").strip()
    if transferring_body:
        query_filters.append(func.lower(Body.Name) == transferring_body.lower())
    series = (filters.get("series") or "").strip()
    if series:
        query_filters.append(func.lower(Series.Name) == series.lower())
    consignment_reference = (filters.get("consignment_reference") or "").strip()
    if consignment_reference:
        query_filters.append(
            func.lower(Consignment.ConsignmentReference)
            == consignment_reference.lower()
        )

    return query_filters


def _resolve_records_consignment_ids(
    accessible_transferring_body_names, filters
):
    hierarchy_filters = _build_records_hierarchy_filters(
        accessible_transferring_body_names, filters
    )
    if not hierarchy_filters:
        return None

    return [
        row.ConsignmentId
        for row in (
            db.session.query(Consignment.ConsignmentId)
            .join(Consignment.series)
            .join(Series.body)
            .filter(*hierarchy_filters)
            .all()
        )
    ]


def _build_records_file_filters(filters):
    query_filters = [func.lower(File.FileType) == "file"]
    if not filters:
        return query_filters

    record_status = (filters.get("record_status") or "").lower()
    if record_status and record_status != "all":
        closure_values = [
            value.lower()
            for value in closure_types_for_record_status(record_status)
        ]
        query_filters.append(func.lower(File.ClosureType).in_(closure_values))

    date_from = filters.get("date_from")
    date_to = filters.get("date_to")
    if date_from or date_to:
        query_filters.extend(
            _build_date_file_id_filters(
                filters.get("date_filter_field"), date_from, date_to
            )
        )

    return query_filters


def _build_date_file_id_filters(date_filter_field, date_from, date_to):
    col_map = {
        "date_last_modified": File.DateLastModified,
        "opening_date": File.OpeningDate,
        "transferred": File.EndDate,
    }
    date_col = col_map.get((date_filter_field or "").lower())
    if date_col is None:
        # sort_date = COALESCE(end_date, date_last_modified)
        date_col = func.coalesce(File.EndDate, File.DateLastModified)

    query_filters = []
    if date_from:
        query_filters.append(date_col >= func.cast(date_from, DATE))
    if date_to:
        # Compute the next midnight in PostgreSQL, including 9999-12-31.
        query_filters.append(
            date_col < func.cast(date_to, DATE) + timedelta(days=1)
        )
    return query_filters


def _apply_base_query_sort(
    query: Query, sorting_orders: Optional[dict[str, str]]
) -> Query:
    if not sorting_orders:
        return query

    if "date_of_record" in sorting_orders:
        sort_date_col = func.coalesce(File.EndDate, File.DateLastModified)
        if sorting_orders["date_of_record"] == "desc":
            return query.order_by(desc(sort_date_col))
        return query.order_by(sort_date_col)

    if "opening_date" in sorting_orders:
        if sorting_orders["opening_date"] == "desc":
            return query.order_by(desc(File.OpeningDate))
        return query.order_by(File.OpeningDate)

    col_map = {
        "file_name": File.FileName,
        "series": Series.Name,
    }
    for field, order in sorting_orders.items():
        col = col_map.get(field)
        if col is not None:
            query = query.order_by(desc(col) if order == "desc" else col)
    return query


def build_browse_records_base_query(
    accessible_transferring_body_names: Optional[list[str]] = None,
    filters: Optional[dict[str, Any]] = None,
    sorting_orders: Optional[dict[str, str]] = None,
):
    """
    File/hierarchy plus the browse metadata fields, all read directly off
    File/Consignment columns - no FileMetadata join.
    """
    consignment_ids = _resolve_records_consignment_ids(
        accessible_transferring_body_names, filters
    )
    query_filters = _build_records_file_filters(filters)
    if consignment_ids is not None:
        query_filters.append(File.ConsignmentId.in_(consignment_ids))

    query = _build_records_metadata_query().filter(*query_filters)
    return _apply_base_query_sort(query, sorting_orders)


def _build_records_metadata_query():
    return (
        db.session.query(
            Body.BodyId.label("transferring_body_id"),
            Body.Name.label("transferring_body"),
            Series.SeriesId.label("series_id"),
            Series.Name.label("series"),
            Consignment.ConsignmentId.label("consignment_id"),
            Consignment.ConsignmentReference.label("consignment_reference"),
            func.to_char(
                Consignment.TransferCompleteDatetime,
                current_app.config["DEFAULT_DATE_FORMAT"],
            ).label("consignment_transfer_complete_date"),
            File.FileId.label("file_id"),
            File.FileName.label("file_name"),
            File.FilePath.label("file_path"),
            File.ClosureType.label("closure_type"),
            func.to_char(
                File.OpeningDate,
                current_app.config["DEFAULT_DATE_FORMAT"],
            ).label("opening_date"),
            func.to_char(
                func.coalesce(File.EndDate, File.DateLastModified),
                current_app.config["DEFAULT_DATE_FORMAT"],
            ).label("date_of_record"),
        )
        .join(File.consignment)
        .join(Consignment.series)
        .join(Series.body)
    )


def _build_scoped_records_candidates(
    consignment_ids, file_filters, sort_column, descending, candidate_limit
):
    permitted = select(
        func.unnest(
            bindparam(
                "consignment_ids",
                value=consignment_ids,
                type_=ARRAY(UUID(as_uuid=True)),
            )
        ).label("consignment_id")
    ).subquery("permitted_consignments")
    candidate = (
        select(
            File.FileId.label("file_id"),
            sort_column.label("sort_value"),
        )
        .where(
            File.ConsignmentId == permitted.c.consignment_id,
            *file_filters,
        )
        .order_by(desc(sort_column) if descending else sort_column)
        .limit(candidate_limit)
        .correlate(permitted)
        .lateral("candidate")
    )
    return select(candidate.c.file_id, candidate.c.sort_value).select_from(
        permitted.join(candidate, true())
    )


def _build_series_records_candidates(
    consignment_ids, file_filters, candidate_limit
):
    series_query = select(Series.SeriesId, Series.Name).join(Series.body)
    if consignment_ids is not None:
        series_query = series_query.where(
            Series.SeriesId.in_(
                select(Consignment.SeriesId).where(
                    Consignment.ConsignmentId.in_(consignment_ids)
                )
            )
        )
        file_filters = [
            *file_filters,
            File.ConsignmentId.in_(consignment_ids),
        ]
    eligible_series = series_query.subquery("eligible_series")
    # All files within a series tie: bound each group's contribution without
    # sorting its files. The global sort also handles duplicate series names.
    candidate = (
        select(File.FileId.label("file_id"))
        .join(File.consignment)
        .where(
            Consignment.SeriesId == eligible_series.c.SeriesId,
            *file_filters,
        )
        .limit(candidate_limit)
        .correlate(eligible_series)
        .lateral("candidate")
    )
    return select(
        candidate.c.file_id, eligible_series.c.Name.label("sort_value")
    ).select_from(eligible_series.join(candidate, true()))


def build_browse_records_queries(
    accessible_transferring_body_names: Optional[list[str]] = None,
    filters: Optional[dict[str, Any]] = None,
    sorting_orders: Optional[dict[str, str]] = None,
    offset: int = 0,
    limit: int = 5,
) -> tuple[Query, Query]:
    count_query, build_page_query = build_browse_records_query_factory(
        accessible_transferring_body_names,
        filters,
        sorting_orders,
    )
    page_query, _ = build_page_query(offset, limit, None)
    return count_query, page_query


def build_browse_records_query_factory(
    accessible_transferring_body_names: Optional[list[str]] = None,
    filters: Optional[dict[str, Any]] = None,
    sorting_orders: Optional[dict[str, str]] = None,
) -> tuple[Query, Callable[[int, int, Optional[int]], tuple[Query, bool]]]:
    """Build the exact count and a page query deferred until count is known."""
    consignment_ids = _resolve_records_consignment_ids(
        accessible_transferring_body_names, filters
    )
    file_filters = _build_records_file_filters(filters)
    count_query = db.session.query(func.count()).select_from(File)
    if consignment_ids is None:
        count_query = (
            count_query.join(File.consignment)
            .join(Consignment.series)
            .join(Series.body)
        )
    else:
        count_query = count_query.filter(
            File.ConsignmentId.in_(consignment_ids)
        )
    count_query = count_query.filter(*file_filters)

    sort_field, _ = next(
        iter((sorting_orders or {"date_of_record": "desc"}).items())
    )
    reverse_supported = sort_field in {
        "date_of_record",
        "opening_date",
        "file_name",
        "series",
    }

    def build_page_query(
        offset: int, limit: int, total_records: Optional[int]
    ) -> tuple[Query, bool]:
        page_offset = offset
        page_limit = limit
        reverse = False
        if total_records is not None:
            page_limit = min(limit, max(0, total_records - offset))
            reverse_offset = max(0, total_records - offset - page_limit)
            if reverse_supported and page_limit and reverse_offset < offset:
                page_offset = reverse_offset
                reverse = True

        return (
            _build_browse_records_page_query(
                consignment_ids,
                file_filters,
                sorting_orders,
                page_offset,
                page_limit,
                reverse,
            ),
            reverse,
        )

    return count_query, build_page_query


def _build_browse_records_page_query(
    consignment_ids,
    file_filters,
    sorting_orders,
    offset,
    limit,
    reverse,
):
    sort_field, direction = next(
        iter((sorting_orders or {"date_of_record": "desc"}).items())
    )
    if sort_field not in {
        "date_of_record",
        "opening_date",
        "file_name",
        "series",
    }:
        # The shared browse schema also accepts other pages' sort options.
        # Preserve their existing unsorted behavior on browse records.
        page_query = _build_records_metadata_query().filter(*file_filters)
        if consignment_ids is not None:
            page_query = page_query.filter(
                File.ConsignmentId.in_(consignment_ids)
            )
        return page_query.offset(offset).limit(limit)
    descending = (direction == "desc") != reverse
    if sort_field == "series":
        candidates = _build_series_records_candidates(
            consignment_ids, file_filters, offset + limit
        )
    else:
        sort_column = {
            "date_of_record": func.coalesce(
                File.EndDate, File.DateLastModified
            ),
            "opening_date": File.OpeningDate,
            "file_name": File.FileName,
        }[sort_field]
        if consignment_ids is not None:
            candidates = _build_scoped_records_candidates(
                consignment_ids,
                file_filters,
                sort_column,
                descending,
                offset + limit,
            )
        else:
            candidates = (
                select(
                    File.FileId.label("file_id"),
                    sort_column.label("sort_value"),
                )
                .join(File.consignment)
                .join(Consignment.series)
                .join(Series.body)
                .where(*file_filters)
            )

    candidates = candidates.subquery("candidates")
    sort_value = candidates.c.sort_value
    page_keys = (
        select(candidates.c.file_id, sort_value)
        .order_by(desc(sort_value) if descending else sort_value)
        .offset(offset)
        .limit(limit)
        .cte("page_keys")
        .prefix_with("MATERIALIZED")
    )
    page_query = (
        _build_records_metadata_query()
        .join(page_keys, File.FileId == page_keys.c.file_id)
        .order_by(
            desc(page_keys.c.sort_value)
            if descending
            else page_keys.c.sort_value
        )
    )
    return page_query


def _build_browse_filters(query, sub_query, filters):
    transferring_body = filters.get("transferring_body")
    if transferring_body:
        filter_value = f"%{transferring_body}%".lower()
        query = query.filter(
            func.lower(sub_query.c.transferring_body).like(filter_value)
        )

    series = filters.get("series")
    if series:
        filter_value = f"%{series}%".lower()
        query = query.filter(func.lower(sub_query.c.series).like(filter_value))

    date_filter = _build_date_range_filter(
        sub_query.c.last_record_transferred,
        filters.get("date_from"),
        filters.get("date_to"),
    )
    if date_filter is not None:
        query = query.filter(date_filter)

    return query


def _build_sorting_orders(query, sub_query, sorting_orders):
    for field, order in sorting_orders.items():
        if field == "date_of_record":
            # Use end_date if available, otherwise
            # fall back to date_last_modified.
            column = func.coalesce(
                sub_query.c.end_date, sub_query.c.date_last_modified
            )
        else:
            column = getattr(sub_query.c, field, None)

        if column is not None:
            query = (
                query.order_by(desc(column))
                if order == "desc"
                else query.order_by(column)
            )
    return query


def get_file_metadata(file_id: uuid.UUID):
    query = _get_file_metadata_query(file_id)
    row = query.first_or_404()
    return dict(row._mapping)


def _get_file_metadata_query(file_id: uuid.UUID):
    select = db.session.query(
        File.FileId.label("file_id"),
        File.FileName.label("file_name"),
        File.FilePath.label("file_path"),
        File.FileReference.label("file_reference"),
        File.CiteableReference.label("citeable_reference"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "former_reference_department",
                    FileMetadata.Value,
                ),
                else_=None,
            ),
        ).label("former_reference"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "title_alternate",
                    FileMetadata.Value,
                ),
                else_=None,
            )
        ).label("alternative_title"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "description",
                    FileMetadata.Value,
                ),
                else_=None,
            ),
        ).label("description"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "description_alternate",
                    FileMetadata.Value,
                ),
                else_=None,
            )
        ).label("alternative_description"),
        File.ClosureType.label("closure_type"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "closure_start_date",
                    func.cast(FileMetadata.Value, DATE),
                ),
                else_=None,
            )
        ).label("closure_start_date"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "closure_period",
                    FileMetadata.Value,
                ),
                else_=None,
            )
        ).label("closure_period"),
        File.OpeningDate.label("opening_date"),
        File.DateLastModified.label("date_last_modified"),
        File.EndDate.label("end_date"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "foi_exemption_code",
                    FileMetadata.Value,
                ),
                else_=None,
            )
        ).label("foi_exemption_code"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "file_name_translation",
                    FileMetadata.Value,
                ),
                else_=None,
            )
        ).label("translated_title"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "related_material",
                    FileMetadata.Value,
                ),
                else_=None,
            ),
        ).label("related_material"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "restrictions_on_use",
                    FileMetadata.Value,
                ),
                else_=None,
            ),
        ).label("restrictions_on_use"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "note",
                    FileMetadata.Value,
                ),
                else_=None,
            ),
        ).label("note"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "held_by",
                    FileMetadata.Value,
                ),
                else_=None,
            ),
        ).label("held_by"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "legal_status",
                    FileMetadata.Value,
                ),
                else_=None,
            ),
        ).label("legal_status"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "rights_copyright",
                    FileMetadata.Value,
                ),
                else_=None,
            ),
        ).label("rights_copyright"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "language",
                    FileMetadata.Value,
                ),
                else_=None,
            ),
        ).label("language"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "evidence_provided_by",
                    FileMetadata.Value,
                ),
                else_=None,
            ),
        ).label("evidence_provided_by"),
    )

    filters = [
        File.FileId == file_id,
        func.lower(File.FileType) == "file",
    ]

    sub_query = (
        select.join(
            FileMetadata, File.FileId == FileMetadata.FileId, isouter=True
        )
        .filter(*filters)
        .group_by(File.FileId)
    ).subquery()

    query = (
        db.session.query(
            sub_query.c.file_id,
            sub_query.c.file_name,
            sub_query.c.file_path,
            sub_query.c.citeable_reference,
            sub_query.c.alternative_title,
            sub_query.c.description,
            sub_query.c.alternative_description,
            sub_query.c.closure_type,
            func.to_char(
                sub_query.c.closure_start_date,
                current_app.config["DEFAULT_DATE_FORMAT"],
            ).label("closure_start_date"),
            sub_query.c.closure_period,
            func.to_char(
                sub_query.c.opening_date,
                current_app.config["DEFAULT_DATE_FORMAT"],
            ).label("opening_date"),
            func.to_char(
                func.coalesce(
                    sub_query.c.end_date, sub_query.c.date_last_modified
                ),
                current_app.config["DEFAULT_DATE_FORMAT"],
            ).label("date_of_record"),
            func.to_char(
                sub_query.c.end_date,
                current_app.config["DEFAULT_DATE_FORMAT"],
            ).label("end_date"),
            sub_query.c.foi_exemption_code,
            sub_query.c.file_reference,
            sub_query.c.former_reference,
            sub_query.c.translated_title,
            sub_query.c.related_material,
            sub_query.c.restrictions_on_use,
            sub_query.c.note,
            sub_query.c.held_by,
            sub_query.c.legal_status,
            sub_query.c.rights_copyright,
            sub_query.c.language,
            sub_query.c.evidence_provided_by,
            Body.Name.label("transferring_body"),
            Series.Name.label("series"),
            Consignment.ConsignmentReference.label("consignment_reference"),
        )
        .join(File.consignment)
        .join(Consignment.series)
        .join(Series.body)
    ).where(sub_query.c.file_id == File.FileId)

    return query


def _build_date_range_filter(
    date_field: ColumnElement, date_from: Optional[str], date_to: Optional[str]
) -> Optional[ColumnElement]:
    date_filter = None
    if date_from and date_to:
        date_filter = and_(
            func.to_char(date_field, "YYYY-MM-DD") >= date_from,
            func.to_char(date_field, "YYYY-MM-DD") <= date_to,
        )
    elif date_from:
        date_filter = func.to_char(date_field, "YYYY-MM-DD") >= date_from
    elif date_to:
        date_filter = func.to_char(date_field, "YYYY-MM-DD") <= date_to

    return date_filter
