import uuid

from flask import current_app
from sqlalchemy import DATE, and_, desc, func, or_

from app.main.db.models import Body, Consignment, File, FileMetadata, Series, db
from app.main.util.date_formatter import validate_date_range


def build_fuzzy_search_transferring_body_query(
    query_string: str, transferring_body_id, sorting_orders=None
):
    sub_query = (
        db.session.query(
            Body.BodyId.label("transferring_body_id"),
            Body.Name.label("transferring_body"),
            Body.Description.label("transferring_body_description"),
            Series.SeriesId.label("series_id"),
            Series.Name.label("series"),
            Series.Description.label("series_description"),
            Consignment.ConsignmentId.label("consignment_id"),
            Consignment.ConsignmentReference.label("consignment_reference"),
            File.FileId.label("file_id"),
            File.FileName.label("file_name"),
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
                ),
            ).label("opening_date"),
        )
        .join(Series, Series.BodyId == Body.BodyId)
        .join(
            Consignment,
            Consignment.SeriesId == Series.SeriesId,
        )
        .join(File, File.ConsignmentId == Consignment.ConsignmentId)
        .join(FileMetadata, File.FileId == FileMetadata.FileId, isouter=True)
        .where(func.lower(File.FileType) == "file")
        .group_by(
            File.FileId, Body.BodyId, Series.SeriesId, Consignment.ConsignmentId
        )
        .order_by(
            Body.Name,
            Series.Name,
            Consignment.ConsignmentReference,
            File.FileName,
        )
    ).subquery()

    query = db.session.query(
        sub_query.c.transferring_body_id,
        sub_query.c.transferring_body,
        sub_query.c.transferring_body_description,
        sub_query.c.series_id,
        sub_query.c.series,
        sub_query.c.series_description,
        sub_query.c.consignment_id,
        sub_query.c.consignment_reference,
        sub_query.c.file_id,
        sub_query.c.file_name,
        sub_query.c.closure_type,
        func.to_char(
            sub_query.c.opening_date,
            current_app.config["DEFAULT_DATE_FORMAT"],
        ).label("opening_date"),
    )

    query = query.filter(
        sub_query.c.transferring_body_id == transferring_body_id
    )

    for term in query_string.split(","):
        if len(term.strip()) > 0:
            filter_value = "%" + term.lower().strip() + "%"

            fuzzy_filters = or_(
                func.lower(sub_query.c.transferring_body).like(filter_value),
                func.lower(sub_query.c.transferring_body_description).like(
                    filter_value
                ),
                func.lower(sub_query.c.series).like(filter_value),
                func.lower(sub_query.c.series_description).like(filter_value),
                func.lower(sub_query.c.consignment_reference).like(
                    filter_value
                ),
                func.lower(sub_query.c.file_name).like(filter_value),
            )
            query = query.filter(fuzzy_filters)

    if sorting_orders:
        query = _build_sorting_orders(query, sub_query, sorting_orders)

    return query


def build_fuzzy_search_summary_query(query_string: str):
    sub_query = (
        db.session.query(
            Body.BodyId.label("transferring_body_id"),
            Body.Name.label("transferring_body"),
            Body.Description.label("transferring_body_description"),
            func.count(File.FileName.label("file_name")).label("records_held"),
        )
        .join(Series, Series.BodyId == Body.BodyId)
        .join(
            Consignment,
            Consignment.SeriesId == Series.SeriesId,
        )
        .join(File, File.ConsignmentId == Consignment.ConsignmentId)
        .group_by(Body.BodyId)
        .order_by(Body.Name)
    ).subquery()

    query = (
        db.session.query(
            sub_query.c.transferring_body_id,
            sub_query.c.transferring_body,
            func.count(sub_query.c.records_held).label("records_held"),
        )
        .join(Series, Series.BodyId == sub_query.c.transferring_body_id)
        .join(
            Consignment,
            Consignment.SeriesId == Series.SeriesId,
        )
        .join(File, File.ConsignmentId == Consignment.ConsignmentId)
        .where(func.lower(File.FileType) == "file")
        .group_by(
            sub_query.c.transferring_body_id, sub_query.c.transferring_body
        )
    )

    for term in query_string.split(","):
        if len(term.strip()) > 0:
            filter_value = "%" + term.lower().strip() + "%"
            fuzzy_filters = or_(
                func.lower(sub_query.c.transferring_body).like(filter_value),
                func.lower(sub_query.c.transferring_body_description).like(
                    filter_value
                ),
                func.lower(Series.Name).like(filter_value),
                func.lower(Series.Description).like(filter_value),
                func.lower(Consignment.ConsignmentReference).like(filter_value),
                func.lower(File.FileName).like(filter_value),
            )
            query = query.filter(fuzzy_filters)

    return query


def build_browse_all_query(filters=None, sorting_orders=None):
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
        .join(Consignment, Consignment.ConsignmentId == File.ConsignmentId)
        .join(Series, Series.SeriesId == Consignment.SeriesId)
        .join(Body, Body.BodyId == Series.BodyId)
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

    if filters:
        query = _build_browse_filters(query, sub_query, filters)

    if sorting_orders:
        query = _build_sorting_orders(query, sub_query, sorting_orders)
    else:
        query = query.order_by(
            sub_query.c.transferring_body, sub_query.c.series
        )

    return query


def build_browse_transferring_body_query(
    transferring_body_id, filters=None, sorting_orders=None
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
        .join(Consignment, Consignment.ConsignmentId == File.ConsignmentId)
        .join(Series, Series.SeriesId == Consignment.SeriesId)
        .join(Body, Body.BodyId == Series.BodyId)
        .where(
            (func.lower(File.FileType) == "file")
            & (Body.BodyId == transferring_body_id)
        )
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
            Body.BodyId.label("transferring_body_id"),
            Body.Name.label("transferring_body"),
            Series.SeriesId.label("series_id"),
            Series.Name.label("series"),
            func.max(Consignment.TransferCompleteDatetime).label(
                "last_record_transferred"
            ),
            func.count(func.distinct(File.FileId)).label("records_held"),
            Consignment.ConsignmentId.label("consignment_id"),
            Consignment.ConsignmentReference.label("consignment_reference"),
        )
        .join(Consignment, Consignment.ConsignmentId == File.ConsignmentId)
        .join(Series, Series.SeriesId == Consignment.SeriesId)
        .join(Body, Body.BodyId == Series.BodyId)
        .where(
            (func.lower(File.FileType) == "file")
            & (Series.SeriesId == series_id)
        )
        .group_by(Body.BodyId, Series.SeriesId, Consignment.ConsignmentId)
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
            ),
        ).label("opening_date"),
        Consignment.ConsignmentId.label("consignment_id"),
        Consignment.ConsignmentReference.label("consignment_reference"),
        Body.Name.label("transferring_body"),
        Body.BodyId.label("transferring_body_id"),
        Series.SeriesId.label("series_id"),
        Series.Name.label("series"),
    )

    query_filters = [
        File.ConsignmentId == consignment_id,
        func.lower(File.FileType) == "file",
    ]

    sub_query = (
        select.join(
            FileMetadata, File.FileId == FileMetadata.FileId, isouter=True
        )
        .join(Consignment, File.ConsignmentId == Consignment.ConsignmentId)
        .join(
            Series,
            Series.SeriesId == Consignment.SeriesId,
        )
        .join(
            Body,
            Body.BodyId == Series.BodyId,
        )
        .filter(*query_filters)
        .group_by(
            File.FileId, Body.BodyId, Series.SeriesId, Consignment.ConsignmentId
        )
        .order_by(File.FileName)
    ).subquery()

    query = db.session.query(
        sub_query.c.file_id,
        sub_query.c.file_name,
        func.to_char(
            sub_query.c.date_last_modified,
            current_app.config["DEFAULT_DATE_FORMAT"],
        ).label("date_last_modified"),
        sub_query.c.closure_type,
        func.to_char(
            sub_query.c.opening_date,
            current_app.config["DEFAULT_DATE_FORMAT"],
        ).label("opening_date"),
        sub_query.c.transferring_body_id,
        sub_query.c.transferring_body,
        sub_query.c.series_id,
        sub_query.c.series,
        sub_query.c.consignment_id,
        sub_query.c.consignment_reference,
    )

    if filters:
        record_status = filters.get("record_status")
        if record_status:
            if record_status and record_status.lower() != "all":
                query = query.filter(
                    func.lower(sub_query.c.closure_type)
                    == record_status.lower()
                )

        date_range = filters.get("date_range")
        if date_range:
            date_filter_field = filters.get("date_filter_field")
            if (
                date_filter_field
                and date_filter_field.lower() == "date_last_modified"
            ):
                dt_range = validate_date_range(date_range)
                date_filter = _build_date_range_filter(
                    sub_query.c.date_last_modified,
                    dt_range["date_from"],
                    dt_range["date_to"],
                )
                query = query.filter(date_filter)
            elif (
                date_filter_field
                and date_filter_field.lower() == "opening_date"
            ):
                dt_range = validate_date_range(date_range)
                date_filter = _build_date_range_filter(
                    sub_query.c.opening_date,
                    dt_range["date_from"],
                    dt_range["date_to"],
                )
                query = query.filter(date_filter)

    if sorting_orders:
        query = _build_sorting_orders(query, sub_query, sorting_orders)
    else:
        query = query.order_by(sub_query.c.file_name)
    return query


def _build_browse_filters(query, sub_query, filters):
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

    date_range = filters.get("date_range")
    if date_range:
        dt_range = validate_date_range(date_range)
        date_filter = _build_date_range_filter(
            sub_query.c.last_record_transferred,
            dt_range["date_from"],
            dt_range["date_to"],
        )
        query = query.filter(date_filter)

    return query


def _build_sorting_orders(query, sub_query, sorting_orders):
    for field, order in sorting_orders.items():
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
    query = db.session.query(
        File.FileId.label("file_id"),
        File.FileName.label("file_name"),
        File.FilePath.label("file_path"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "closure_type",
                    FileMetadata.Value,
                ),
                else_=None,
            )
        ).label("status"),
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
                    FileMetadata.PropertyName == "date_last_modified",
                    FileMetadata.Value,
                ),
                else_=None,
            )
        ).label("date_last_modified"),
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
        Consignment.ConsignmentId.label("consignment_id"),
        Consignment.ConsignmentReference.label("consignment"),
        Body.Name.label("transferring_body"),
        Body.BodyId.label("transferring_body_id"),
        Series.SeriesId.label("series_id"),
        Series.Name.label("series"),
    )

    filters = [
        File.FileId == file_id,
        func.lower(File.FileType) == "file",
    ]

    query = (
        query.join(
            FileMetadata, File.FileId == FileMetadata.FileId, isouter=True
        )
        .join(Consignment, File.ConsignmentId == Consignment.ConsignmentId)
        .join(
            Series,
            Series.SeriesId == Consignment.SeriesId,
        )
        .join(
            Body,
            Body.BodyId == Series.BodyId,
        )
        .filter(*filters)
        .group_by(
            File.FileId, Body.BodyId, Series.SeriesId, Consignment.ConsignmentId
        )
    )

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
