import json
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from app.main.util.render_utils import (
    create_presigned_url,
    extract_pdf_pages_as_images,
    generate_breadcrumb_values,
    generate_pdf_manifest,
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


@pytest.fixture
def app_context():
    app = Flask(__name__)
    with app.app_context():
        yield


def test_extract_pdf_pages_as_images_success():
    app = Flask(__name__)
    with app.app_context():
        with open("local_services/mds_data_generator/example_files/file.pdf", "rb") as f:
            pdf_bytes = f.read()

        result = extract_pdf_pages_as_images(pdf_bytes)

        assert isinstance(result, list)
        assert len(result) > 0  # Should have at least one page

        for idx, page in enumerate(result, start=1):
            assert page["page_number"] == idx
            assert isinstance(page["width"], int)
            assert isinstance(page["height"], int)
            assert page["thumbnail_url"].startswith("data:image/jpeg;base64,")
            assert page["page_image_url"].startswith("data:image/jpeg;base64,")
            assert isinstance(page["thumbnail_base64_size"], int)
            assert isinstance(page["page_base64_size"], int)


def test_extract_pdf_pages_as_images_invalid_pdf():
    app = Flask(__name__)
    with app.app_context():
        with pytest.raises(KeyError) as excinfo:
            extract_pdf_pages_as_images(b"not a pdf")
        assert "Error extracting PDF pages: Failed to open stream" in str(excinfo.value)



@pytest.fixture
def flask_app():
    app = Flask(__name__)
    with app.app_context():
        yield app


@patch("app.main.util.render_utils.get_pdf_pages_from_s3")
@patch("app.main.util.render_utils.current_app")
def test_generate_pdf_manifest_success(
    mock_current_app, mock_get_pdf_pages_from_s3, flask_app
):
    # Prepare mock page data
    page_data = [
        {
            "page_number": 1,
            "width": 800,
            "height": 1000,
            "thumbnail_url": "data:image/jpeg;base64,thumb1",
            "page_image_url": "data:image/jpeg;base64,page1",
            "thumbnail_base64_size": 123,
            "page_base64_size": 456,
        },
        {
            "page_number": 2,
            "width": 800,
            "height": 1000,
            "thumbnail_url": "data:image/jpeg;base64,thumb2",
            "page_image_url": "data:image/jpeg;base64,page2",
            "thumbnail_base64_size": 124,
            "page_base64_size": 457,
        },
    ]
    mock_get_pdf_pages_from_s3.return_value = (page_data, None)
    mock_logger = Mock()
    mock_current_app.logger = mock_logger

    with flask_app.app_context():
        resp = generate_pdf_manifest(
            "test.pdf", "http://manifest.url", file_obj=Mock()
        )
        assert resp.status_code == 200
        manifest = json.loads(resp.get_data(as_text=True))
        assert manifest["@type"] == "sc:Manifest"
        assert manifest["@id"] == "http://manifest.url"
        assert manifest["label"]["en"] == ["test.pdf"]
        assert "sequences" in manifest
        assert len(manifest["sequences"][0]["canvases"]) == 2
        for idx, canvas in enumerate(manifest["sequences"][0]["canvases"]):
            assert canvas["@type"] == "sc:Canvas"
            assert canvas["thumbnail"]["@id"] == page_data[idx]["thumbnail_url"]
            assert (
                canvas["images"][0]["resource"]["@id"]
                == page_data[idx]["page_image_url"]
            )


@patch("app.main.util.render_utils.get_pdf_pages_from_s3")
@patch("app.main.util.render_utils.current_app")
def test_generate_pdf_manifest_error_response(
    mock_current_app, mock_get_pdf_pages_from_s3, flask_app
):
    error_response = Mock()
    mock_get_pdf_pages_from_s3.return_value = (None, error_response)
    mock_logger = Mock()
    mock_current_app.logger = mock_logger

    with flask_app.app_context():
        resp = generate_pdf_manifest(
            "bad.pdf", "http://manifest.url", file_obj=Mock()
        )
        assert resp == error_response
