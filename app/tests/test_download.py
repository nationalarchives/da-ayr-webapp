import boto3
from moto import mock_aws

from app.tests.factories import FileFactory


def create_mock_s3_bucket_with_object(bucket_name, file):
    """
    Creates a dummy bucket to be used by tests
    """
    s3 = boto3.resource("s3", region_name="us-east-1")

    bucket = s3.create_bucket(Bucket=bucket_name)

    object = s3.Object(
        bucket_name, f"{file.consignment.ConsignmentReference}/{file.FileId}"
    )
    object.put(Body="record")
    return bucket


def test_invalid_id_raises_404(client):
    """
    Given a UUID, `invalid_file_id`, not corresponding to the id
        of a file in the database
    When a GET request is made to `/download/invalid_file_id`
    Then a 404 http response is returned
    """
    response = client.get("/download/some-id")

    assert response.status_code == 404


@mock_aws
def test_downloads_record_successfully_for_user_with_access_to_files_transferring_body(
    app, client, mock_standard_user
):
    """
    Given a File in the database with corresponding file in the s3 bucket
    When a standard user with access to the file's transferring body makes a
        request to download record
    Then the response status code should be 200
    And the file should contain the expected content
    And the the downloaded filename should be the File's CiteableReference
    """
    bucket_name = "test_bucket"
    file = FileFactory(
        FileType="file",
    )
    create_mock_s3_bucket_with_object(bucket_name, file)
    app.config["RECORD_BUCKET_NAME"] = bucket_name

    mock_standard_user(client, file.consignment.series.body.Name)
    response = client.get(f"/download/{file.FileId}")

    assert response.status_code == 200
    assert (
        response.headers["Content-Disposition"]
        == f"attachment;filename={file.CiteableReference}"
    )
    assert response.data == b"record"


@mock_aws
def test_downloads_record_successfully_for_user_with_access_to_files_transferring_body_without_citable_reference(
    app, client, mock_standard_user
):
    """
    Given a File in the database with corresponding file in the s3 bucket
        without a CiteableReference
    When a standard user with access to the file's transferring body makes a
        request to download record
    Then the response status code should be 200
    And the file should contain the expected content
    And the the downloaded filename should be File's FileName
    """
    bucket_name = "test_bucket"
    file = FileFactory(FileType="file", CiteableReference=None)
    create_mock_s3_bucket_with_object(bucket_name, file)
    app.config["RECORD_BUCKET_NAME"] = bucket_name

    mock_standard_user(client, file.consignment.series.body.Name)
    response = client.get(f"/download/{file.FileId}")

    assert response.status_code == 200
    assert (
        response.headers["Content-Disposition"]
        == f"attachment;filename={file.FileName}"
    )
    assert response.data == b"record"


@mock_aws
def test_raises_404_for_user_without_access_to_files_transferring_body(
    app, client, mock_standard_user
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

    mock_standard_user(client, "different_body")
    response = client.get(f"/download/{file.FileId}")

    assert response.status_code == 404


@mock_aws
def test_downloads_record_successfully_for_all_access_user(
    app, client, mock_all_access_user
):
    """
    Given a File in the database
    And an all_access_user
    When the all_access_user makes a request to download record
    Then the response status code should be 200
    """
    bucket_name = "test_bucket"
    file = FileFactory(
        FileType="file",
    )
    create_mock_s3_bucket_with_object(bucket_name, file)
    app.config["RECORD_BUCKET_NAME"] = bucket_name

    mock_all_access_user(client)
    response = client.get(f"/download/{file.FileId}")

    assert response.status_code == 200
