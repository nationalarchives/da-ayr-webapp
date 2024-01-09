import boto3
from moto import mock_s3

from app.tests.conftest import mock_standard_user, mock_superuser
from app.tests.factories import (
    ConsignmentFactory,
    FileFactory,
    FileMetadataFactory,
)

BUCKET = "test-download"
CONSIGNMENT_REF = "TDR-123-TEST"
FILE_PATH = "data/content/folder_a/test_file.txt"
FILE_NAME = "test_file.txt"


def mock_record():
    """
    Creates a dummy record to be used by tests
    """
    consignment = ConsignmentFactory(ConsignmentReference=CONSIGNMENT_REF)
    file = FileFactory(
        file_consignments=consignment,
        FileName=FILE_NAME,
        FilePath=FILE_PATH,
        FileType="file",
    )

    metadata = {
        "date_last_modified": "2023-02-25T10:12:47",
        "closure_type": "Closed",
        "description": "Test description",
        "held_by": "Test holder",
        "legal_status": "Test legal status",
        "rights_copyright": "Test copyright",
        "language": "English",
    }

    [
        FileMetadataFactory(
            file_metadata=file,
            PropertyName=property_name,
            Value=value,
        )
        for property_name, value in metadata.items()
    ]

    return file


def test_invalid_id_raises_404(client):
    """
    Given a UUID, `invalid_file_id`, not corresponding to the id
        of a file in the database
    When a GET request is made to `/download/invalid_file_id`
    Then a 404 http response is returned
    """
    response = client.get("/download/some-id")

    assert response.status_code == 404


@mock_s3
def create_mock_s3_bucket_with_object():
    """
    Creates a dummy bucket to be used by tests
    """
    s3 = boto3.resource("s3", region_name="us-east-1")

    bucket = s3.create_bucket(Bucket=BUCKET)

    object = s3.Object(BUCKET, f"{CONSIGNMENT_REF}/{FILE_PATH}")
    object.put(Body="record")
    return bucket


@mock_s3
def test_downloads_record_successfully_for_user_with_access_to_files_transferring_body(
    app, client
):
    """
    Given a File in the database
    When a standard user with access to the file's transferring body makes a
        request to view the record page
    Then the response status code should be 200
    And the HTML content should contain specific elements
        related to the record
    """
    create_mock_s3_bucket_with_object()
    app.config["RECORD_BUCKET_NAME"] = BUCKET
    file = mock_record()
    mock_standard_user(client, file.file_consignments.consignment_bodies.Name)
    response = client.get(f"/download/{file.FileId}")

    assert response.status_code == 200
    assert (
        response.headers["Content-Disposition"]
        == f"attachment;filename={FILE_NAME}"
    )
    assert response.data == b"record"


@mock_s3
def test_raises_404_for_user_without_access_to_files_transferring_body(
    app, client
):
    """
    Given a File in the database
    When a standard user without access to the file's consignment body makes a
        request to download record
    Then the response status code should be 404
    """
    create_mock_s3_bucket_with_object()
    app.config["RECORD_BUCKET_NAME"] = BUCKET
    file = mock_record()
    mock_standard_user(client, "different_body")
    response = client.get(f"/download/{file.FileId}")

    assert response.status_code == 404


@mock_s3
def test_downloads_record_successfully_for_superuser(app, client):
    """
    Given a File in the database
    And a superuser
    When the superuser makes a request to download the record
    Then the response status code should be 200
    """
    create_mock_s3_bucket_with_object()
    app.config["RECORD_BUCKET_NAME"] = BUCKET
    file = mock_record()
    mock_superuser(client)
    response = client.get(f"/download/{file.FileId}")

    assert response.status_code == 200
