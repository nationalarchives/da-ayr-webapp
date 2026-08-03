import logging
from unittest.mock import Mock, patch

import pymupdf
import pytest
from flask import Flask

from app.main.util.render_utils import (
    _open_pdf,
    create_presigned_url,
    generate_breadcrumb_values,
    get_download_filename,
    get_file_extension,
    get_file_puid,
    search_within_pdf,
)

RENDER_UTILS_LOGGER = "app.main.util.render_utils"


def _make_pdf_with_text(text: str) -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 100), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_get_file_extension_with_ffid_extension():
    mock_file = Mock()
    mock_file.ffid_metadata.Extension = "PDF"
    mock_file.FileName = "ignored.txt"

    ext = get_file_extension(mock_file)
    assert ext == "pdf"


def test_get_file_puid_with_ffid_puid():
    mock_file = Mock()
    mock_file.ffid_metadata.PUID = "fmt/40"
    puid = get_file_puid(mock_file)
    assert puid == "fmt/40"


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


MINIMAL_VALID_PDF_TWO_PAGES = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >>\nendobj\n"
    b"4 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] >>\nendobj\n"
    b"xref\n0 5\n0000000000 65535 f \n0000000010 00000 n \n0000000061 00000 n \n0000000120 00000 n \n0000000179 00000 n \n"  # noqa
    b"trailer\n<< /Root 1 0 R /Size 5 >>\nstartxref\n238\n%%EOF"
)


@patch("app.main.util.render_utils.get_pdf_from_s3")
def test_search_within_pdf_returns_annotations_for_matches(
    mock_get_pdf_from_s3,
):
    mock_get_pdf_from_s3.return_value = _make_pdf_with_text("hello world")

    app = Flask(__name__)
    with app.app_context():
        response = search_within_pdf(
            query="hello",
            search_url="http://localhost/record/abc/search",
            manifest_url="http://localhost/record/abc/manifest",
            bucket="test-bucket",
            key="test/key",
        )

    data = response.get_json()
    assert data["@type"] == "sc:AnnotationList"
    assert data["within"]["total"] >= 1
    assert len(data["resources"]) >= 1
    assert len(data["hits"]) >= 1

    resource = data["resources"][0]
    assert resource["@type"] == "oa:Annotation"
    assert "#xywh=" in resource["on"]
    assert resource["resource"]["chars"] == "hello"

    hit = data["hits"][0]
    assert hit["@type"] == "search:Hit"
    assert hit["match"] == "hello"


def _mupdf_messages(records):
    return [r.message for r in records if r.message.startswith("MuPDF:")]


def test_open_pdf_logs_recoverable_messages_at_debug(caplog):
    """A repairable PDF opens fine and its MuPDF messages are logged at DEBUG."""
    with caplog.at_level(logging.DEBUG, logger=RENDER_UTILS_LOGGER):
        with _open_pdf(MINIMAL_VALID_PDF_TWO_PAGES) as doc:
            assert doc.page_count == 2

    messages = _mupdf_messages(caplog.records)
    assert messages, "expected MuPDF repair messages to be logged"
    assert "repairing PDF document" in messages[0]
    assert all(
        r.levelno == logging.DEBUG
        for r in caplog.records
        if r.message.startswith("MuPDF:")
    )


def test_open_pdf_clean_pdf_logs_nothing(caplog):
    """A well formed PDF produces no MuPDF messages, so nothing is logged."""
    clean_pdf = _make_pdf_with_text("hello")
    with caplog.at_level(logging.DEBUG, logger=RENDER_UTILS_LOGGER):
        with _open_pdf(clean_pdf) as doc:
            assert doc.page_count == 1

    assert _mupdf_messages(caplog.records) == []


def test_open_pdf_empty_bytes_raises_file_data_error():
    """Genuine open failures propagate as pymupdf.FileDataError."""
    with pytest.raises(pymupdf.FileDataError):
        with _open_pdf(b""):
            pass


def test_open_pdf_garbage_raises_file_data_error():
    with pytest.raises(pymupdf.FileDataError):
        with _open_pdf(b"this is not a pdf"):
            pass


def test_open_pdf_propagates_body_exceptions_untouched():
    """Errors raised inside the with body must keep their type and message."""
    with pytest.raises(KeyError, match="unrelated"):
        with _open_pdf(MINIMAL_VALID_PDF_TWO_PAGES):
            raise KeyError("unrelated")


def test_open_pdf_restores_mupdf_display_flags():
    """The context manager re-enables MuPDF stderr display on exit."""
    pymupdf.TOOLS.mupdf_display_errors(True)
    pymupdf.TOOLS.mupdf_display_warnings(True)

    with _open_pdf(MINIMAL_VALID_PDF_TWO_PAGES):
        assert pymupdf.TOOLS.mupdf_display_errors() is False
        assert pymupdf.TOOLS.mupdf_display_warnings() is False

    assert pymupdf.TOOLS.mupdf_display_errors() is True
    assert pymupdf.TOOLS.mupdf_display_warnings() is True


def test_open_pdf_restores_mupdf_display_flags_on_failure():
    """Flags are restored even when opening fails."""
    pymupdf.TOOLS.mupdf_display_errors(True)
    pymupdf.TOOLS.mupdf_display_warnings(True)

    with pytest.raises(pymupdf.FileDataError):
        with _open_pdf(b""):
            pass

    assert pymupdf.TOOLS.mupdf_display_errors() is True
    assert pymupdf.TOOLS.mupdf_display_warnings() is True
