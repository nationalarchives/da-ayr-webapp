from sqlalchemy import Text, and_, exc, func, or_

from app.main.authorize.keycloak_manager import (
    get_user_transferring_body_groups,
)
from app.main.db.models import Body, Consignment, File, FileMetadata, Series, db


def fuzzy_search(query_string):
    results = []
    filter_value = str(f"%{query_string}%").lower()

    query = (
        db.select(
            Body.BodyId.label("body_id"),
            Body.Name.label("transferring_body"),
            Series.SeriesId.label("series_id"),
            Series.Name.label("series"),
            Consignment.ConsignmentReference.label("consignment_reference"),
            File.FileName.label("file_name"),
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
    query_results = None
    try:
        query_results = db.session.execute(query)
    except exc.SQLAlchemyError as e:
        print("Failed to return results from database with error : " + str(e))

    if query_results is not None:
        for r in query_results:
            record = {
                "transferring_body_id": r.body_id,
                "transferring_body": r.transferring_body,
                "series_id": r.series_id,
                "series": r.series,
                "consignment_reference": r.consignment_reference,
                "file_name": r.file_name,
            }
            results.append(record)
    return results


def browse_data(transferring_body_id=None, series_id=None, consignment_id=None):
    results = []
    try:
        if transferring_body_id is not None:
            query_results = db.session.execute(
                generate_transferring_body_filter_query(transferring_body_id)
            )
            results = [
                {
                    "transferring_body_id": r.body_id,
                    "transferring_body": r.transferring_body,
                    "series_id": r.series_id,
                    "series": r.series,
                    "consignment_in_series": r.consignment_in_series,
                    "last_record_transferred": r.last_record_transferred,
                    "records_held": r.records_held,
                }
                for r in query_results
            ]
        elif series_id is not None:
            query_results = db.session.execute(
                generate_series_filter_query(series_id)
            )
            results = [
                {
                    "transferring_body_id": r.body_id,
                    "transferring_body": r.transferring_body,
                    "series_id": r.series_id,
                    "series": r.series,
                    "last_record_transferred": r.last_record_transferred,
                    "records_held": r.records_held,
                    "consignment_id": r.consignment_id,
                    "consignment_reference": r.consignment_reference,
                }
                for r in query_results
            ]
        elif consignment_id is not None:
            query_results = db.session.execute(
                generate_consignment_reference_filter_query(consignment_id)
            )
            results = [
                {
                    "last_modified": r.last_modified,
                    "file_id": r.file_id,
                    "file_name": r.file_name,
                    "status": r.status,
                    "consignment_id": r.consignment_id,
                    "consignment_reference": r.consignment_reference,
                }
                for r in query_results
            ]
        else:
            query_results = db.session.execute(
                generate_browse_everything_query()
            )
            results = [
                {
                    "transferring_body_id": r.body_id,
                    "transferring_body": r.transferring_body,
                    "series_id": r.series_id,
                    "series": r.series,
                    "consignment_in_series": r.consignment_in_series,
                    "last_record_transferred": r.last_record_transferred,
                    "records_held": r.records_held,
                }
                for r in query_results
            ]
    except exc.SQLAlchemyError as e:
        print("Failed to return results from database with error : " + str(e))
    return results


def get_user_accessible_transferring_bodies(access_token):
    unique_transferring_bodies = []
    bodies = None
    try:
        query = db.select(Body.BodyId, Body.Name, Body.Description)
        bodies = db.session.execute(query)
    except exc.SQLAlchemyError as e:
        print("Failed to return results from database with error : " + str(e))

    # get transferring bodies for which user has access to
    user_transferring_body_groups = get_user_transferring_body_groups(
        access_token
    )

    if bodies is not None and user_transferring_body_groups is not None:
        for body in bodies:
            group_name = body.Name
            if len(user_transferring_body_groups) > 0:
                for user_group in user_transferring_body_groups:
                    if (
                        user_group.strip().replace(" ", "").lower()
                        == group_name.strip().replace(" ", "").lower()
                    ):
                        unique_transferring_bodies.append(group_name)
    return unique_transferring_bodies


def get_file_metadata(file_id):
    results = []
    query = (
        db.select(
            FileMetadata.PropertyName.label("property_name"),
            FileMetadata.Value.label("property_value"),
        )
        .join(File, FileMetadata.FileId == File.FileId)
        .where((func.lower(File.FileType) == "file") & (File.FileId == file_id))
    )
    query_results = None
    try:
        query_results = db.session.execute(query)
    except exc.SQLAlchemyError as e:
        print("Failed to return results from database with error : " + str(e))

    if query_results is not None:
        for r in query_results:
            record = {
                "property_name": r.property_name,
                "property_value": r.property_value,
            }
            results.append(record)
    return results


def generate_browse_everything_query():
    query = (
        db.select(
            Body.BodyId.label("body_id"),
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
        .join(Body, Body.BodyId == Consignment.BodyId)
        .join(Series, Series.SeriesId == Consignment.SeriesId)
        .where(func.lower(File.FileType) == "file")
        .group_by(Body.BodyId, Series.SeriesId)
        .order_by(Body.Name, Series.Name)
    )

    return query


def generate_transferring_body_filter_query(transferring_body_id):
    query = (
        db.select(
            Body.BodyId.label("body_id"),
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


def generate_series_filter_query(series_id):
    query = (
        db.select(
            Body.BodyId.label("body_id"),
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


def generate_consignment_reference_filter_query(consignment_id):
    query = (
        db.select(
            func.max(FileMetadata.Value).label("last_modified"),
            File.FileId.label("file_id"),
            File.FileName.label("file_name"),
            func.max(FileMetadata.Value).label("status"),
            Consignment.ConsignmentId.label("consignment_id"),
            Consignment.ConsignmentReference.label("consignment_reference"),
        )
        .join(Consignment, Consignment.ConsignmentId == File.ConsignmentId)
        .join(Body, Body.BodyId == Consignment.BodyId)
        .join(Series, Series.SeriesId == Consignment.SeriesId)
        .join(FileMetadata, FileMetadata.FileId == File.FileId)
        .where(
            (func.lower(File.FileType) == "file")
            & (Consignment.ConsignmentId == consignment_id)
        )
        .group_by(File.FileId, File.FileName, Consignment.ConsignmentId)
        .order_by(File.FileName)
    )

    return query
