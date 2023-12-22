import uuid

from app.main.db.models import Body, Consignment, File, FileMetadata, Series, db


def create_multiple_test_records():
    new_body = Body(
        BodyId=uuid.uuid4(), Name="test body1", Description="test body1"
    )
    db.session.add(new_body)
    db.session.commit()

    new_series = Series(
        SeriesId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        Name="test series1",
        Description="test series1",
    )
    db.session.add(new_series)
    db.session.commit()

    new_consignment = Consignment(
        ConsignmentId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        SeriesId=new_series.SeriesId,
        ConsignmentReference="test consignment1",
        ContactName="test young",
        ContactEmail="test1@test.com",
        ConsignmentType="standard",
        TransferStartDatetime="2023-01-01",
        TransferCompleteDatetime="2023-01-01",
    )
    db.session.add(new_consignment)
    db.session.commit()

    file_1 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=new_consignment.ConsignmentId,
        FileName="test_file1.pdf",
        FileType="file",
        FileReference="test_file1.pdf",
        FilePath="/data/test_file1.pdf",
    )
    db.session.add(file_1)
    db.session.commit()

    file_1_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_1.FileId,
        PropertyName="file_name",
        Value="test_file1.pdf",
    )
    db.session.add(file_1_metadata)
    db.session.commit()

    file_1_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_1.FileId,
        PropertyName="date_last_modified",
        Value="2023-12-15",
    )
    db.session.add(file_1_metadata)
    db.session.commit()

    file_1_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_1.FileId,
        PropertyName="closure_type",
        Value="open",
    )
    db.session.add(file_1_metadata)
    db.session.commit()

    file_1_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_1.FileId,
        PropertyName="file_type",
        Value="pdf",
    )
    db.session.add(file_1_metadata)
    db.session.commit()

    new_body = Body(
        BodyId=uuid.uuid4(), Name="test body2", Description="test body2"
    )
    db.session.add(new_body)
    db.session.commit()

    new_series = Series(
        SeriesId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        Name="test series2",
        Description="test series2",
    )
    db.session.add(new_series)
    db.session.commit()

    new_consignment = Consignment(
        ConsignmentId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        SeriesId=new_series.SeriesId,
        ConsignmentReference="test consignment2",
        ContactName="test young",
        ContactEmail="test2@test.com",
        ConsignmentType="standard",
        TransferStartDatetime="2023-01-01",
        TransferCompleteDatetime="2023-01-01",
    )
    db.session.add(new_consignment)
    db.session.commit()

    file_2 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=new_consignment.ConsignmentId,
        FileName="test_file2.txt",
        FileType="file",
        FileReference="test_file2.txt",
        FilePath="/data/test_file2.txt",
    )
    db.session.add(file_2)
    db.session.commit()

    file_2_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_2.FileId,
        PropertyName="file_name",
        Value="test_file2.pdf",
    )
    db.session.add(file_2_metadata)
    db.session.commit()

    file_2_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_2.FileId,
        PropertyName="closure_type",
        Value="closed",
    )
    db.session.add(file_2_metadata)
    db.session.commit()

    file_2_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_2.FileId,
        PropertyName="file_type",
        Value="txt",
    )
    db.session.add(file_2_metadata)
    db.session.commit()

    new_body = Body(
        BodyId=uuid.uuid4(), Name="testing body3", Description="testing bodyy3"
    )
    db.session.add(new_body)
    db.session.commit()

    new_series = Series(
        SeriesId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        Name="test series3",
        Description="test series3",
    )
    db.session.add(new_series)
    db.session.commit()

    new_consignment = Consignment(
        ConsignmentId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        SeriesId=new_series.SeriesId,
        ConsignmentReference="test consignment3",
        ContactName="test young",
        ContactEmail="test3@test.com",
        ConsignmentType="standard",
        TransferStartDatetime="2023-01-01",
        TransferCompleteDatetime="2023-01-01",
    )
    db.session.add(new_consignment)
    db.session.commit()

    file_3 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=new_consignment.ConsignmentId,
        FileName="test_file3.pdf",
        FileType="file",
        FileReference="test_file3.pdf",
        FilePath="/data/test_file3.pdf",
    )
    db.session.add(file_3)
    db.session.commit()

    file_3_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_3.FileId,
        PropertyName="file_name",
        Value="test_file3.pdf",
    )
    db.session.add(file_3_metadata)
    db.session.commit()

    file_3_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_3.FileId,
        PropertyName="closure_type",
        Value="open",
    )
    db.session.add(file_3_metadata)
    db.session.commit()

    file_3_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_3.FileId,
        PropertyName="file_type",
        Value="pdf",
    )
    db.session.add(file_3_metadata)
    db.session.commit()

    new_body = Body(
        BodyId=uuid.uuid4(), Name="testing body4", Description="testing body4"
    )
    db.session.add(new_body)
    db.session.commit()

    new_series = Series(
        SeriesId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        Name="test series4",
        Description="test series4",
    )
    db.session.add(new_series)
    db.session.commit()

    new_consignment = Consignment(
        ConsignmentId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        SeriesId=new_series.SeriesId,
        ConsignmentReference="test consignment4",
        ContactName="test young",
        ContactEmail="test4@test.com",
        ConsignmentType="standard",
        TransferStartDatetime="2023-01-01",
        TransferCompleteDatetime="2023-01-01",
    )
    db.session.add(new_consignment)
    db.session.commit()

    file_4 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=new_consignment.ConsignmentId,
        FileName="test_file4.txt",
        FileType="file",
        FileReference="test_file4.txt",
        FilePath="/data/test_file4.txt",
    )
    db.session.add(file_4)
    db.session.commit()

    file_4_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_4.FileId,
        PropertyName="file_name",
        Value="test_file4.pdf",
    )
    db.session.add(file_4_metadata)
    db.session.commit()

    file_4_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_4.FileId,
        PropertyName="closure_type",
        Value="closed",
    )
    db.session.add(file_4_metadata)
    db.session.commit()

    file_4_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_4.FileId,
        PropertyName="file_type",
        Value="txt",
    )
    db.session.add(file_4_metadata)
    db.session.commit()

    new_body = Body(
        BodyId=uuid.uuid4(), Name="testing body5", Description="testing body5"
    )
    db.session.add(new_body)
    db.session.commit()

    new_series = Series(
        SeriesId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        Name="test series5",
        Description="test series5",
    )
    db.session.add(new_series)
    db.session.commit()

    new_consignment = Consignment(
        ConsignmentId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        SeriesId=new_series.SeriesId,
        ConsignmentReference="test consignment5",
        ContactName="test young",
        ContactEmail="test5@test.com",
        ConsignmentType="standard",
        TransferStartDatetime="2023-01-01",
        TransferCompleteDatetime="2023-02-15",
    )
    db.session.add(new_consignment)
    db.session.commit()

    file_5 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=new_consignment.ConsignmentId,
        FileName="test_file5.txt",
        FileType="file",
        FileReference="test_file5.txt",
        FilePath="/data/test_file5.txt",
    )
    db.session.add(file_5)
    db.session.commit()

    file_5_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_5.FileId,
        PropertyName="file_name",
        Value="test_file5.pdf",
    )
    db.session.add(file_5_metadata)
    db.session.commit()

    file_5_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_5.FileId,
        PropertyName="closure_type",
        Value="closed",
    )
    db.session.add(file_5_metadata)
    db.session.commit()

    file_5_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_5.FileId,
        PropertyName="file_type",
        Value="txt",
    )
    db.session.add(file_5_metadata)
    db.session.commit()

    new_body = Body(
        BodyId=uuid.uuid4(), Name="testing body6", Description="testing body6"
    )
    db.session.add(new_body)
    db.session.commit()

    new_series = Series(
        SeriesId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        Name="test series6",
        Description="test series6",
    )
    db.session.add(new_series)
    db.session.commit()

    new_consignment = Consignment(
        ConsignmentId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        SeriesId=new_series.SeriesId,
        ConsignmentReference="test consignment6",
        ContactName="test young",
        ContactEmail="test6@test.com",
        ConsignmentType="standard",
        TransferStartDatetime="2023-01-01",
        TransferCompleteDatetime="2023-02-15",
    )
    db.session.add(new_consignment)
    db.session.commit()

    file_6 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=new_consignment.ConsignmentId,
        FileName="test_file6.txt",
        FileType="file",
        FileReference="test_file6.txt",
        FilePath="/data/test_file6.txt",
    )
    db.session.add(file_6)
    db.session.commit()

    file_6_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_6.FileId,
        PropertyName="file_name",
        Value="test_file6.pdf",
    )
    db.session.add(file_6_metadata)
    db.session.commit()

    file_6_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_6.FileId,
        PropertyName="closure_type",
        Value="closed",
    )
    db.session.add(file_6_metadata)
    db.session.commit()

    file_6_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_6.FileId,
        PropertyName="file_type",
        Value="txt",
    )
    db.session.add(file_6_metadata)
    db.session.commit()

    new_body = Body(
        BodyId=uuid.uuid4(), Name="testing body7", Description="testing body7"
    )
    db.session.add(new_body)
    db.session.commit()

    new_series = Series(
        SeriesId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        Name="test series7",
        Description="test series7",
    )
    db.session.add(new_series)
    db.session.commit()

    new_consignment = Consignment(
        ConsignmentId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        SeriesId=new_series.SeriesId,
        ConsignmentReference="test consignment7",
        ContactName="test young",
        ContactEmail="test7@test.com",
        ConsignmentType="standard",
        TransferStartDatetime="2023-01-01",
        TransferCompleteDatetime="2023-02-15",
    )
    db.session.add(new_consignment)
    db.session.commit()

    file_7 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=new_consignment.ConsignmentId,
        FileName="test_file7.txt",
        FileType="file",
        FileReference="test_file7.txt",
        FilePath="/data/test_file7.txt",
    )
    db.session.add(file_7)
    db.session.commit()

    file_7_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_7.FileId,
        PropertyName="file_name",
        Value="test_file7.pdf",
    )
    db.session.add(file_7_metadata)
    db.session.commit()

    file_7_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_7.FileId,
        PropertyName="closure_type",
        Value="open",
    )
    db.session.add(file_7_metadata)
    db.session.commit()

    file_7_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_7.FileId,
        PropertyName="file_type",
        Value="txt",
    )
    db.session.add(file_7_metadata)
    db.session.commit()

    new_body = Body(
        BodyId=uuid.uuid4(), Name="testing body8", Description="testing body8"
    )
    db.session.add(new_body)
    db.session.commit()

    new_series = Series(
        SeriesId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        Name="test series8",
        Description="test series8",
    )
    db.session.add(new_series)
    db.session.commit()

    new_consignment = Consignment(
        ConsignmentId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        SeriesId=new_series.SeriesId,
        ConsignmentReference="test consignment8",
        ContactName="test young",
        ContactEmail="test8@test.com",
        ConsignmentType="standard",
        TransferStartDatetime="2023-01-01",
        TransferCompleteDatetime="2023-02-15",
    )
    db.session.add(new_consignment)
    db.session.commit()

    file_8 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=new_consignment.ConsignmentId,
        FileName="test_file8.txt",
        FileType="file",
        FileReference="test_file8.txt",
        FilePath="/data/test_file8.txt",
    )
    db.session.add(file_8)
    db.session.commit()

    file_8_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_8.FileId,
        PropertyName="file_name",
        Value="test_file8.pdf",
    )
    db.session.add(file_8_metadata)
    db.session.commit()

    file_8_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_8.FileId,
        PropertyName="closure_type",
        Value="open",
    )
    db.session.add(file_8_metadata)
    db.session.commit()

    file_8_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_8.FileId,
        PropertyName="file_type",
        Value="txt",
    )
    db.session.add(file_8_metadata)
    db.session.commit()

    new_body = Body(
        BodyId=uuid.uuid4(), Name="testing body9", Description="testing body9"
    )
    db.session.add(new_body)
    db.session.commit()

    new_series = Series(
        SeriesId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        Name="test series9",
        Description="test series9",
    )
    db.session.add(new_series)
    db.session.commit()

    new_consignment = Consignment(
        ConsignmentId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        SeriesId=new_series.SeriesId,
        ConsignmentReference="test consignment9",
        ContactName="test young",
        ContactEmail="test9@test.com",
        ConsignmentType="standard",
        TransferStartDatetime="2023-01-01",
        TransferCompleteDatetime="2023-02-15",
    )
    db.session.add(new_consignment)
    db.session.commit()

    file_9 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=new_consignment.ConsignmentId,
        FileName="test_file9.txt",
        FileType="file",
        FileReference="test_file9.txt",
        FilePath="/data/test_file9.txt",
    )
    db.session.add(file_9)
    db.session.commit()

    file_9_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_9.FileId,
        PropertyName="file_name",
        Value="test_file9.pdf",
    )
    db.session.add(file_9_metadata)
    db.session.commit()

    file_9_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_9.FileId,
        PropertyName="closure_type",
        Value="open",
    )
    db.session.add(file_9_metadata)
    db.session.commit()

    file_9_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_9.FileId,
        PropertyName="file_type",
        Value="txt",
    )
    db.session.add(file_9_metadata)
    db.session.commit()

    new_body = Body(
        BodyId=uuid.uuid4(), Name="testing body10", Description="testing body10"
    )
    db.session.add(new_body)
    db.session.commit()

    new_series = Series(
        SeriesId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        Name="test series10",
        Description="test series10",
    )
    db.session.add(new_series)
    db.session.commit()

    new_consignment = Consignment(
        ConsignmentId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        SeriesId=new_series.SeriesId,
        ConsignmentReference="test consignment10",
        ContactName="test young",
        ContactEmail="test10@test.com",
        ConsignmentType="standard",
        TransferStartDatetime="2023-01-01",
        TransferCompleteDatetime="2023-01-01",
    )
    db.session.add(new_consignment)
    db.session.commit()

    file_10 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=new_consignment.ConsignmentId,
        FileName="test_file10.txt",
        FileType="file",
        FileReference="test_file10.txt",
        FilePath="/data/test_file10.txt",
    )
    db.session.add(file_10)
    db.session.commit()

    file_10_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_10.FileId,
        PropertyName="file_name",
        Value="test_file10.pdf",
    )
    db.session.add(file_10_metadata)
    db.session.commit()

    file_10_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_10.FileId,
        PropertyName="closure_type",
        Value="closed",
    )
    db.session.add(file_10_metadata)
    db.session.commit()

    file_10_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_10.FileId,
        PropertyName="file_type",
        Value="txt",
    )
    db.session.add(file_10_metadata)
    db.session.commit()

    new_body = Body(
        BodyId=uuid.uuid4(), Name="testing body11", Description="test body11"
    )
    db.session.add(new_body)
    db.session.commit()

    new_series = Series(
        SeriesId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        Name="test series11",
        Description="test series11",
    )
    db.session.add(new_series)
    db.session.commit()

    new_consignment = Consignment(
        ConsignmentId=uuid.uuid4(),
        BodyId=new_body.BodyId,
        SeriesId=new_series.SeriesId,
        ConsignmentReference="test consignment11",
        ContactName="test young",
        ContactEmail="test11@test.com",
        ConsignmentType="standard",
        TransferStartDatetime="2023-01-01",
        TransferCompleteDatetime="2023-01-01",
    )
    db.session.add(new_consignment)
    db.session.commit()

    file_11 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=new_consignment.ConsignmentId,
        FileName="test_file11.txt",
        FileType="file",
        FileReference="test_file11.txt",
        FilePath="/data/test_file11.txt",
    )
    db.session.add(file_11)
    db.session.commit()

    file_11_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_11.FileId,
        PropertyName="file_name",
        Value="test_file11.pdf",
    )
    db.session.add(file_11_metadata)
    db.session.commit()

    file_11_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_11.FileId,
        PropertyName="closure_type",
        Value="closed",
    )
    db.session.add(file_11_metadata)
    db.session.commit()

    file_11_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_11.FileId,
        PropertyName="file_type",
        Value="txt",
    )
    db.session.add(file_11_metadata)
    db.session.commit()

    return [
        file_1,
        file_2,
        file_3,
        file_4,
        file_5,
        file_6,
        file_7,
        file_8,
        file_9,
        file_10,
        file_11,
    ]


def create_multiple_files_for_consignment(consignment_id):
    file_2 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=consignment_id,
        FileName="test_file2.txt",
        FileType="file",
        FileReference="test_file2.txt",
        FilePath="/data/test_file2.txt",
    )
    db.session.add(file_2)
    db.session.commit()

    file_2_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_2.FileId,
        PropertyName="file_name",
        Value="test_file2.txt",
    )
    db.session.add(file_2_metadata)
    db.session.commit()

    file_2_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_2.FileId,
        PropertyName="date_last_modified",
        Value="2023-12-15",
    )
    db.session.add(file_2_metadata)
    db.session.commit()

    file_2_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_2.FileId,
        PropertyName="closure_type",
        Value="closed",
    )
    db.session.add(file_2_metadata)
    db.session.commit()

    file_2_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_2.FileId,
        PropertyName="closure_start_date",
        Value="2023-12-15",
    )
    db.session.add(file_2_metadata)
    db.session.commit()

    file_2_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_2.FileId,
        PropertyName="closure_expiry",
        Value="50",
    )
    db.session.add(file_2_metadata)
    db.session.commit()

    file_2_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_2.FileId,
        PropertyName="file_type",
        Value="txt",
    )
    db.session.add(file_2_metadata)
    db.session.commit()

    file_3 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=consignment_id,
        FileName="test_file3.pdf",
        FileType="file",
        FileReference="test_file3.pdf",
        FilePath="/data/test_file3.pdf",
    )
    db.session.add(file_3)
    db.session.commit()

    file_3_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_3.FileId,
        PropertyName="file_name",
        Value="test_file3.pdf",
    )
    db.session.add(file_3_metadata)
    db.session.commit()

    file_3_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_3.FileId,
        PropertyName="date_last_modified",
        Value="2023-12-15",
    )
    db.session.add(file_3_metadata)
    db.session.commit()

    file_3_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_3.FileId,
        PropertyName="closure_type",
        Value="open",
    )
    db.session.add(file_3_metadata)
    db.session.commit()

    file_3_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_3.FileId,
        PropertyName="closure_start_date",
        Value=None,
    )
    db.session.add(file_3_metadata)
    db.session.commit()

    file_3_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_3.FileId,
        PropertyName="closure_expiry",
        Value=None,
    )
    db.session.add(file_3_metadata)
    db.session.commit()

    file_3_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_3.FileId,
        PropertyName="file_type",
        Value="pdf",
    )
    db.session.add(file_3_metadata)
    db.session.commit()

    file_4 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=consignment_id,
        FileName="test_file4.doc",
        FileType="file",
        FileReference="test_file4.doc",
        FilePath="/data/test_file4.doc",
    )
    db.session.add(file_4)
    db.session.commit()

    file_4_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_4.FileId,
        PropertyName="file_name",
        Value="test_file4.doc",
    )
    db.session.add(file_4_metadata)
    db.session.commit()

    file_4_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_4.FileId,
        PropertyName="date_last_modified",
        Value="2023-12-15",
    )
    db.session.add(file_4_metadata)
    db.session.commit()

    file_4_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_4.FileId,
        PropertyName="closure_type",
        Value="closed",
    )
    db.session.add(file_4_metadata)
    db.session.commit()

    file_4_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_4.FileId,
        PropertyName="closure_start_date",
        Value=None,
    )
    db.session.add(file_4_metadata)
    db.session.commit()

    file_4_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_4.FileId,
        PropertyName="closure_expiry",
        Value="100",
    )
    db.session.add(file_4_metadata)
    db.session.commit()

    file_4_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_4.FileId,
        PropertyName="file_type",
        Value="doc",
    )
    db.session.add(file_4_metadata)
    db.session.commit()

    file_5 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=consignment_id,
        FileName="test_file5.pdf",
        FileType="file",
        FileReference="test_file5.pdf",
        FilePath="/data/test_file5.pdf",
    )
    db.session.add(file_5)
    db.session.commit()

    file_5_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_5.FileId,
        PropertyName="file_name",
        Value="test_file5.pdf",
    )
    db.session.add(file_5_metadata)
    db.session.commit()

    file_5_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_5.FileId,
        PropertyName="date_last_modified",
        Value="2023-12-15",
    )
    db.session.add(file_5_metadata)
    db.session.commit()

    file_5_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_5.FileId,
        PropertyName="closure_type",
        Value="open",
    )
    db.session.add(file_5_metadata)
    db.session.commit()

    file_5_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_5.FileId,
        PropertyName="closure_start_date",
        Value=None,
    )
    db.session.add(file_5_metadata)
    db.session.commit()

    file_5_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_5.FileId,
        PropertyName="closure_expiry",
        Value=None,
    )
    db.session.add(file_5_metadata)
    db.session.commit()

    file_5_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_5.FileId,
        PropertyName="file_type",
        Value="pdf",
    )
    db.session.add(file_5_metadata)
    db.session.commit()

    file_6 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=consignment_id,
        FileName="test_file6.txt",
        FileType="file",
        FileReference="test_file6.txt",
        FilePath="/data/test_file6.txt",
    )
    db.session.add(file_6)
    db.session.commit()

    file_6_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_6.FileId,
        PropertyName="file_name",
        Value="test_file6.txt",
    )
    db.session.add(file_6_metadata)
    db.session.commit()

    file_6_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_6.FileId,
        PropertyName="date_last_modified",
        Value="2023-12-15",
    )
    db.session.add(file_6_metadata)
    db.session.commit()

    file_6_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_6.FileId,
        PropertyName="closure_type",
        Value="closed",
    )
    db.session.add(file_6_metadata)
    db.session.commit()

    file_6_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_6.FileId,
        PropertyName="closure_start_date",
        Value="2023-11-05",
    )
    db.session.add(file_6_metadata)
    db.session.commit()

    file_6_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_6.FileId,
        PropertyName="closure_expiry",
        Value="70",
    )
    db.session.add(file_6_metadata)
    db.session.commit()

    file_6_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_6.FileId,
        PropertyName="file_type",
        Value="txt",
    )

    db.session.add(file_6_metadata)
    db.session.commit()

    file_7 = File(
        FileId=uuid.uuid4(),
        ConsignmentId=consignment_id,
        FileName="test_file7.png",
        FileType="file",
        FileReference="test_file7.png",
        FilePath="/data/test_file7.png",
    )
    db.session.add(file_7)
    db.session.commit()

    file_7_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_7.FileId,
        PropertyName="file_name",
        Value="test_file7.png",
    )
    db.session.add(file_7_metadata)
    db.session.commit()

    file_7_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_7.FileId,
        PropertyName="date_last_modified",
        Value="2023-12-15",
    )
    db.session.add(file_7_metadata)
    db.session.commit()

    file_7_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_7.FileId,
        PropertyName="closure_type",
        Value="closed",
    )
    db.session.add(file_7_metadata)
    db.session.commit()

    file_7_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_7.FileId,
        PropertyName="closure_start_date",
        Value="2023-11-05",
    )
    db.session.add(file_7_metadata)
    db.session.commit()

    file_7_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_7.FileId,
        PropertyName="closure_expiry",
        Value="10",
    )
    db.session.add(file_7_metadata)
    db.session.commit()

    file_7_metadata = FileMetadata(
        MetadataId=uuid.uuid4(),
        FileId=file_7.FileId,
        PropertyName="file_type",
        Value="png",
    )

    db.session.add(file_7_metadata)
    db.session.commit()

    return [
        file_2,
        file_3,
        file_4,
        file_5,
        file_6,
        file_7,
    ]
