from sqlalchemy import Text, and_, func, or_

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
                    # func.lower(FileMetadata.PropertyName).like(filter_value),
                    func.lower(FileMetadata.Value).like(filter_value),
                ),
            )
        )
        .distinct()
    )
    # print(str(query))
    result = db.session.execute(query)

    for r in result:
        # print(r)
        record = {
            "TransferringBody": r.TransferringBody,
            "Series": r.Series,
            "ConsignmentReference": r.ConsignmentReference,
            "FileName": r.FileName,
        }
        # print(record)
        results.append(record)
    return results


def browse_view(transferring_body=None):
    results = []
    try:
        if transferring_body is not None:
            query = (
                db.select(
                    Body.Name.label("TransferringBody"),
                    Series.Name.label("Series"),
                    func.max(Consignment.TransferCompleteDatetime).label(
                        "Last_Record_Transferred"
                    ),
                    func.count(
                        func.distinct(Consignment.ConsignmentReference)
                    ).label("Consignment_in_Series"),
                    func.count(func.distinct(File.FileId)).label(
                        "Records_Held"
                    ),
                )
                .join(
                    Consignment, Consignment.ConsignmentId == File.ConsignmentId
                )
                .join(Body, Body.BodyId == Consignment.BodyId)
                .join(Series, Series.SeriesId == Consignment.SeriesId)
                .where(func.lower(Body.Name) == func.lower(transferring_body))
                .group_by(Body.BodyId, Series.SeriesId)
                .order_by(Body.Name, Series.Name)
            )
            # print(query)
        else:
            query = (
                db.select(
                    Body.Name.label("TransferringBody"),
                    Series.Name.label("Series"),
                    func.max(Consignment.TransferCompleteDatetime).label(
                        "Last_Record_Transferred"
                    ),
                    func.count(
                        func.distinct(Consignment.ConsignmentReference)
                    ).label("Consignment_in_Series"),
                    func.count(func.distinct(File.FileId)).label(
                        "Records_Held"
                    ),
                )
                .join(
                    Consignment, Consignment.ConsignmentId == File.ConsignmentId
                )
                .join(Body, Body.BodyId == Consignment.BodyId)
                .join(Series, Series.SeriesId == Consignment.SeriesId)
                .group_by(Body.BodyId, Series.SeriesId)
                .order_by(Body.Name, Series.Name)
            )
            # print(query)
        query_results = db.session.execute(query)

        for r in query_results:
            # print(r)
            record = {
                "TransferringBody": r.TransferringBody,
                "Series": r.Series,
                "Consignment_in_Series": r.Consignment_in_Series,
                "Last_Record_Transferred": r.Last_Record_Transferred,
                "Records_Held": r.Records_Held,
            }
            # print(record)
            results.append(record)
    except Exception as error:
        print("Error while fetching data from PostgresSQL", error)
    return results


def browse_view_series(series):
    results = []
    try:
        query = (
            db.select(
                Body.Name.label("TransferringBody"),
                Series.Name.label("Series"),
                func.max(Consignment.TransferCompleteDatetime).label(
                    "Last_Record_Transferred"
                ),
                func.count(func.distinct(File.FileId)).label("Records_Held"),
                Consignment.ConsignmentReference.label("Consignment_Reference"),
            )
            .join(Consignment, Consignment.ConsignmentId == File.ConsignmentId)
            .join(Body, Body.BodyId == Consignment.BodyId)
            .join(Series, Series.SeriesId == Consignment.SeriesId)
            .where(func.lower(Series.Name) == func.lower(series))
            .group_by(
                Body.BodyId, Series.SeriesId, Consignment.ConsignmentReference
            )
            .order_by(Body.Name, Series.Name)
        )
        # print(query)
        query_results = db.session.execute(query)

        for r in query_results:
            print(r)
            record = {
                "TransferringBody": r.TransferringBody,
                "Series": r.Series,
                "Last_Record_Transferred": r.Last_Record_Transferred,
                "Records_Held": r.Records_Held,
                "ConsignmentReference": r.Consignment_Reference,
            }
            # print(record)
            results.append(record)
    except Exception as error:
        print("Error while fetching data from PostgresSQL", error)
    return results


def browse_view_consignment_reference(consignment_reference):
    results = []
    try:
        query = (
            db.select(
                FileMetadata.Value.label("LastModified"),
                File.FileName.label("FileName"),
                FileMetadata.Value.label("Status"),
                File.FileName,
                Consignment.ConsignmentReference.label("Consignment_Reference"),
            )
            .join(Consignment, Consignment.ConsignmentId == File.ConsignmentId)
            .join(Body, Body.BodyId == Consignment.BodyId)
            .join(Series, Series.SeriesId == Consignment.SeriesId)
            .where(
                func.lower(Consignment.ConsignmentReference)
                == func.lower(consignment_reference)
            )
            .group_by(
                Body.BodyId, Series.SeriesId, Consignment.ConsignmentReference
            )
            .order_by(Body.Name, Series.Name)
        )
        # print(query)
        query_results = db.session.execute(query)

        for r in query_results:
            print(r)
            record = {
                "TransferringBody": r.TransferringBody,
                "Series": r.Series,
                "Last_Record_Transferred": r.Last_Record_Transferred,
                "Records_Held": r.Records_Held,
                "ConsignmentReference": r.Consignment_Reference,
            }
            # print(record)
            results.append(record)
    except Exception as error:
        print("Error while fetching data from PostgresSQL", error)
    return results


def browse_view_pavan(transferring_body):
    results = []
    try:
        subq1 = (
            db.select(
                Consignment.BodyId,
                Consignment.SeriesId,
                Consignment.ConsignmentId,
                func.max(Consignment.TransferCompleteDatetime).label(
                    "LastTransferredDate"
                ),
                func.count(Consignment.ConsignmentId).label("ConsignmentCount"),
                func.count(File.FileId).label("FileCount"),
            )
            .join(File, File.ConsignmentId == Consignment.ConsignmentId)
            .group_by(
                Consignment.BodyId,
                Consignment.SeriesId,
                Consignment.ConsignmentId,
            )
            .cte()
        )

        query = (
            db.select(
                Body.Name.label("TransferringBody"),
                Series.Name.label("Series"),
                func.max(subq1.c.LastTransferredDate).label(
                    "Last_Record_Transferred"
                ),
                func.count(subq1.c.ConsignmentCount).label(
                    "Consignment_in_Series"
                ),
                func.sum(subq1.c.FileCount).label("Records_Held"),
            )
            .join(Body, Body.BodyId == subq1.c.BodyId)
            .join(
                Series,
                Series.BodyId == Body.BodyId
                and Series.SeriesId == subq1.c.SeriesId,
            )
            .where(func.lower(Body.Name) == func.lower(transferring_body))
            .group_by(Body.Name, Series.Name)
            .order_by(Body.Name, Series.Name)
        )
        # print(query)
        query_results = db.session.execute(query)

        for r in query_results:
            print(r)
            record = {
                "TransferringBody": transferring_body,
                "Series": r.Series,
                "Consignment_in_Series": r.Consignment_in_Series,
                "Last_Record_Transferred": r.Last_Record_Transferred,
                "Records_Held": r.Records_Held,
            }
            # print(record)
            results.append(record)
    except Exception as error:
        print("Error while fetching data from PostgresSQL", error)
    return results


def get_full_list_of_transferring_bodies():
    bodies = []
    try:
        # query = db.select(Body.BodyId, Body.Name, Body.Description)
        # bodies = db.session.execute(query)
        bodies = Body.query.all()
    except Exception as error:
        print("Error while fetching data from PostgresSQL", error)
    return bodies


def get_full_list_of_series():
    series = []
    try:
        series = Series.query.all()
    except Exception as error:
        print("Error while fetching data from PostgresSQL", error)
    return series


def get_full_list_of_consignments():
    consignments = []
    try:
        consignments = Consignment.query.all()
    except Exception as error:
        print("Error while fetching data from PostgresSQL", error)
    return consignments


def get_full_list_of_files():
    files = []
    try:
        files = File.query.all()
    except Exception as error:
        print("Error while fetching data from PostgresSQL", error)
    return files


def get_full_list_of_file_meta_data(file_id):
    file_meta_data = []
    try:
        query = (
            db.select(FileMetadata.PropertyName, FileMetadata.Value)
            .join(File, FileMetadata.FileId == File.FileId)
            .where(func.lower(File.FileId) == func.lower(file_id))
        )
        file_meta_data = db.session.execute(query)
    except Exception as error:
        print("Error while fetching data from PostgresSQL", error)
    return file_meta_data
