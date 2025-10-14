from unittest.mock import Mock, patch

import pytest
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


@pytest.fixture
def app_context():
    app = Flask(__name__)
    with app.app_context():
        yield


@patch("app.main.util.render_utils.pymupdf")
@patch("app.main.util.render_utils.Image")
@patch("app.main.util.render_utils.current_app")
def test_extract_pdf_pages_as_images_success(
    mock_current_app, mock_Image, mock_pymupdf, app_context
):
    mock_pdf_document = Mock()
    mock_pdf_document.page_count = 2
    mock_page = Mock()
    mock_pix = Mock()
    mock_pix.tobytes.return_value = b"fake_png_bytes"
    mock_page.get_pixmap.return_value = mock_pix
    mock_pdf_document.load_page.return_value = mock_page
    mock_pymupdf.open.return_value.__enter__.return_value = mock_pdf_document

    mock_image = Mock()
    mock_image.width = 800
    mock_image.height = 1000
    mock_image.size = (800, 1000)
    mock_image.format = "JPEG"
    mock_Image.open.return_value = mock_image
    mock_image.copy.return_value = mock_image
    mock_image.close.return_value = None

    pdf_bytes = b"%PDF-1.4 fake pdf bytes"
    result = extract_pdf_pages_as_images(pdf_bytes)

    assert isinstance(result, list)
    assert len(result) == 2
    for page in result:
        assert "page_number" in page
        assert "width" in page
        assert "height" in page
        assert "thumbnail_url" in page
        assert "page_image_url" in page
        assert page["width"] == 800
        assert page["height"] == 1000
        assert page["thumbnail_url"].startswith("data:image/jpeg;base64,")
        assert page["page_image_url"].startswith("data:image/jpeg;base64,")
        assert isinstance(page["thumbnail_base64_size"], int)
        assert isinstance(page["page_base64_size"], int)


@patch("app.main.util.render_utils.pymupdf")
@patch("app.main.util.render_utils.current_app")
def test_extract_pdf_pages_as_images_invalid_pdf(
    mock_current_app, mock_pymupdf, app_context
):
    class DummyFileDataError(Exception):
        pass

    mock_pymupdf.fitz.FileDataError = DummyFileDataError
    mock_pymupdf.open.side_effect = DummyFileDataError("bad pdf")
    mock_logger = Mock()
    mock_current_app.logger = mock_logger

    result = extract_pdf_pages_as_images(b"not a pdf")
    assert result == []
    mock_logger.error.assert_called()
