import uuid

import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyChoice, FuzzyText

from app.main.db.models import (
    Body,
    Consignment,
    FFIDMetadata,
    File,
    FileMetadata,
    Series,
    db,
)


class BodyFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Body
        sqlalchemy_session = db.session

    BodyId = factory.LazyFunction(uuid.uuid4)
    Name = FuzzyText(length=10)
    Description = FuzzyText(length=50)


class SeriesFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Series
        sqlalchemy_session = db.session

    SeriesId = factory.LazyFunction(uuid.uuid4)
    body = factory.SubFactory(BodyFactory)
    Name = FuzzyText(length=10)
    Description = FuzzyText(length=50)


class ConsignmentFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Consignment
        sqlalchemy_session = db.session

    ConsignmentId = factory.LazyFunction(uuid.uuid4)
    series = factory.SubFactory(SeriesFactory)
    ConsignmentReference = FuzzyText(length=10)
    ConsignmentType = FuzzyText(length=10)
    IncludeTopLevelFolder = factory.Faker("boolean")
    ContactName = FuzzyText(length=10)
    ContactEmail = factory.Faker("email")
    TransferStartDatetime = factory.Faker("date_time")
    TransferCompleteDatetime = factory.Faker("date_time")
    ExportDatetime = factory.Faker("date_time")
    CreatedDatetime = factory.Faker("date_time")


class FFIDMetadataFactory(SQLAlchemyModelFactory):
    class Meta:
        model = FFIDMetadata
        sqlalchemy_session = db.session

    FileId = factory.SelfAttribute("file.FileId")
    Extension = FuzzyChoice(["pdf", "txt", "docx", "jpg"])
    PUID = FuzzyText(length=8)
    FormatName = FuzzyChoice(
        ["Adobe PDF", "Plain Text", "Word Document", "JPEG Image"]
    )
    ExtensionMismatch = factory.Faker("boolean")
    FFID_Software = FuzzyChoice(["DROID", "Siegfried"])
    FFID_SoftwareVersion = FuzzyText(length=5)
    FFID_BinarySignatureFileVersion = FuzzyText(length=5)
    FFID_ContainerSignatureFileVersion = FuzzyText(length=5)
    file = factory.SubFactory("app.tests.factories.FileFactory")


class FileFactory(SQLAlchemyModelFactory):
    class Meta:
        model = File
        sqlalchemy_session = db.session

    FileId = factory.LazyFunction(uuid.uuid4)
    consignment = factory.SubFactory(ConsignmentFactory)
    FileReference = FuzzyText(length=10)
    FileType = FuzzyText(length=10)
    FileName = FuzzyText(length=10)
    FilePath = FuzzyText(length=50)
    CiteableReference = FuzzyText(length=10)
    Checksum = FuzzyText(length=10)
    CreatedDatetime = factory.Faker("date_time")
    ffid_metadata = factory.RelatedFactory(FFIDMetadataFactory, "file")


class FileMetadataFactory(SQLAlchemyModelFactory):
    class Meta:
        model = FileMetadata
        sqlalchemy_session = db.session

    MetadataId = factory.LazyFunction(uuid.uuid4)
    file = factory.SubFactory(FileFactory)
    PropertyName = FuzzyText(length=10)
    Value = FuzzyText(length=10)
    CreatedDatetime = factory.Faker("date_time")
