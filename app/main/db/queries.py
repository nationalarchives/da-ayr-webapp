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
