from unittest.mock import patch

import boto3
from botocore.exceptions import ClientError
from flask.testing import FlaskClient
from moto import mock_aws

from app.tests.factories import FileFactory


def create_mock_s3_bucket_with_object(bucket_name, file):
    """
    Creates a dummy bucket to be used by tests
    """
    s3 = boto3.resource("s3", region_name="us-east-1")

    bucket = s3.create_bucket(Bucket=bucket_name)

    file_object = s3.Object(
        bucket_name, f"{file.consignment.ConsignmentReference}/{file.FileId}"
    )
    file_object.put(Body="record")
    return bucket


class TestDownload:
    @property
    def route_url(self):
        return "/download"

    def test_invalid_id_raises_404(self, client: FlaskClient):
        """
        Given a UUID, not corresponding to the id of a file in the database
        When a GET request is made to download route
        Then a 404 http response is returned
        """
        response = client.get(f"{self.route_url}/some-id")

        assert response.status_code == 404

    @mock_aws
    def test_download_existing_file_with_presigned_url(
        self, app, client, mock_standard_user
    ):
        """
        Given an existing file in the database with corresponding file in the S3 bucket
        When a standard user with access to the file's transferring body makes a request to download the record
        Then the response status code should be 302 and they're redirected to the presigned url
        """
        bucket_name = "test_bucket"
        file = FileFactory(FileType="file", FileName="testfile.doc")

        create_mock_s3_bucket_with_object(bucket_name, file)
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        mock_standard_user(
            client, file.consignment.series.body.Name, can_download=True
        )
        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 302
        assert (
            "https://s3.eu-west-2.amazonaws.com/test_bucket"
            in response.headers["Location"]
        )

    @mock_aws
    def test_download_non_existing_file_with_presigned_url(
        self, app, client, mock_standard_user
    ):
        """
        Given a non existing file in the database with corresponding file in the S3 bucket
        When a standard user with access to the file's transferring body makes a request to download the record
        Then the response status code should be 404
        """
        bucket_name = "test_bucket"
        file = FileFactory(FileType="file", FileName="testfile.doc")

        s3 = boto3.resource("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=bucket_name)

        app.config["RECORD_BUCKET_NAME"] = bucket_name

        mock_standard_user(
            client, file.consignment.series.body.Name, can_download=True
        )
        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 404

    @mock_aws
    @patch("app.main.routes.boto3.client")
    def test_presigned_url_generation_failure(
        self, mock_boto3_client, app, client, mock_standard_user, caplog
    ):
        """
        Given a file in the database with a corresponding S3 bucket entry
        But presigned URL generation fails
        When a standard user with access to the file's transferring body makes a request to download the record
        Then the response status code should be 500
        """

        bucket_name = "test_bucket"
        file = FileFactory(
            FileType="file", FileName="testfile.doc", CiteableReference=None
        )

        create_mock_s3_bucket_with_object(bucket_name, file)

        app.config["RECORD_BUCKET_NAME"] = bucket_name

        mock_s3_client = mock_boto3_client.return_value
        mock_s3_client.generate_presigned_url.side_effect = Exception(
            "Simulated error in presigned URL generation"
        )

        mock_standard_user(
            client, file.consignment.series.body.Name, can_download=True
        )

        response = client.get(
            f"/download/{file.FileId}", follow_redirects=False
        )

        assert response.status_code == 500
        assert "Failed to generate presigned URL" in caplog.text

    @mock_aws
    @patch("app.main.routes.boto3.client")
    def test_s3_fetch_failure(
        self, mock_boto3_client, app, client, mock_standard_user, caplog
    ):
        """
        Given a file in the database
        But the corresponding S3 object does not exist or S3 fetch fails
        When a standard user with access to the file's transferring body makes a request to download the record
        Then the response status code should be 500, and an appropriate error message should be logged
        """

        bucket_name = "test_bucket"
        file = FileFactory(
            FileType="file", FileName="testfile.doc", CiteableReference=None
        )

        create_mock_s3_bucket_with_object(bucket_name, file)

        app.config["RECORD_BUCKET_NAME"] = bucket_name

        error_response = {
            "Error": {
                "Code": "500",
                "Message": "Simulated error fetching object from S3 bucket",
            }
        }

        mock_s3_client = mock_boto3_client.return_value
        mock_s3_client.head_object.side_effect = ClientError(
            error_response, "HeadObject"
        )

        mock_standard_user(
            client, file.consignment.series.body.Name, can_download=True
        )

        response = client.get(
            f"/download/{file.FileId}", follow_redirects=False
        )

        assert response.status_code == 500
        assert "Failed to fetch object from S3 bucket" in caplog.text

    @mock_aws
    def test_raises_404_for_standard_user_without_access_to_files_transferring_body(
        self, app, client, mock_standard_user
    ):
        """
        Given a File in the database
        When a standard user without access to the file's consignment body makes a
            request to download record
        Then the response status code should be 404
        """
        bucket_name = "test_bucket"
        file = FileFactory(
            FileType="file",
        )
        create_mock_s3_bucket_with_object(bucket_name, file)
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        mock_standard_user(client, "different_body", can_download=True)
        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 404

    @mock_aws
    def test_download_record_for_all_access_user_valid_response(
        self, app, client, mock_all_access_user
    ):
        """
        Given a File in the database
        And an all_access_user
        When the all_access_user makes a request to download record
        Then the response status code should be 302 (redirect to presigned url)
        """
        bucket_name = "test_bucket"
        file = FileFactory(
            FileType="file",
        )
        create_mock_s3_bucket_with_object(bucket_name, file)
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        mock_all_access_user(client, can_download=True)
        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 302

    @mock_aws
    def test_download_record_for_all_access_user_forbidden_response(
        self, app, client, mock_all_access_user
    ):
        """
        Given a File in the database
        And an all_access_user
        When the all_access_user with no download permissions makes a request to download record
        Then the response status code should be 401
        """
        bucket_name = "test_bucket"
        file = FileFactory(
            FileType="file",
        )
        create_mock_s3_bucket_with_object(bucket_name, file)
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        mock_all_access_user(client)
        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 403

    @mock_aws
    def test_download_record_for_standard_user_forbidden_response(
        self, app, client, mock_standard_user
    ):
        """
        Given a File in the database
        And an all_access_user
        When the standard_user with no download permissions makes a request to download record
        Then the response status code should be 401
        """
        bucket_name = "test_bucket"
        file = FileFactory(
            FileType="file",
        )
        create_mock_s3_bucket_with_object(bucket_name, file)
        app.config["RECORD_BUCKET_NAME"] = bucket_name

        mock_standard_user(client, file.consignment.series.body.Name)
        response = client.get(f"{self.route_url}/{file.FileId}")

        assert response.status_code == 403
