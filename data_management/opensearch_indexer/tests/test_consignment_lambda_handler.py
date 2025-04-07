import json
from unittest.mock import patch
from uuid import uuid4

import boto3
import botocore
import pytest
from moto import mock_aws
from opensearch_indexer.index_consignment.lambda_function import lambda_handler
from opensearch_indexer.text_extraction import TextExtractionStatus
from requests_aws4auth import AWS4Auth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .conftest import Body, Consignment, File, FileMetadata, Series

# Original botocore _make_api_call function
orig = botocore.client.BaseClient._make_api_call


# Mocked botocore _make_api_call function
def mock_make_api_call(self, operation_name, kwarg):

    return orig(self, operation_name, kwarg)


@mock_aws
def test_lambda_handler_invokes_bulk_index_with_correct_file_data(
    monkeypatch, database
):
    """
    Test case for the lambda_handler function to ensure correct integration with the OpenSearch indexer.

    Given:
    - An S3 bucket containing files.
    - A secret stored in AWS Secrets Manager containing configuration details such as database connection,
      OpenSearch host URL, and an IAM role for OpenSearch access.

    When:
    - The lambda_handler function is invoked via an S3 event notification.

    Then:
    - The bulk_index_files_in_opensearch function is called with the correct parameters for each file:
      - Correct file metadata and content, including the extracted text, metadata properties,
        and associated consignment details.
      - The OpenSearch host URL.
      - An AWS4Auth object with credentials derived from the assumed IAM role.
      - The timeout for the OpenSearch bulk indexing operation.
    """
    # Set up the database engine and session using the URL
    engine = create_engine(database.url())
    from data_management.opensearch_indexer.tests.conftest import Base

    Base.metadata.create_all(engine)  # Create tables for the test

    # Create a session and set up test data
    Session = sessionmaker(bind=engine)
    session = Session()

    secret_name = "test_vars"  # pragma: allowlist secret
    db_secret_name = "test_db_vars"  # pragma: allowlist secret

    monkeypatch.setenv("SECRET_ID", secret_name)
    monkeypatch.setenv("DB_SECRET_ID", db_secret_name)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_access_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret_key")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "test_token")

    bucket_name = "test_bucket"

    opensearch_master_role_arn = (
        "arn:aws:iam::123456789012:role/test-opensearch-role"
    )
    secret_string = json.dumps(
        {
            "AWS_REGION": "eu-west-2",
            "RECORD_BUCKET_NAME": bucket_name,
            "OPEN_SEARCH_HOST": "https://test-opensearch.com",
            "OPEN_SEARCH_MASTER_ROLE_ARN": opensearch_master_role_arn,
            "OPEN_SEARCH_BULK_INDEX_TIMEOUT": 600,
        }
    )

    db_secret_string = json.dumps(
        {
            "username": "postgres",
            "password": "",
            "proxy": "127.0.0.1",
            "port": database.settings["port"],
            "dbname": "test",
        }
    )

    secretsmanager_client = boto3.client(
        "secretsmanager", region_name="eu-west-2"
    )

    secretsmanager_client.create_secret(
        Name=secret_name, SecretString=secret_string
    )
    secretsmanager_client.create_secret(
        Name=db_secret_name, SecretString=db_secret_string
    )

    s3_client = boto3.client("s3", region_name="us-east-1")

    body_id = uuid4()
    series_id = uuid4()
    consignment_id = uuid4()

    consignment_reference = "TDR-2024-ABCD"

    file_1_id = uuid4()
    file_2_id = uuid4()
    file_3_id = uuid4()

    session.add_all(
        [
            File(
                FileId=file_1_id,
                FileType="File",
                FileName="test-document.txt",
                FileReference="file-123",
                FilePath="/path/to/file",
                CiteableReference="cite-ref-123",
                ConsignmentId=consignment_id,
            ),
            File(
                FileId=file_2_id,
                FileType="File",
                FileName="test-document.txt",
                FileReference="file-123",
                FilePath="/path/to/file",
                CiteableReference="cite-ref-123",
                ConsignmentId=consignment_id,
            ),
            File(
                FileId=file_3_id,
                FileType="File",
                FileName="test-document.txt",
                FileReference="file-123",
                FilePath="/path/to/file",
                CiteableReference="cite-ref-123",
                ConsignmentId=consignment_id,
            ),
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
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_1_id,
                PropertyName="Key1",
                Value="Value1",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_1_id,
                PropertyName="Key2",
                Value="Value2",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_2_id,
                PropertyName="Key3",
                Value="Value3",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_2_id,
                PropertyName="Key4",
                Value="Value4",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_3_id,
                PropertyName="Key5",
                Value="Value5",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_3_id,
                PropertyName="Key6",
                Value="Value6",
            ),
        ]
    )
    session.commit()

    object_key_1 = f"{consignment_reference}/{file_1_id}"
    object_key_2 = f"{consignment_reference}/{file_2_id}"
    object_key_3 = f"{consignment_reference}/{file_3_id}"

    s3_client.create_bucket(Bucket=bucket_name)

    s3_client.put_object(
        Bucket=bucket_name, Key=object_key_1, Body=b"Test file content"
    )
    s3_client.put_object(Bucket=bucket_name, Key=object_key_2, Body=b"")
    s3_client.put_object(
        Bucket=bucket_name,
        Key=object_key_3,
        Body=b"File content but in file we do not support text extraction for",
    )

    sns_message = {
        "properties": {
            "messageType": "uk.gov.nationalarchives.da.messages.ayrmetadata.loaded",
            "function": "ddt-ayrmetadataload-process",
        },
        "parameters": {
            "reference": consignment_reference,
        },
    }

    event = {
        "Records": [
            {
                "Sns": {
                    "Message": json.dumps(sns_message),
                },
            }
        ]
    }

    with patch(
        "botocore.client.BaseClient._make_api_call", new=mock_make_api_call
    ):
        with patch(
            "opensearch_indexer.index_consignment.bulk_index_consignment.bulk_index_files_in_opensearch"
        ) as mock_bulk_index_files_in_opensearch:
            lambda_handler(event, None)

            args, _ = mock_bulk_index_files_in_opensearch.call_args

            assert args[0] == [
                {
                    "file_id": str(file_1_id),
                    "document": {
                        "file_id": str(file_1_id),
                        "file_name": "test-document.txt",
                        "file_reference": "file-123",
                        "file_path": "/path/to/file",
                        "citeable_reference": "cite-ref-123",
                        "series_id": str(series_id),
                        "series_name": "series-name",
                        "transferring_body": "body-name",
                        "transferring_body_id": str(body_id),
                        "transferring_body_description": "transferring body description",
                        "consignment_id": str(consignment_id),
                        "consignment_reference": "TDR-2024-ABCD",
                        "Key1": "Value1",
                        "Key2": "Value2",
                        "content": "Test file content",
                        "text_extraction_status": TextExtractionStatus.SUCCEEDED.value,
                    },
                },
                {
                    "document": {
                        "file_id": str(file_2_id),
                        "file_name": "test-document.txt",
                        "file_reference": "file-123",
                        "file_path": "/path/to/file",
                        "citeable_reference": "cite-ref-123",
                        "series_id": str(series_id),
                        "series_name": "series-name",
                        "transferring_body": "body-name",
                        "transferring_body_id": str(body_id),
                        "transferring_body_description": "transferring body description",
                        "consignment_id": str(consignment_id),
                        "consignment_reference": "TDR-2024-ABCD",
                        "Key3": "Value3",
                        "Key4": "Value4",
                        "content": "",
                        "text_extraction_status": TextExtractionStatus.SUCCEEDED.value,
                    },
                    "file_id": str(file_2_id),
                },
                {
                    "document": {
                        "file_id": str(file_3_id),
                        "file_name": "test-document.txt",
                        "file_reference": "file-123",
                        "file_path": "/path/to/file",
                        "citeable_reference": "cite-ref-123",
                        "series_id": str(series_id),
                        "series_name": "series-name",
                        "consignment_id": str(consignment_id),
                        "consignment_reference": "TDR-2024-ABCD",
                        "transferring_body": "body-name",
                        "transferring_body_id": str(body_id),
                        "transferring_body_description": "transferring body description",
                        "Key5": "Value5",
                        "Key6": "Value6",
                        "content": "File content but in file we do not support text extraction for",
                        "text_extraction_status": TextExtractionStatus.SUCCEEDED.value,
                    },
                    "file_id": str(file_3_id),
                },
            ]
            assert args[1] == "https://test-opensearch.com"

            aws_auth = args[2]
            assert isinstance(aws_auth, AWS4Auth)
            assert aws_auth.access_id == "test_access_key"
            assert (
                aws_auth.signing_key.secret_key
                == "test_secret_key"  # pragma: allowlist secret
            )
            assert aws_auth.region == "eu-west-2"
            assert aws_auth.service == "es"
            assert aws_auth.session_token == "test_token"

            assert args[3] == 600
            assert args[4] is None


@mock_aws
def test_lambda_handler_raises_exception_when_no_consignment_reference_in_sns_message():
    """
    Test case for the lambda_handler function to ensure correct integration with the OpenSearch indexer.

    Given:
    - An S3 bucket containing files.
    - A secret stored in AWS Secrets Manager containing configuration details such as database connection,
      OpenSearch host URL, and an IAM role for OpenSearch access.

    When:
    - The lambda_handler function is invoked via an S3 event notification.

    Then:
    - The bulk_index_files_in_opensearch function is called with the correct parameters for each file:
      - Correct file metadata and content, including the extracted text, metadata properties,
        and associated consignment details.
      - The OpenSearch host URL.
      - An AWS4Auth object with credentials derived from the assumed IAM role.
      - The timeout for the OpenSearch bulk indexing operation.
    """
    consignment_reference = None
    sns_message = {
        "properties": {
            "messageType": "uk.gov.nationalarchives.da.messages.ayrmetadata.loaded",
            "function": "ddt-ayrmetadataload-process",
        },
        "parameters": {
            "reference": consignment_reference,
        },
    }

    event = {
        "Records": [
            {
                "Sns": {
                    "Message": json.dumps(sns_message),
                },
            }
        ]
    }

    with pytest.raises(
        Exception,
        match="Missing reference in SNS Message required for indexing",
    ):
        lambda_handler(event, None)


@mock_aws
def test_lambda_handler_raises_exception_when_no_secret_id_env_var_set(
    monkeypatch,
):
    """
    Test case for the lambda_handler function to ensure correct integration with the OpenSearch indexer.

    Given:
    - An S3 bucket containing files.
    - A secret stored in AWS Secrets Manager containing configuration details such as database connection,
      OpenSearch host URL, and an IAM role for OpenSearch access.

    When:
    - The lambda_handler function is invoked via an S3 event notification.

    Then:
    - The bulk_index_files_in_opensearch function is called with the correct parameters for each file:
      - Correct file metadata and content, including the extracted text, metadata properties,
        and associated consignment details.
      - The OpenSearch host URL.
      - An AWS4Auth object with credentials derived from the assumed IAM role.
      - The timeout for the OpenSearch bulk indexing operation.
    """
    consignment_reference = "TDR-2024-ABCD"
    sns_message = {
        "properties": {
            "messageType": "uk.gov.nationalarchives.da.messages.ayrmetadata.loaded",
            "function": "ddt-ayrmetadataload-process",
        },
        "parameters": {
            "reference": consignment_reference,
        },
    }

    event = {
        "Records": [
            {
                "Sns": {
                    "Message": json.dumps(sns_message),
                },
            }
        ]
    }

    with pytest.raises(
        Exception,
        match="Missing SECRET_ID environment variable required for indexing",
    ):
        lambda_handler(event, None)
