import uuid

from flask import current_app
from sqlalchemy import DATE, Text, and_, func, or_

from app.main.authorize.permissions_helpers import (
    validate_body_user_groups_or_404,
)
from app.main.db.models import Body, Consignment, File, FileMetadata, Series, db
from app.main.util.date_formatter import validate_date_range


def fuzzy_search(query: str, page: int, per_page: int):
    if len(query) > 0:
        fuzzy_search_query = _build_fuzzy_search_query(query)
        return fuzzy_search_query.paginate(page=page, per_page=per_page)


def browse_data(
    page,
    per_page,
    transferring_body_id=None,
    series_id=None,
    consignment_id=None,
    date_range=None,
    date_filter_field=None,
):
    if transferring_body_id:
        body = Body.query.get_or_404(transferring_body_id)
        validate_body_user_groups_or_404(body.Name)
        browse_query = _build_transferring_body_filter_query(
            transferring_body_id
        )
    elif series_id:
        series = Series.query.get_or_404(series_id)
        validate_body_user_groups_or_404(series.body_series.Name)
        browse_query = _build_series_filter_query(series_id)
    elif consignment_id:
        consignment = Consignment.query.get_or_404(consignment_id)
        validate_body_user_groups_or_404(consignment.consignment_bodies.Name)

        browse_query = _build_consignment_filter_query(
            consignment_id,
            date_range,
            date_filter_field=date_filter_field,
        )
    else:
        browse_query = _build_browse_everything_query()

    if not consignment_id and date_range:
        dt_range = validate_date_range(date_range)

        date_filter = _build_date_range_filter(
            Consignment.TransferCompleteDatetime,
            dt_range["date_from"],
            dt_range["date_to"],
        )
        browse_query = browse_query.filter(date_filter)

    return browse_query.paginate(page=page, per_page=per_page)


def _build_fuzzy_search_query(query_string: str):
    filter_value = str(f"%{query_string}%").lower()

    query = (
        db.session.query(
            Body.Name.label("transferring_body"),
            Series.Name.label("series"),
            Consignment.ConsignmentReference.label("consignment_reference"),
            File.FileName.label("file_name"),
            Body.BodyId.label("body_id"),
            Series.SeriesId.label("series_id"),
        )
        .join(Series, Series.BodyId == Body.BodyId)
        .join(
            Consignment,
            and_(
                Consignment.BodyId == Body.BodyId,
                Consignment.SeriesId == Series.SeriesId,
            ),
        )
        .join(File, File.ConsignmentId == Consignment.ConsignmentId)
        .join(FileMetadata, FileMetadata.FileId == File.FileId)
        .where(
            and_(
                func.lower(File.FileType) == "file",
                or_(
                    func.lower(Consignment.ConsignmentReference).like(
                        filter_value
                    ),
                    func.lower(Consignment.ConsignmentType).like(filter_value),
                    func.lower(Consignment.ContactName).like(filter_value),
                    func.lower(Consignment.ContactEmail).like(filter_value),
                    func.cast(Consignment.TransferStartDatetime, Text).like(
                        filter_value
                    ),
                    func.cast(Consignment.TransferCompleteDatetime, Text).like(
                        filter_value
                    ),
                    func.cast(Consignment.ExportDatetime, Text).like(
                        filter_value
                    ),
                    func.lower(Body.Name).like(filter_value),
                    func.lower(Body.Description).like(filter_value),
                    func.lower(Series.Name).like(filter_value),
                    func.lower(Series.Description).like(filter_value),
                    func.lower(File.FileName).like(filter_value),
                    func.lower(File.FileReference).like(filter_value),
                    func.lower(FileMetadata.Value).like(filter_value),
                ),
            )
        )
        .distinct()
        .order_by(Body.Name, Series.Name)
    )

    return query


def _build_browse_everything_query():
    query = (
        db.session.query(
            Body.BodyId.label("transferring_body_id"),
            Body.Name.label("transferring_body"),
            Series.SeriesId.label("series_id"),
            Series.Name.label("series"),
            func.to_char(
                func.cast(func.max(Consignment.TransferCompleteDatetime), DATE),
                current_app.config["DEFAULT_DATE_FORMAT"],
            ).label("last_record_transferred"),
            func.count(func.distinct(Consignment.ConsignmentReference)).label(
                "consignment_in_series"
            ),
            func.count(func.distinct(File.FileId)).label("records_held"),
        )
        .join(Consignment, Consignment.ConsignmentId == File.ConsignmentId)
        .join(Body, Body.BodyId == Consignment.BodyId)
        .join(Series, Series.SeriesId == Consignment.SeriesId)
        .where(func.lower(File.FileType) == "file")
        .group_by(Body.BodyId, Series.SeriesId)
        .order_by(Body.Name, Series.Name)
    )

    return query


def _build_transferring_body_filter_query(transferring_body_id):
    query = (
        db.session.query(
            Body.BodyId.label("transferring_body_id"),
            Body.Name.label("transferring_body"),
            Series.SeriesId.label("series_id"),
            Series.Name.label("series"),
            func.to_char(
                func.cast(func.max(Consignment.TransferCompleteDatetime), DATE),
                current_app.config["DEFAULT_DATE_FORMAT"],
            ).label("last_record_transferred"),
            func.count(func.distinct(Consignment.ConsignmentReference)).label(
                "consignment_in_series"
            ),
            func.count(func.distinct(File.FileId)).label("records_held"),
        )
        .join(Consignment, Consignment.ConsignmentId == File.ConsignmentId)
        .join(Body, Body.BodyId == Consignment.BodyId)
        .join(Series, Series.SeriesId == Consignment.SeriesId)
        .where(
            (func.lower(File.FileType) == "file")
            & (Body.BodyId == transferring_body_id)
        )
        .group_by(Body.BodyId, Series.SeriesId)
        .order_by(Body.Name, Series.Name)
    )

    return query


def _build_series_filter_query(series_id):
    query = (
        db.session.query(
            Body.BodyId.label("transferring_body_id"),
            Body.Name.label("transferring_body"),
            Series.SeriesId.label("series_id"),
            Series.Name.label("series"),
            func.to_char(
                func.cast(func.max(Consignment.TransferCompleteDatetime), DATE),
                current_app.config["DEFAULT_DATE_FORMAT"],
            ).label("last_record_transferred"),
            func.count(func.distinct(File.FileId)).label("records_held"),
            Consignment.ConsignmentId.label("consignment_id"),
            Consignment.ConsignmentReference.label("consignment_reference"),
        )
        .join(Consignment, Consignment.ConsignmentId == File.ConsignmentId)
        .join(Body, Body.BodyId == Consignment.BodyId)
        .join(Series, Series.SeriesId == Consignment.SeriesId)
        .where(
            (func.lower(File.FileType) == "file")
            & (Series.SeriesId == series_id)
        )
        .group_by(Body.BodyId, Series.SeriesId, Consignment.ConsignmentId)
        .order_by(Body.Name, Series.Name)
    )

    return query


def _build_consignment_filter_query(
    consignment_id: uuid.UUID, date_range=None, date_filter_field=None
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
                    FileMetadata.PropertyName == "closure_start_date",
                    func.cast(FileMetadata.Value, DATE),
                ),
                else_=None,
            ),
        ).label("closure_start_date"),
        func.max(
            db.case(
                (
                    FileMetadata.PropertyName == "closure_period",
                    FileMetadata.Value,
                ),
                else_=None,
            ),
        ).label("closure_period"),
    )

    filters = [
        File.ConsignmentId == consignment_id,
        func.lower(File.FileType) == "file",
    ]

    sub_query = (
        select.join(FileMetadata, File.FileId == FileMetadata.FileId)
        .filter(*filters)
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
        sub_query.c.closure_type,
        func.to_char(
            sub_query.c.closure_start_date,
            current_app.config["DEFAULT_DATE_FORMAT"],
        ).label("closure_start_date"),
        sub_query.c.closure_period,
    )

    if date_range and date_filter_field is not None:
        dt_range = validate_date_range(date_range)
        if date_filter_field.lower() == "date_last_modified":
            date_filter = _build_date_range_filter(
                sub_query.c.date_last_modified,
                dt_range["date_from"],
                dt_range["date_to"],
            )
            query = query.filter(date_filter)

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
        query.join(File, FileMetadata.FileId == File.FileId)
        .join(Consignment, File.ConsignmentId == Consignment.ConsignmentId)
        .join(
            Body,
            Body.BodyId == Consignment.BodyId,
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
