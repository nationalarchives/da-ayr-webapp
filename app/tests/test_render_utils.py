import base64
from unittest.mock import MagicMock, Mock, patch

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


@patch("app.main.util.render_utils.Image")
@patch("app.main.util.render_utils.pymupdf")
def test_extract_pdf_pages_as_images_success(mock_pymupdf, mock_Image):
    app = Flask(__name__)
    with app.app_context():
        with patch(
            "app.main.util.render_utils.current_app.logger"
        ) as mock_logger:
            # Mock data structure (like JSON)
            mock_data = {
                "pdf_document": {
                    "page_count": 2,
                    "pages": [
                        {"pixmap": {"tobytes": b"fakepngbytes"}},
                        {"pixmap": {"tobytes": b"fakepngbytes"}},
                    ],
                },
                "pymupdf": {"Matrix": "matrix"},
                "image": {
                    "width": 1000,
                    "height": 2000,
                    "save_bytes": b"jpegbytes",
                },
            }

            # Setup mocks using the structure above
            mock_pdf_document = MagicMock()
            mock_pdf_document.page_count = mock_data["pdf_document"][
                "page_count"
            ]

            mock_pages = []
            for page_info in mock_data["pdf_document"]["pages"]:
                mock_pixmap = MagicMock()
                mock_pixmap.tobytes.return_value = page_info["pixmap"][
                    "tobytes"
                ]
                mock_page = MagicMock()
                mock_page.get_pixmap.return_value = mock_pixmap
                mock_pages.append(mock_page)
            mock_pdf_document.load_page.side_effect = mock_pages

            mock_pymupdf.open.return_value.__enter__.return_value = (
                mock_pdf_document
            )
            mock_pymupdf.Matrix.return_value = mock_data["pymupdf"]["Matrix"]

            # Mock PIL Image
            mock_image = MagicMock()
            mock_image.width = mock_data["image"]["width"]
            mock_image.height = mock_data["image"]["height"]
            mock_image.copy.return_value = mock_image
            mock_image.save.side_effect = (
                lambda buf, format, quality: buf.write(
                    mock_data["image"]["save_bytes"]
                )
            )
            mock_image.thumbnail = MagicMock()
            mock_Image.open.return_value = mock_image

            # Call function
            result = extract_pdf_pages_as_images(b"dummy_pdf_bytes")

            # Assertions
            assert isinstance(result, list)
            assert len(result) == 2
            for i, page in enumerate(result):
                assert page["page_number"] == i + 1
                assert page["width"] == mock_data["image"]["width"]
                assert page["height"] == mock_data["image"]["height"]
                assert page["thumbnail_url"].startswith(
                    "data:image/jpeg;base64,"
                )
                assert page["page_image_url"].startswith(
                    "data:image/jpeg;base64,"
                )
                # Check base64 decodes
                base64.b64decode(page["thumbnail_url"].split(",")[1])
                base64.b64decode(page["page_image_url"].split(",")[1])

            assert mock_logger.debug.call_count == 2
