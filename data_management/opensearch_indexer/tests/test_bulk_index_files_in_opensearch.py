import re
from unittest import mock
from uuid import uuid4

import boto3
import pytest
import sqlalchemy
import sqlalchemy.exc
from moto import mock_aws
from opensearch_indexer.index_consignment.bulk_index_consignment import (
    ConsignmentBulkIndexError,
    bulk_index_consignment,
    bulk_index_files_in_opensearch,
    construct_documents,
    fetch_files_in_consignment,
    format_bulk_indexing_error_message,
    validate_text_extraction,
)
from opensearchpy import RequestsHttpConnection
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from data_management.conftest import (
    Body,
    Consignment,
    FFIDMetadata,
    File,
    Series,
)


@mock.patch(
    "opensearch_indexer.index_consignment.bulk_index_consignment.OpenSearch"
)
def test_index_file_content_and_metadata_in_opensearch(
    mock_open_search, caplog
):
    """
    Test the `bulk_index_files_in_opensearch` function for successful indexing.

    Given:
    - A list of document dictionaries containing file IDs and content.
    - Mocked OpenSearch connection details.

    When:
    - `bulk_index_files_in_opensearch` is invoked.

    Then:
    - Documents are indexed in OpenSearch successfully.
    - OpenSearch client is initialized with the correct parameters.
    - Logs confirm the completion of the bulk indexing operation without errors.
    """
    open_search_host_url = "test_open_search_host_url"
    open_search_http_auth = mock.Mock()

    documents = [
        {
            "file_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
            "document": {
                "a": "foo1",
                "b": "bar1",
            },
        },
        {
            "file_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f",
            "document": {
                "c": "foo2",
                "d": "bar2",
            },
        },
        {
            "file_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270",
            "document": {
                "e": "foo3",
                "f": "bar3",
            },
        },
    ]

    mock_opensearch_response = {
        "took": 203,
        "errors": False,
        "items": [
            {
                "index": {
                    "_index": "documents",
                    "_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
                    "_version": 26,
                    "result": "updated",
                    "_shards": {"total": 2, "successful": 1, "failed": 0},
                    "_seq_no": 420,
                    "status": 200,
                }
            },
            {
                "index": {
                    "_index": "documents",
                    "_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f",
                    "_version": 26,
                    "result": "updated",
                    "_shards": {"total": 2, "successful": 1, "failed": 0},
                    "_seq_no": 421,
                    "_primary_term": 8,
                    "status": 200,
                }
            },
            {
                "index": {
                    "_index": "documents",
                    "_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270",
                    "_version": 26,
                    "result": "updated",
                    "_shards": {"total": 2, "successful": 1, "failed": 0},
                    "_seq_no": 422,
                    "_primary_term": 8,
                    "status": 200,
                }
            },
        ],
    }
    mock_open_search.return_value.bulk.return_value = mock_opensearch_response

    bulk_index_files_in_opensearch(
        documents,
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
    mock_open_search.return_value.bulk.assert_called_once_with(
        index="documents",
        body=(
            '{"index": {"_index": "documents", "_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f"}}\n'
            '{"a": "foo1", "b": "bar1"}\n'
            '{"index": {"_index": "documents", "_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f"}}\n'
            '{"c": "foo2", "d": "bar2"}\n'
            '{"index": {"_index": "documents", "_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270"}}\n'
            '{"e": "foo3", "f": "bar3"}\n'
        ),
        timeout=60,
    )

    assert [rec.message for rec in caplog.records] == [
        "Opensearch bulk indexing call completed with response",
        str(mock_opensearch_response),
        "Opensearch bulk indexing completed successfully",
    ]


@mock.patch(
    "opensearch_indexer.index_consignment.bulk_index_consignment.OpenSearch"
)
def test_index_file_content_and_metadata_in_opensearch_with_document_indexing_errors(
    mock_open_search, caplog
):
    """
    Test the `bulk_index_files_in_opensearch` function for error handling during indexing.

    Given:
    - A list of document dictionaries containing file IDs and content.
    - Mocked OpenSearch connection details.

    When:
    - `bulk_index_files_in_opensearch` is invoked, and OpenSearch returns errors for some documents.

    Then:
    - An exception is raised for the failed documents.
    - OpenSearch client is initialized with the correct parameters.
    - Logs indicate the presence of errors in the indexing operation.
    """
    open_search_host_url = "test_open_search_host_url"
    open_search_http_auth = mock.Mock()

    documents = [
        {
            "file_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
            "document": {
                "a": "foo1",
                "b": "bar1",
            },
        },
        {
            "file_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f",
            "document": {
                "c": "foo2",
                "d": "bar2",
            },
        },
        {
            "file_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270",
            "document": {
                "e": "foo3",
                "f": "bar3",
            },
        },
    ]

    mock_opensearch_response = {
        "took": 203,
        "errors": True,
        "items": [
            {
                "index": {
                    "_index": "documents",
                    "_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
                    "_version": 26,
                    "result": "updated",
                    "_shards": {"total": 2, "successful": 1, "failed": 1},
                    "_seq_no": 420,
                    "status": 200,
                }
            },
            {
                "index": {
                    "_index": "documents",
                    "_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f",
                    "_version": 26,
                    "result": "updated",
                    "_shards": {"total": 2, "successful": 1, "failed": 0},
                    "_seq_no": 421,
                    "_primary_term": 8,
                    "status": 200,
                }
            },
            {
                "index": {
                    "_index": "documents",
                    "_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270",
                    "error": {
                        "type": "document_missing_exception",
                        "reason": "[_doc][tt0816711]: document missing",
                        "index": "documents",
                        "shard": "0",
                        "index_uuid": "yhizhusbSWmP0G7OJnmcLg",
                    },
                    "status": 404,
                }
            },
        ],
    }

    mock_open_search.return_value.bulk.return_value = mock_opensearch_response

    with pytest.raises(
        Exception,
        match=re.escape(
            (
                "Opensearch bulk indexing errors:\n"
                "Error for document ID 47526ba9-88e5-4cc8-8bc1-d682a10fa270: "
                "{'type': 'document_missing_exception', 'reason': '[_doc][tt0816711]: document missing', "
                "'index': 'documents', 'shard': '0', 'index_uuid': 'yhizhusbSWmP0G7OJnmcLg'}"
            )
        ),
    ):
        bulk_index_files_in_opensearch(
            documents,
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
    mock_open_search.return_value.bulk.assert_called_once_with(
        index="documents",
        body=(
            '{"index": {"_index": "documents", "_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f"}}\n'
            '{"a": "foo1", "b": "bar1"}\n'
            '{"index": {"_index": "documents", "_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f"}}\n'
            '{"c": "foo2", "d": "bar2"}\n'
            '{"index": {"_index": "documents", "_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270"}}\n'
            '{"e": "foo3", "f": "bar3"}\n'
        ),
        timeout=60,
    )

    assert [rec.message for rec in caplog.records] == [
        "Opensearch bulk indexing call completed with response",
        str(mock_opensearch_response),
        "Opensearch bulk indexing completed with errors",
    ]


@mock.patch(
    "opensearch_indexer.index_consignment.bulk_index_consignment.OpenSearch"
)
def test_index_file_content_and_metadata_in_opensearch_with_bulk_api_exception(
    mock_open_search, caplog
):
    """
    Test the `bulk_index_files_in_opensearch` function for handling exceptions raised by the OpenSearch bulk API.

    Given:
    - A list of document dictionaries containing file IDs and content.
    - Mocked OpenSearch connection details.

    When:
    - `bulk_index_files_in_opensearch` is invoked, and the OpenSearch bulk API raises an exception.

    Then:
    - The exception is propagated as expected.
    - Logs capture the error details.
    """
    open_search_host_url = "test_open_search_host_url"
    open_search_http_auth = mock.Mock()

    documents = [
        {
            "file_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
            "document": {"a": "foo1", "b": "bar1"},
        }
    ]

    mock_open_search.return_value.bulk.side_effect = Exception(
        "Simulated OpenSearch bulk API failure"
    )

    with pytest.raises(
        Exception, match="Simulated OpenSearch bulk API failure"
    ):
        bulk_index_files_in_opensearch(
            documents,
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
    mock_open_search.return_value.bulk.assert_called_once_with(
        index="documents",
        body=(
            '{"index": {"_index": "documents", "_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f"}}\n'
            '{"a": "foo1", "b": "bar1"}\n'
        ),
        timeout=60,
    )

    assert [rec.message for rec in caplog.records] == [
        "Opensearch bulk indexing call failed: Simulated OpenSearch bulk API failure"
    ]


def test_validate_text_extraction_with_all_success_or_skipped_status():
    """
    Given a list of documents where all have either 'SUCCEEDED' or 'SKIPPED' text extraction status,
    When validate_text_extraction is called,
    Then it should return None, indicating no errors.
    """
    documents = [
        {
            "file_id": "1",
            "document": {
                "file_id": "1",
                "content": "Test file content",
                "text_extraction_status": "SUCCEEDED",
            },
        },
        {
            "file_id": "2",
            "document": {
                "file_id": "2",
                "text_extraction_status": "SKIPPED",
            },
        },
    ]
    assert validate_text_extraction(documents) is None


def test_validate_text_extraction_with_failed_status_returns_error_message():
    """
    Given a list of documents where some have 'FAILED' text extraction status,
    When validate_text_extraction is called,
    Then it should return an error message listing the file IDs with failed status.
    """
    documents = [
        {
            "file_id": "1",
            "document": {
                "file_id": "1",
                "content": "Test file content",
                "text_extraction_status": "SUCCEEDED",
            },
        },
        {
            "file_id": "2",
            "document": {
                "file_id": "2",
                "text_extraction_status": "FAILED",
            },
        },
        {
            "file_id": "3",
            "document": {
                "file_id": "3",
                "text_extraction_status": "FAILED",
            },
        },
    ]
    expected_error_message = (
        "Text extraction failed on the following documents:\n2\n3"
    )
    assert validate_text_extraction(documents) == expected_error_message


def test_format_bulk_indexing_error_message_with_both_errors():
    """
    Given a consignment reference, a text extraction error message, and a bulk index error message,
    When format_bulk_indexing_error_message is called,
    Then it should return a detailed error message including both errors.
    """
    consignment_reference = "test-consignment"
    text_extraction_error = "Failed to extract text for documents: 1, 2"
    bulk_index_error = "Bulk index timeout occurred for documents: 3, 4"

    result = format_bulk_indexing_error_message(
        consignment_reference, text_extraction_error, bulk_index_error
    )

    expected_message = (
        "Bulk indexing failed for consignment test-consignment:"
        "\nText Extraction Errors:\nFailed to extract text for documents: 1, 2"
        "\nBulk Index Errors:\nBulk index timeout occurred for documents: 3, 4"
    )
    assert result == expected_message


def test_format_bulk_indexing_error_message_with_only_text_extraction_error():
    """
    Given a consignment reference and a text extraction error message,
    When format_bulk_indexing_error_message is called with no bulk index error,
    Then it should return a detailed error message including only the text extraction error.
    """
    consignment_reference = "test-consignment"
    text_extraction_error = "Failed to extract text for documents: 1, 2"
    bulk_index_error = None

    result = format_bulk_indexing_error_message(
        consignment_reference, text_extraction_error, bulk_index_error
    )

    expected_message = (
        "Bulk indexing failed for consignment test-consignment:"
        "\nText Extraction Errors:\nFailed to extract text for documents: 1, 2"
    )
    assert result == expected_message


def test_format_bulk_indexing_error_message_with_only_bulk_index_error():
    """
    Given a consignment reference and a bulk index error message,
    When format_bulk_indexing_error_message is called with no text extraction error,
    Then it should return a detailed error message including only the bulk index error.
    """
    consignment_reference = "test-consignment"
    text_extraction_error = None
    bulk_index_error = "Bulk index timeout occurred for documents: 3, 4"

    result = format_bulk_indexing_error_message(
        consignment_reference, text_extraction_error, bulk_index_error
    )

    expected_message = (
        "Bulk indexing failed for consignment test-consignment:"
        "\nBulk Index Errors:\nBulk index timeout occurred for documents: 3, 4"
    )
    assert result == expected_message


def test_format_bulk_indexing_error_message_with_no_errors():
    """
    Given a consignment reference with no text extraction error or bulk index error,
    When format_bulk_indexing_error_message is called,
    Then it should return an error message with no specific error details.
    """
    consignment_reference = "test-consignment"
    text_extraction_error = None
    bulk_index_error = None

    result = format_bulk_indexing_error_message(
        consignment_reference, text_extraction_error, bulk_index_error
    )

    expected_message = "Bulk indexing failed for consignment test-consignment:"
    assert result == expected_message


def test_fetch_files_in_consignment_invalid_column_with_logging(
    database, caplog
):
    """
    Given a databse without correctly setup tables
    When fetch_files_in_consignment is called with a consignment reference and the database url,
    Then it should log an error indicating the failure to retrieve file metadata.
    """
    database_url = database.url()
    # Create the engine and session
    engine = create_engine(database_url)

    # Minimal setup, omitting necessary schema parts
    with engine.connect() as connection:
        connection.execute(
            text(
                """
            CREATE TABLE Consignment (
                ConsignmentId SERIAL PRIMARY KEY,
                ConsignmentReference TEXT
            );
        """
            )
        )

    consignment_reference = "reference-123"
    with pytest.raises(sqlalchemy.exc.ProgrammingError):
        fetch_files_in_consignment(consignment_reference, database_url)

    assert (
        "Failed to retrieve file metadata for consignment reference: reference-123"
        in caplog.text
    )


@mock_aws
def test_construct_documents_s3_error_logging(caplog):
    """
    Given a list of file metadata and a bucket name,
    When the function attempts to retrieve files from S3 and encounters an error (e.g., file not found),
    Then it should log the error and raise an exception.
    """
    files = [
        {
            "file_id": 1,
            "consignment_reference": "consignment-123",
        },
    ]
    bucket_name = "test-bucket"

    # Create the mock bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=bucket_name)

    # No files are uploaded to the bucket, so retrieving any file should fail.
    # The file we are trying to access does not exist in the mocked bucket.

    with pytest.raises(Exception):
        with caplog.at_level("ERROR"):
            construct_documents(files, bucket_name)

    # Assert that the correct error message is logged
    assert (
        "Failed to obtain file consignment-123/1: An error occurred (NoSuchKey) when calling "
        "the GetObject operation: The specified key does not exist."
    ) in caplog.text


# Test for bulk_index_consignment error handling when bulk index operation fails
@mock.patch(
    "opensearch_indexer.index_consignment.bulk_index_consignment.bulk_index_files_in_opensearch"
)
@mock_aws
def test_bulk_index_consignment_error_handling(
    mock_bulk_index_files_in_opensearch, caplog, database
):
    """
    Given a consignment reference and files,
    When the bulk indexing fails,
    Then it should log the error and raise a ConsignmentBulkIndexError.
    """

    # Prepare input data
    database_url = database.url()
    consignment_reference = "consignment-123"
    bucket_name = "test-bucket"
    open_search_host_url = "https://opensearch.example.com"
    open_search_http_auth = ("username", "password")
    open_search_bulk_index_timeout = 30

    # Insert mock data into PostgreSQL
    engine = create_engine(database_url)
    from data_management.conftest import Base

    Base.metadata.create_all(engine)  # Create tables for the test
    Session = sessionmaker(bind=engine)
    session = Session()

    body_id = uuid4()
    series_id = uuid4()
    consignment_id = uuid4()

    consignment_reference = "TDR-2024-XYWZ"

    file_id = uuid4()

    session.add_all(
        [
            Consignment(
                ConsignmentId=consignment_id,
                ConsignmentType="foo",
                ConsignmentReference=consignment_reference,
                SeriesId=series_id,
            ),
            Series(SeriesId=series_id, Name="series-name", BodyId=body_id),
            Body(
                BodyId=body_id,
                Name="body-name",
                Description="transferring body description",
            ),
            File(
                FileId=file_id,
                FileType="File",
                FileName="test-document.txt",
                FileReference="file-123",
                FilePath="/path/to/file",
                CiteableReference="cite-ref-123",
                ConsignmentId=consignment_id,
            ),
            FFIDMetadata(
                FileId=file_id,
                Extension="txt",
                FormatName="Plain Text",
                ExtensionMismatch=False,
                FFID_Software="Siegfried",
                FFID_SoftwareVersion="1.0",
                FFID_BinarySignatureFileVersion="1",
                FFID_ContainerSignatureFileVersion="1",
                PUID="x-fmt/111",
            ),
        ]
    )
    # Insert mock consignment and file data
    session.commit()

    # Upload a file to S3 (mocked by moto)
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=bucket_name)
    s3.put_object(
        Bucket=bucket_name,
        Key=f"{consignment_reference}/{file_id}",
        Body=b"Test file content",
    )

    # Mock OpenSearch bulk indexing to raise an error
    mock_bulk_index_files_in_opensearch.side_effect = Exception(
        "Some opensearch bulk indexing error string."
    )

    # Run the function and capture logs
    with pytest.raises(
        ConsignmentBulkIndexError,
        match=(
            "Bulk indexing failed for consignment TDR-2024-XYWZ:\n"
            "Bulk Index Errors:\nSome opensearch bulk indexing error string."
        ),
    ):
        with caplog.at_level("ERROR"):
            bulk_index_consignment(
                consignment_reference,
                bucket_name,
                database_url,
                open_search_host_url,
                open_search_http_auth,
                open_search_bulk_index_timeout,
            )
