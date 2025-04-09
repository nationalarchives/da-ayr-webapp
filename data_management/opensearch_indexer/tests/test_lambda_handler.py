import json
from unittest.mock import patch

import boto3
from moto import mock_aws
from opensearch_indexer.lambda_function import lambda_handler
from requests_aws4auth import AWS4Auth


@mock_aws
def test_lambda_handler_calls_index_file_content_and_metadata_in_opensearch(
    monkeypatch,
):
    """
    Given:
    - An S3 bucket containing a file.
    - A secret in AWS Secrets Manager with secret name specified in environment variable `SECRET_ID`
        including database and OpenSearch connection details including an IAM role.

    When:
    - The lambda_handler function is triggered by an S3 event.

    Then:
    - The index_file_content_and_metadata_in_opensearch function is called with the correct parameters:
      - The file name "test-file.txt".
      - The file content b"Test file content".
      - The database connection string.
      - The OpenSearch host URL.
      - An AWS4Auth object with the correct credentials determined by assuming the IAM role.
    """
    secret_name = "test_vars"  # pragma: allowlist secret
    db_secret_name = "test_db_vars"  # pragma: allowlist secret
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_access_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret_key")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "test_token")
    monkeypatch.setenv("SECRET_ID", secret_name)
    monkeypatch.setenv("DB_SECRET_ID", db_secret_name)

    opensearch_master_role_arn = (
        "arn:aws:iam::123456789012:role/test-opensearch-role"
    )

    bucket_name = "test_bucket"

    secret_string = json.dumps(
        {
            "OPEN_SEARCH_HOST": "https://test-opensearch.com",
            "OPEN_SEARCH_MASTER_ROLE_ARN": opensearch_master_role_arn,
            "AWS_REGION": "eu-west-2",
            "RECORD_BUCKET_NAME": bucket_name,
        }
    )

    db_secret_string = json.dumps(
        {
            "username": "testuser",
            "password": "testpassword",  # pragma: allowlist secret
            "proxy": "testhost",
            "port": 5432,
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
    object_key = "test-file.txt"
    s3_client.create_bucket(Bucket=bucket_name)
    s3_client.put_object(
        Bucket=bucket_name, Key=object_key, Body=b"Test file content"
    )

    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": bucket_name},
                    "object": {"key": object_key},
                }
            }
        ]
    }

    with patch(
        "opensearch_indexer.index_file_content_and_metadata_in_opensearch_from_aws"
        ".index_file_content_and_metadata_in_opensearch"
    ) as mock_index_file_content_and_metadata_in_opensearch:
        lambda_handler(event, None)

        args, _ = mock_index_file_content_and_metadata_in_opensearch.call_args

        assert args[0] == "test-file.txt"
        assert args[1] == b"Test file content"
        assert (
            args[2]
            == "postgresql+pg8000://testuser:testpassword@testhost:5432/testdb"  # pragma: allowlist secret
        )
        assert args[3] == "https://test-opensearch.com"

        aws_auth = args[4]
        assert isinstance(aws_auth, AWS4Auth)
        assert aws_auth.access_id == "test_access_key"
        assert (
            aws_auth.signing_key.secret_key
            == "test_secret_key"  # pragma: allowlist secret
        )
        assert aws_auth.region == "eu-west-2"
        assert aws_auth.service == "es"
        assert aws_auth.session_token == "test_token"
