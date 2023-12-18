import uuid

import factory
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyText

from app.main.db.models import Body, Consignment, File, FileMetadata, Series, db


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
    body_series = factory.SubFactory(BodyFactory)
    Name = FuzzyText(length=10)
    Description = FuzzyText(length=50)


class ConsignmentFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Consignment
        sqlalchemy_session = db.session

    ConsignmentId = factory.LazyFunction(uuid.uuid4)
    consignment_series = factory.SubFactory(SeriesFactory)
    consignment_bodies = factory.SubFactory(BodyFactory)
    ConsignmentReference = FuzzyText(length=10)
    ConsignmentType = FuzzyText(length=10)
    IncludeTopLevelFolder = factory.Faker("boolean")
    ContactName = FuzzyText(length=10)
    ContactEmail = factory.Faker("email")
    TransferStartDatetime = factory.Faker("date_time")
    TransferCompleteDatetime = factory.Faker("date_time")
    ExportDatetime = factory.Faker("date_time")
    CreatedDatetime = factory.Faker("date_time")


class FileFactory(SQLAlchemyModelFactory):
    class Meta:
        model = File
        sqlalchemy_session = db.session

    FileId = factory.LazyFunction(uuid.uuid4)
    file_consignments = factory.SubFactory(ConsignmentFactory)
    FileReference = FuzzyText(length=10)
    FileType = FuzzyText(length=10)
    FileName = FuzzyText(length=10)
    FilePath = FuzzyText(length=50)
    ParentId = factory.Faker("uuid4")
    CiteableReference = FuzzyText(length=10)
    Checksum = FuzzyText(length=10)
    CreatedDatetime = factory.Faker("date_time")


class FileMetadataFactory(SQLAlchemyModelFactory):
    class Meta:
        model = FileMetadata
        sqlalchemy_session = db.session

    MetadataId = factory.LazyFunction(uuid.uuid4)
    file_metadata = factory.SubFactory(FileFactory)
    PropertyName = FuzzyText(length=10)
    Value = FuzzyText(length=10)
    CreatedDatetime = factory.Faker("date_time")
