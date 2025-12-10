import uuid

from flask import current_app
from sqlalchemy import DATE, and_, desc, func

from app.main.db.models import Body, Consignment, File, FileMetadata, Series, db


def build_browse_query(
    transferring_body_id=None, filters=None, sorting_orders=None
):
    db.engine.dispose()
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
    db.engine.dispose()
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
    db.engine.dispose()
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


def _build_browse_filters(query, sub_query, filters):
    db.engine.dispose()
    transferring_body = filters.get("transferring_body")
    if transferring_body:
        filter_value = str(f"%{transferring_body}%").lower()
        query = query.filter(
            func.lower(sub_query.c.transferring_body).like(filter_value)
        )

    series = filters.get("series")
    if series:
        filter_value = str(f"%{series}%").lower()
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
            # Use end_date if available, otherwise fall back to date_last_modified
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
    db.engine.dispose()
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
