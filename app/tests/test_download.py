import boto3
from moto import mock_s3

from app.tests.factories import (
    ConsignmentFactory,
    FileFactory,
    FileMetadataFactory,
)


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
def test_returns_record_page_for_user_with_access_to_files_transferring_body(
    app, client, mock_standard_user
):
    """
    Given a File in the database
    When a standard user with access to the file's transferring body makes a
        request to view the record page
    Then the response status code should be 200
    And the HTML content should contain specific elements
        related to the record
    """
    consignment = ConsignmentFactory(ConsignmentReference="TDR-123-TEST")
    file = FileFactory(
        file_consignments=consignment,
        FileName="test_file.txt",
        FilePath="data/content/folder_a/test_file.txt",
        FileType="file",
    )

    app.config["RECORD_BUCKET_NAME"] = "foo"
    s3 = boto3.resource("s3", region_name="us-east-1")

    s3.create_bucket(Bucket="foo")

    object = s3.Object(
        "foo", "TDR-123-TEST/data/content/folder_a/test_file.txt"
    )
    object.put(Body="foobar")

    mock_standard_user(client, [file.file_consignments.consignment_bodies.Name])

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

    response = client.get(f"/download/{file.FileId}")

    assert response.status_code == 200
