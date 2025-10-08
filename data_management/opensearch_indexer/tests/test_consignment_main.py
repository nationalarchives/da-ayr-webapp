import json
from unittest.mock import patch
from uuid import uuid4

import boto3
import pytest
from moto import mock_aws
from opensearch_indexer.index_consignment.main import consingment_indexer
from requests_aws4auth import AWS4Auth
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data_management.conftest import (
    Body,
    Consignment,
    FFIDMetadata,
    File,
    FileMetadata,
    Series,
)


# Mock ENVIRONMENT for slack alerts
@pytest.fixture(autouse=True)
def patch_environment():
    with patch("opensearch_indexer.text_extraction.ENVIRONMENT", "test-env"):
        yield


@mock_aws
def test_main_invokes_bulk_index_with_correct_file_data(monkeypatch, database):
    engine = create_engine(database.url())
    from data_management.conftest import Base

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    secret_name = "test_vars"  # pragma: allowlist secret
    db_secret_name = "test_db_vars"  # pragma: allowlist secret

    monkeypatch.setenv("SECRET_ID", secret_name)
    monkeypatch.setenv("DB_SECRET_ID", db_secret_name)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_access_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret_key")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "test_token")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-2")

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
            "username": "testuser",
            "password": "testPass123",  # pragma: allowlist secret
            "proxy": "postgres",
            "port": database.settings["port"],
            "dbname": "testdb",
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

    file_ids = [uuid4() for _ in range(4)]

    session.add_all(
        [
            *[
                File(
                    FileId=file_ids[i],
                    FileType="File",
                    FileName="test-document.txt",
                    FileReference="file-123",
                    FilePath="/path/to/file",
                    CiteableReference="cite-ref-123",
                    ConsignmentId=consignment_id,
                )
                for i in range(4)
            ],
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
                FileId=file_ids[0],
                PropertyName="Key1",
                Value="Value1",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_ids[0],
                PropertyName="Key2",
                Value="Value2",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_ids[1],
                PropertyName="Key3",
                Value="Value3",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_ids[1],
                PropertyName="Key4",
                Value="Value4",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_ids[2],
                PropertyName="Key5",
                Value="Value5",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_ids[3],
                PropertyName="Key6",
                Value="Value6",
            ),
            FFIDMetadata(
                FileId=file_ids[0],
                Extension="txt",
                PUID="fmt/115",
                FormatName="Plain Text",
            ),
            FFIDMetadata(
                FileId=file_ids[1],
                Extension="txt",
                PUID="fmt/115",
                FormatName="Plain Text",
            ),
            FFIDMetadata(
                FileId=file_ids[2],
                Extension="bin",
                PUID="x-fmt/111",
                FormatName="Binary",
            ),
            FFIDMetadata(
                FileId=file_ids[3],
                Extension="txt",
                PUID="fmt/115",
                FormatName="Plain Text",
            ),
        ]
    )
    session.commit()

    s3_client.create_bucket(Bucket=bucket_name)
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"{consignment_reference}/{file_ids[0]}",
        Body=b"Test file content",
    )
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"{consignment_reference}/{file_ids[1]}",
        Body=b"",
    )
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"{consignment_reference}/{file_ids[2]}",
        Body=b"Unsupported content",
    )
    s3_client.put_object(
        Bucket=bucket_name,
        Key=f"{consignment_reference}/{file_ids[3]}",
        Body=b"Test file content",
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
    monkeypatch.setenv("SNS_MESSAGE", json.dumps(sns_message))

    with patch(
        "opensearch_indexer.index_consignment.bulk_index_consignment.bulk_index_files_in_opensearch"
    ) as mock_bulk_index:
        consingment_indexer()

        args, _ = mock_bulk_index.call_args
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

        doc = next(
            d["document"] for d in args[0] if d["file_id"] == str(file_ids[0])
        )
        assert doc["file_name"] == "test-document.txt"
        assert doc["file_extension"] == "txt"
        assert doc["Key1"] == "Value1"
        assert doc["content"] == "Test file content"


@mock_aws
def test_main_raises_exception_when_no_reference(monkeypatch):
    monkeypatch.setenv(
        "SNS_MESSAGE",
        json.dumps(
            {
                "properties": {
                    "messageType": "uk.gov.nationalarchives.da.messages.ayrmetadata.loaded",
                    "function": "ddt-ayrmetadataload-process",
                },
                "parameters": {},
            }
        ),
    )
    monkeypatch.setenv("SECRET_ID", "any")
    monkeypatch.setenv("DB_SECRET_ID", "any")

    with pytest.raises(
        Exception,
        match="Missing reference in SNS Message required for indexing",
    ):
        consingment_indexer()


@mock_aws
def test_main_raises_exception_when_no_sns_message(monkeypatch):
    monkeypatch.delenv("SNS_MESSAGE", raising=False)
    monkeypatch.setenv("SECRET_ID", "any")
    monkeypatch.setenv("DB_SECRET_ID", "any")

    with pytest.raises(
        Exception, match="SNS_MESSAGE environment variable not found"
    ):
        consingment_indexer()


@mock_aws
def test_main_raises_exception_when_missing_env_vars(monkeypatch):
    monkeypatch.setenv(
        "SNS_MESSAGE",
        json.dumps({"parameters": {"reference": "TDR-1234-TEST"}}),
    )
    monkeypatch.delenv("SECRET_ID", raising=False)
    monkeypatch.delenv("DB_SECRET_ID", raising=False)

    with pytest.raises(
        Exception,
        match="Missing required environment variables: SECRET_ID or DB_SECRET_ID",
    ):
        consingment_indexer()
