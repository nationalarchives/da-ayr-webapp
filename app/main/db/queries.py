from sqlalchemy import Text, and_, exc, func, or_

from app.main.db.models import Body, Consignment, File, FileMetadata, Series, db


def fuzzy_search(query_string):
    results = []
    filter_value = str(f"%{query_string}%").lower()

    query = (
        db.select(
            Body.Name.label("TransferringBody"),
            Series.Name.label("Series"),
            Consignment.ConsignmentReference,
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
    )

    try:
        result = db.session.execute(query)

        for r in result:
            record = {
                "TransferringBody": r.TransferringBody,
                "Series": r.Series,
                "ConsignmentReference": r.ConsignmentReference,
                "FileName": r.FileName,
            }
            results.append(record)
    except exc.SQLAlchemyError as e:
        print("Failed to return results from database with error : " + str(e))
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
