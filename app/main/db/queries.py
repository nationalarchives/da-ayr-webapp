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
            Body.BodyId.label("BodyId"),
            Body.Name.label("TransferringBody"),
            Series.SeriesId.label("SeriesId"),
            Series.Name.label("Series"),
            Consignment.ConsignmentReference.label("ConsignmentReference"),
            File.FileName.label("FileName"),
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
                "transferring_body_id": r.BodyId,
                "transferring_body": r.TransferringBody,
                "series_id": r.SeriesId,
                "series": r.Series,
                "consignment_reference": r.ConsignmentReference,
                "file_name": r.FileName,
            }
            results.append(record)
    return results


def browse_data(transferring_body_id=None, series_id=None, consignment_id=None):
    results = []
    if transferring_body_id is not None:
        query = generate_transferring_body_filter_query(transferring_body_id)
    elif series_id is not None:
        query = generate_series_filter_query(series_id)
    elif consignment_id is not None:
        query = generate_consignment_reference_filter_query(consignment_id)
    else:
        query = generate_browse_everything_query()

    # print(query)
    query_results = None
    try:
        query_results = db.session.execute(query)
    except exc.SQLAlchemyError as e:
        print("Failed to return results from database with error : " + str(e))

    if query_results is not None:
        results = process_result(
            query_results, transferring_body_id, series_id, consignment_id
        )
    return results


def generate_browse_everything_query():
    query = (
        db.select(
            Body.BodyId.label("BodyId"),
            Body.Name.label("TransferringBody"),
            Series.SeriesId.label("SeriesId"),
            Series.Name.label("Series"),
            func.max(Consignment.TransferCompleteDatetime).label(
                "Last_Record_Transferred"
            ),
            func.count(func.distinct(Consignment.ConsignmentReference)).label(
                "Consignment_in_Series"
            ),
            func.count(func.distinct(File.FileId)).label("Records_Held"),
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
            Body.BodyId.label("BodyId"),
            Body.Name.label("TransferringBody"),
            Series.SeriesId.label("SeriesId"),
            Series.Name.label("Series"),
            func.max(Consignment.TransferCompleteDatetime).label(
                "Last_Record_Transferred"
            ),
            func.count(func.distinct(Consignment.ConsignmentReference)).label(
                "Consignment_in_Series"
            ),
            func.count(func.distinct(File.FileId)).label("Records_Held"),
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
            Body.BodyId.label("BodyId"),
            Body.Name.label("TransferringBody"),
            Series.SeriesId.label("SeriesId"),
            Series.Name.label("Series"),
            func.max(Consignment.TransferCompleteDatetime).label(
                "Last_Record_Transferred"
            ),
            func.count(func.distinct(File.FileId)).label("Records_Held"),
            Consignment.ConsignmentId.label("ConsignmentId"),
            Consignment.ConsignmentReference.label("Consignment_Reference"),
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
            func.max(FileMetadata.Value).label("LastModified"),
            File.FileId.label("FileId"),
            File.FileName.label("FileName"),
            func.max(FileMetadata.Value).label("Status"),
            Consignment.ConsignmentId.label("ConsignmentId"),
            Consignment.ConsignmentReference.label("Consignment_Reference"),
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


def get_user_accessible_transferring_bodies(access_token):
    unique_transferring_bodies = []
    bodies = None
    try:
        bodies = Body.query.all()
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


def process_result(
    query_results,
    transferring_body_id=None,
    series_id=None,
    consignment_id=None,
):
    results = []
    for r in query_results:
        if transferring_body_id is not None:
            record = {
                "transferring_body_id": r.BodyId,
                "transferring_body": r.TransferringBody,
                "series_id": r.SeriesId,
                "series": r.Series,
                "consignment_in_series": r.Consignment_in_Series,
                "last_record_transferred": r.Last_Record_Transferred,
                "records_held": r.Records_Held,
            }
        elif series_id is not None:
            record = {
                "transferring_body_id": r.BodyId,
                "transferring_body": r.TransferringBody,
                "series_id": r.SeriesId,
                "series": r.Series,
                "last_record_transferred": r.Last_Record_Transferred,
                "records_held": r.Records_Held,
                "consignment_id": r.ConsignmentId,
                "consignment_reference": r.Consignment_Reference,
            }
        elif consignment_id is not None:
            record = {
                "last_modified": r.LastModified,
                "file_id": r.FileId,
                "file_name": r.FileName,
                "status": r.Status,
                "consignment_id": r.ConsignmentId,
                "consignment_reference": r.Consignment_Reference,
            }
        else:
            record = {
                "transferring_body_id": r.BodyId,
                "transferring_body": r.TransferringBody,
                "series_id": r.SeriesId,
                "series": r.Series,
                "consignment_in_series": r.Consignment_in_Series,
                "last_record_transferred": r.Last_Record_Transferred,
                "records_held": r.Records_Held,
            }
        results.append(record)
    return results


def get_file_meta_data(file_id):
    results = []
    query = (
        db.select(FileMetadata.PropertyName, FileMetadata.Value)
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
            record = {"PropertyName": r.PropertyName, "PropertyValue": r.Value}
            results.append(record)
    return results


def get_file_data_grouped_by_transferring_body_and_series():
    results = []

    query = (
        db.select(
            Body.Name.label("transferring_body"),
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
        .group_by(Body.BodyId, Series.SeriesId)
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
                "transferring_body": r.transferring_body,
                "series": r.series,
                "consignment_in_series": r.consignment_in_series,
                "last_record_transferred": r.last_record_transferred,
                "records_held": r.records_held,
            }
            results.append(record)
    return results


def browse_view_transferring_body(transferring_body):
    results = []
    query = (
        db.select(
            Body.Name.label("TransferringBody"),
            Series.Name.label("Series"),
            func.max(Consignment.TransferCompleteDatetime).label(
                "Last_Record_Transferred"
            ),
            func.count(func.distinct(Consignment.ConsignmentReference)).label(
                "Consignment_in_Series"
            ),
            func.count(func.distinct(File.FileId)).label("Records_Held"),
        )
        .join(Consignment, Consignment.ConsignmentId == File.ConsignmentId)
        .join(Body, Body.BodyId == Consignment.BodyId)
        .join(Series, Series.SeriesId == Consignment.SeriesId)
        .where(func.lower(Body.Name) == func.lower(transferring_body))
        .group_by(Body.BodyId, Series.SeriesId)
        .order_by(Body.Name, Series.Name)
    )

    try:
        query_results = db.session.execute(query)

        for r in query_results:
            record = {
                "TransferringBody": r.TransferringBody,
                "Series": r.Series,
                "Consignment_in_Series": r.Consignment_in_Series,
                "Last_Record_Transferred": r.Last_Record_Transferred,
                "Records_Held": r.Records_Held,
            }
            results.append(record)
    except exc.SQLAlchemyError as e:
        print("Failed to return results from database with error : " + str(e))
    return results


def get_full_list_of_transferring_bodies():
    bodies = []
    try:
        bodies = Body.query.all()
    except exc.SQLAlchemyError as e:
        print("Failed to return results from database with error : " + str(e))
    return bodies
