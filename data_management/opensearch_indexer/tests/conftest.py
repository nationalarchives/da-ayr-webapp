import tempfile

import pytest
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    create_engine,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from testing.postgresql import PostgresqlFactory

Base = declarative_base()


class Body(Base):
    __tablename__ = "Body"
    BodyId = Column(UUID(as_uuid=True), primary_key=True)
    Name = Column(Text)
    Description = Column(Text)


class Series(Base):
    __tablename__ = "Series"
    SeriesId = Column(UUID(as_uuid=True), primary_key=True)
    BodyId = Column(UUID(as_uuid=True), ForeignKey("Body.BodyId"))
    Name = Column(Text)
    Description = Column(Text)
    body = relationship("Body", foreign_keys="Series.BodyId")


class Consignment(Base):
    __tablename__ = "Consignment"
    ConsignmentId = Column(UUID(as_uuid=True), primary_key=True)
    SeriesId = Column(UUID(as_uuid=True), ForeignKey("Series.SeriesId"))
    BodyId = Column(UUID(as_uuid=True), ForeignKey("Body.BodyId"))
    ConsignmentReference = Column(Text)
    ConsignmentType = Column(String, nullable=False)
    IncludeTopLevelFolder = Column(Boolean)
    ContactName = Column(Text)
    ContactEmail = Column(Text)
    TransferStartDatetime = Column(DateTime)
    TransferCompleteDatetime = Column(DateTime)
    ExportDatetime = Column(DateTime)
    CreatedDatetime = Column(DateTime)
    series = relationship("Series", foreign_keys="Consignment.SeriesId")


class File(Base):
    __tablename__ = "File"
    FileId = Column(UUID(as_uuid=True), primary_key=True)
    ConsignmentId = Column(
        UUID(as_uuid=True), ForeignKey("Consignment.ConsignmentId")
    )
    FileReference = Column(Text, nullable=False)
    FileType = Column(Text, nullable=False)
    FileName = Column(Text, nullable=False)
    FilePath = Column(Text, nullable=False)
    CiteableReference = Column(Text)
    Checksum = Column(Text)
    CreatedDatetime = Column(DateTime)
    consignment = relationship("Consignment", foreign_keys="File.ConsignmentId")


class FileMetadata(Base):
    __tablename__ = "FileMetadata"
    MetadataId = Column(UUID(as_uuid=True), primary_key=True)
    FileId = Column(UUID(as_uuid=True), ForeignKey("File.FileId"))
    PropertyName = Column(Text, nullable=False)
    Value = Column(Text)
    CreatedDatetime = Column(DateTime)
    file = relationship("File", foreign_keys="FileMetadata.FileId")


@pytest.fixture()
def temp_db():
    temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db_file.close()
    database_url = f"sqlite:///{temp_db_file.name}"
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="session")
def database(request):
    # Launch new PostgreSQL server
    postgresql = PostgresqlFactory(cache_initialized_db=True)()
    yield postgresql

    # PostgreSQL server is terminated here
    @request.addfinalizer
    def drop_database():
        postgresql.stop()
