import base64
from unittest.mock import Mock, patch

from flask import Flask

from app.main.util.render_utils import (
    create_presigned_url,
    extract_pdf_pages_as_images,
    generate_breadcrumb_values,
    get_download_filename,
    get_file_extension,
)


def test_get_file_extension_with_ffid_extension():
    mock_file = Mock()
    mock_file.ffid_metadata.Extension = "PDF"
    mock_file.FileName = "ignored.txt"

    ext = get_file_extension(mock_file)
    assert ext == "pdf"


def test_get_file_extension_with_ffid_extension_none_uses_filename():
    mock_file = Mock()
    mock_file.ffid_metadata.Extension = None
    mock_file.FileName = "example.DOC"

    ext = get_file_extension(mock_file)
    assert ext == "doc"


def test_generate_breadcrumb_values():
    mock_file = Mock()
    mock_file.consignment.consignment_id = "consignment_id"
    mock_file.consignment.series.series_id = "series_id"
    mock_file.consignment.series.body.BodyId = "body_id"
    mock_file.consignment.series.Name = "Series Name"
    mock_file.consignment.ConsignmentId = "consignment_id"
    mock_file.consignment.ConsignmentReference = "consignment_reference"
    mock_file.FileName = "file_name.pdf"

    result = generate_breadcrumb_values(mock_file)

    assert result[0]["transferring_body_id"] == "body_id"
    assert result[3]["series"] == "Series Name"
    assert result[4]["consignment_id"] == "consignment_id"
    assert result[5]["consignment_reference"] == "consignment_reference"
    assert result[6]["file_name"] == "file_name.pdf"


def test_get_download_filename():
    mock_file = Mock()
    mock_file.CiteableReference = "CITEREF-123"
    mock_file.FileName = "example.txt"
    assert get_download_filename(mock_file) == "CITEREF-123.txt"

    mock_file.FileName = "no_extension"
    assert get_download_filename(mock_file) is None


@patch("boto3.client")
def test_create_presigned_url(mock_boto_client):
    app = Flask(__name__)

    app.config["RECORD_BUCKET_NAME"] = "test_record_download_bucket"

    mock_file = Mock()
    mock_file.FileName = "test.pdf"
    mock_file.FileId = "file_id"
    mock_file.consignment.ConsignmentReference = "consignment_reference"

    mock_s3_client = mock_boto_client.return_value
    mock_s3_client.generate_presigned_url.return_value = "http://presigned.url"

    with app.app_context():
        url = create_presigned_url(mock_file)

    mock_s3_client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={
            "Bucket": "test_record_download_bucket",
            "Key": "consignment_reference/file_id",
        },
        ExpiresIn=10,
    )
    assert url == "http://presigned.url"


def test_extract_pdf_pages_as_images_with_actual_pdf_file():
    app = Flask(__name__)
    pdf_path = "local_services/mds_data_generator/example_files/file.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    with app.app_context():
        result = extract_pdf_pages_as_images(pdf_bytes)
    assert isinstance(result, list)
    assert len(result) > 0
    for i, page in enumerate(result):
        assert page["page_number"] == i + 1
        assert page["width"] > 1200
        assert page["height"] > 1700
        assert page["thumbnail_url"].startswith("data:image/jpeg;base64,")
        assert page["page_image_url"].startswith("data:image/jpeg;base64,")
        # Check base64 decodes
        base64.b64decode(page["thumbnail_url"].split(",")[1])
        base64.b64decode(page["page_image_url"].split(",")[1])
