import uuid

from flask import current_app
from sqlalchemy import DATE, and_, desc, func

from app.main.db.models import Body, Consignment, File, FileMetadata, Series, db


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
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "date_last_modified",
                    func.cast(FileMetadata.Value, DATE),
                ),
                else_=None,
            )
        ).label("date_last_modified"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "end_date",
                    func.cast(FileMetadata.Value, DATE),
                ),
                else_=None,
            )
        ).label("end_date"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "closure_type",
                    FileMetadata.Value,
                ),
                else_=None,
            )
        ).label("closure_type"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "opening_date",
                    func.cast(FileMetadata.Value, DATE),
                ),
                else_=None,
            )
        ).label("opening_date"),
        # Add coalesced date column for sorting
        func.coalesce(
            func.max(
                db.case(
                    (
                        FileMetadata.PropertyName == "end_date",
                        func.cast(FileMetadata.Value, DATE),
                    ),
                    else_=None,
                )
            ),
            func.max(
                db.case(
                    (
                        FileMetadata.PropertyName == "date_last_modified",
                        func.cast(FileMetadata.Value, DATE),
                    ),
                    else_=None,
                )
            ),
        ).label("sort_date"),
    )

    query_filters = [
        File.ConsignmentId == consignment_id,
        func.lower(File.FileType) == "file",
    ]

    sub_query = (
        select.join(
            FileMetadata, File.FileId == FileMetadata.FileId, isouter=True
        )
        .join(File.consignment)
        .filter(*query_filters)
        .group_by(File.FileId)
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
            query = query.filter(
                func.lower(sub_query.c.closure_type) == record_status.lower()
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


def _build_base_query_filters(accessible_transferring_body_names, filters):
    query_filters = [func.lower(File.FileType) == "file"]
    if accessible_transferring_body_names is not None:
        query_filters.append(Body.Name.in_(accessible_transferring_body_names))

    if not filters:
        return query_filters

    if filters.get("transferring_body"):
        query_filters.append(
            func.lower(Body.Name).like(
                f"%{filters['transferring_body'].lower()}%"
            )
        )
    if filters.get("series"):
        query_filters.append(
            func.lower(Series.Name).like(f"%{filters['series'].lower()}%")
        )
    if filters.get("consignment_reference"):
        query_filters.append(
            func.lower(Consignment.ConsignmentReference).like(
                f"%{filters['consignment_reference'].lower()}%"
            )
        )

    record_status = (filters.get("record_status") or "").lower()
    if record_status and record_status != "all":
        closure_sub = db.session.query(FileMetadata.FileId).filter(
            FileMetadata.PropertyName == "closure_type",
            func.lower(FileMetadata.Value) == record_status,
        )
        query_filters.append(File.FileId.in_(closure_sub))

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
    prop_map = {
        "date_last_modified": "date_last_modified",
        "opening_date": "opening_date",
        "transferred": "end_date",
    }
    prop = prop_map.get((date_filter_field or "").lower())
    if prop:
        date_sub = db.session.query(FileMetadata.FileId).filter(
            FileMetadata.PropertyName == prop
        )
        if date_from:
            date_sub = date_sub.filter(
                func.to_char(func.cast(FileMetadata.Value, DATE), "YYYY-MM-DD")
                >= date_from
            )
        if date_to:
            date_sub = date_sub.filter(
                func.to_char(func.cast(FileMetadata.Value, DATE), "YYYY-MM-DD")
                <= date_to
            )
        return [File.FileId.in_(date_sub)]

    # sort_date = COALESCE(end_date, date_last_modified)
    sort_date_col = func.coalesce(
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "end_date",
                    func.cast(FileMetadata.Value, DATE),
                ),
                else_=None,
            )
        ),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "date_last_modified",
                    func.cast(FileMetadata.Value, DATE),
                ),
                else_=None,
            )
        ),
    )
    having_conds = []
    if date_from:
        having_conds.append(
            func.to_char(sort_date_col, "YYYY-MM-DD") >= date_from
        )
    if date_to:
        having_conds.append(
            func.to_char(sort_date_col, "YYYY-MM-DD") <= date_to
        )
    sort_date_ids = (
        db.session.query(FileMetadata.FileId)
        .group_by(FileMetadata.FileId)
        .having(and_(*having_conds))
    )
    return [File.FileId.in_(sort_date_ids)]


def _apply_base_query_sort(query, sorting_orders):
    if not sorting_orders:
        sorting_orders = {"date_of_record": "desc"}

    if "date_of_record" in sorting_orders:
        sort_sq = (
            db.session.query(
                FileMetadata.FileId.label("fid"),
                func.coalesce(
                    func.max(
                        db.case(
                            (
                                FileMetadata.PropertyName == "end_date",
                                func.cast(FileMetadata.Value, DATE),
                            ),
                            else_=None,
                        )
                    ),
                    func.max(
                        db.case(
                            (
                                FileMetadata.PropertyName
                                == "date_last_modified",
                                func.cast(FileMetadata.Value, DATE),
                            ),
                            else_=None,
                        )
                    ),
                ).label("sort_date"),
            ).group_by(FileMetadata.FileId)
        ).subquery()
        query = query.outerjoin(sort_sq, File.FileId == sort_sq.c.fid)
        if sorting_orders["date_of_record"] == "desc":
            return query.order_by(
                desc(sort_sq.c.sort_date), File.FileName, File.FileId
            )
        return query.order_by(sort_sq.c.sort_date, File.FileName, File.FileId)

    if "opening_date" in sorting_orders:
        opening_sq = (
            db.session.query(
                FileMetadata.FileId.label("fid"),
                func.max(
                    db.case(
                        (
                            FileMetadata.PropertyName == "opening_date",
                            func.cast(FileMetadata.Value, DATE),
                        ),
                        else_=None,
                    )
                ).label("opening_date"),
            ).group_by(FileMetadata.FileId)
        ).subquery()
        query = query.outerjoin(opening_sq, File.FileId == opening_sq.c.fid)
        if sorting_orders["opening_date"] == "desc":
            return query.order_by(
                desc(opening_sq.c.opening_date), File.FileName, File.FileId
            )
        return query.order_by(
            opening_sq.c.opening_date, File.FileName, File.FileId
        )

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
    accessible_transferring_body_names=None,
    filters=None,
    sorting_orders=None,
):
    """
    Stage-1 query: File/hierarchy only, no FileMetadata join in the main select.
    Pair with get_browse_records_metadata_for_files for the two-stage fetch.
    """
    query_filters = _build_base_query_filters(
        accessible_transferring_body_names, filters
    )

    query = (
        db.session.query(
            Body.BodyId.label("transferring_body_id"),
            Body.Name.label("transferring_body"),
            Series.SeriesId.label("series_id"),
            Series.Name.label("series"),
            Consignment.ConsignmentId.label("consignment_id"),
            Consignment.ConsignmentReference.label("consignment_reference"),
            File.FileId.label("file_id"),
            File.FileName.label("file_name"),
            File.FilePath.label("file_path"),
        )
        .join(File.consignment)
        .join(Consignment.series)
        .join(Series.body)
        .filter(*query_filters)
    )

    return _apply_base_query_sort(query, sorting_orders)


def get_browse_records_metadata_for_files(file_ids):
    """
    Stage-2 query: fetch and pivot the 4 browse metadata properties for a
    small set of file IDs. Reads only the rows needed for the current page.
    """
    if not file_ids:
        return {}

    properties = (
        "date_last_modified",
        "end_date",
        "closure_type",
        "opening_date",
    )
    date_properties = ("date_last_modified", "end_date", "opening_date")

    rows = (
        db.session.query(
            FileMetadata.FileId,
            FileMetadata.PropertyName,
            db.case(
                (
                    FileMetadata.PropertyName.in_(date_properties),
                    func.to_char(
                        func.cast(FileMetadata.Value, DATE),
                        current_app.config["DEFAULT_DATE_FORMAT"],
                    ),
                ),
                else_=FileMetadata.Value,
            ).label("value"),
        )
        .filter(
            FileMetadata.FileId.in_(file_ids),
            FileMetadata.PropertyName.in_(properties),
        )
        .all()
    )

    result = {}
    for file_id, prop, value in rows:
        if file_id not in result:
            result[file_id] = {}
        result[file_id][prop] = value

    return result


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
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "closure_type",
                    FileMetadata.Value,
                ),
                else_=None,
            )
        ).label("closure_type"),
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
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "opening_date",
                    func.cast(FileMetadata.Value, DATE),
                ),
                else_=None,
            ),
        ).label("opening_date"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "date_last_modified",
                    func.cast(FileMetadata.Value, DATE),
                ),
                else_=None,
            )
        ).label("date_last_modified"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "end_date",
                    func.cast(FileMetadata.Value, DATE),
                ),
                else_=None,
            )
        ).label("end_date"),
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


def _build_date_range_filter(date_field, date_from, date_to):
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
