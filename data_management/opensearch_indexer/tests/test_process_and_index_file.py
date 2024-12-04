import tempfile
from unittest import mock
from uuid import uuid4

import pytest
from opensearch_indexer.index_file_content_and_metadata_in_opensearch import (
    index_file_content_and_metadata_in_opensearch,
)
from opensearchpy import RequestsHttpConnection
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
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

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


@pytest.fixture
def temp_db():
    temp_db_file = tempfile.NamedTemporaryFile(suffix=".db")
    database_url = f"sqlite:///{temp_db_file.name}"
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    yield engine


@mock.patch(
    "opensearch_indexer.index_file_content_and_metadata_in_opensearch.OpenSearch"
)
def test_index_file_content_and_metadata_in_opensearch(
    mock_open_search, temp_db
):
    """
    Given:
    - A file stream representing a text file.
    - An SQLite database mimicking the file data.
    - OpenSearch connection details.

    When:
    - The index_file_content_and_metadata_in_opensearch function is invoked.

    Then:
    - The relevant file data is fetched from the database.
    - The file's text content is extracted using real extract_text.
    - The file is indexed in OpenSearch with the extracted text.
    """
    Session = sessionmaker(bind=temp_db)
    session = Session()

    body_id = uuid4()
    series_id = uuid4()
    consignment_id = uuid4()
    file_id = uuid4()
    session.add_all(
        [
            File(
                FileId=file_id,
                FileType="bar",
                FileName="test-document.txt",
                FileReference="file-123",
                FilePath="/path/to/file",
                CiteableReference="cite-ref-123",
                ConsignmentId=consignment_id,
            ),
            Consignment(
                ConsignmentId=consignment_id,
                ConsignmentType="foo",
                ConsignmentReference="consignment-123",
                SeriesId=series_id,
            ),
            Series(SeriesId=series_id, Name="series-name", BodyId=body_id),
            Body(
                BodyId=body_id,
                Name="body-name",
                Description="transferring body description",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_id,
                PropertyName="Key1",
                Value="Value1",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_id,
                PropertyName="Key2",
                Value="Value2",
            ),
        ]
    )
    session.commit()
    file_id_hex = file_id.hex
    file_stream = b"Text stream"
    open_search_host_url = "test_open_search_host_url"
    open_search_http_auth = mock.Mock()

    index_file_content_and_metadata_in_opensearch(
        file_id_hex,
        file_stream,
        temp_db.url,
        open_search_host_url,
        open_search_http_auth,
    )

    mock_open_search.assert_called_once_with(
        open_search_host_url,
        http_auth=open_search_http_auth,
        use_ssl=True,
        verify_certs=True,
        ca_certs=None,
        connection_class=RequestsHttpConnection,
    )
    mock_open_search.return_value.index.assert_called_once_with(
        index="documents",
        id=file_id_hex,
        body={
            "file_id": file_id_hex,
            "file_name": "test-document.txt",
            "file_reference": "file-123",
            "file_path": "/path/to/file",
            "citeable_reference": "cite-ref-123",
            "series_id": series_id.hex,
            "series_name": "series-name",
            "transferring_body": "body-name",
            "transferring_body_id": body_id.hex,
            "transferring_body_description": "transferring body description",
            "consignment_id": consignment_id.hex,
            "consignment_reference": "consignment-123",
            "Key1": "Value1",
            "Key2": "Value2",
            "content": "Text stream",
            "text_extraction_status": "success",
        },
    )
