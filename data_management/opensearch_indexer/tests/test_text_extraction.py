from pathlib import Path
from unittest.mock import patch

import pytest
from opensearch_indexer.text_extraction import (
    TextExtractionStatus,
    add_text_content,
    extract_text,
)


class TestExtractText:
    @pytest.mark.parametrize(
        "file_name, file_type, expected_output",
        [
            (
                "multiline.txt",
                "txt",
                "This is line 1\nThis is line 2\nThis is line 3\nThis is line 4, the final line.\n",
            ),
            (
                "multiline.docx",
                "docx",
                "This is line 1\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t"
                "This is line 2\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t"
                "This is line 3\n\n"
                "This is line 4, the final line.",
            ),
            (
                "multiline.doc",
                "doc",
                "\nExpected content\nSecond line\nThird line\n",
            ),
            (
                "multiline.pdf",
                "pdf",
                "This is line 1\nThis is line 2\nThis is line 3\nThis is line 4, the final line.\n\n\x0c",
            ),
            (
                "multiline.odt",
                "odt",
                "This is line 1\nThis is line 2\nThis is line 3\nThis is line 4, the final odt line.\n",
            ),
            (
                "multiline.html",
                "html",
                "\nThis is line 1\n            This is line 2\n            This is line 3, the final html line.\n",
            ),
            (
                "multiline.htm",
                "html",
                "\nThis is line 1\n            This is line 2\n            This is line 3, the final htm line.\n",
            ),
            (
                "multiline.epub",
                "epub",
                "multiline\nThis is line 1\nThis is line 2\nThis is line 3\nThis is line 4, the final epub line.\n",
            ),
            (
                "multiline.json",
                "json",
                "value1 value2 value3 ",
            ),
            (
                "multiline.eml",
                "eml",
                "This is line 1\nThis is line 2\nThis is line 3\nThis is line 4, the final eml line.\n",
            ),
            (
                "multiline.msg",
                "msg",
                "\n\nThis is line 1\r\nThis is line 2\r\nThis is line 3\r\nThis is line 4, the final msg line.\r\n",
            ),
            (
                "multiline.csv",
                "csv",
                "\tHeader1\tHeader2\tHeader3\t\t\t\n\tValue1\tValue2\tValue3\t\t\t",
            ),
            (
                "multiline.xlsx",
                "xlsx",
                "\nHeader1 Header2 Header3\nValue1 Value2 Value3\n",
            ),
        ],
    )
    def test_extract_text(self, file_name, file_type, expected_output):
        path = Path(__file__).parent / f"test_files/{file_name}"
        with open(path, "rb") as file:
            file_stream = file.read()

        assert extract_text(file_stream, file_type) == expected_output


# Mock the extract_text function to simulate text extraction behavior
@pytest.fixture
def mock_extract_text():
    with patch("opensearch_indexer.text_extraction.extract_text") as mock:
        yield mock


# Test for successfully extracting text from a supported file type
def test_add_text_content_success(mock_extract_text, caplog):
    """
    Given a supported file type and a valid file stream,
    When text extraction succeeds,
    Then the content is updated and the status is set to SUCCEEDED.
    """

    # Given
    file = {
        "file_id": 1,
        "file_name": "example.pdf",
        "content": "",
        "text_extraction_status": "",
    }
    file_stream = b"Some file content"
    mock_extract_text.return_value = "Extracted text"

    # When
    result = add_text_content(file, file_stream)

    # Then
    assert result["content"] == "Extracted text"
    assert (
        result["text_extraction_status"] == TextExtractionStatus.SUCCEEDED.value
    )
    mock_extract_text.assert_called_once_with(file_stream, "pdf")

    assert "Text extraction succeeded for file 1" in caplog.text


# Test for unsupported file type
def test_add_text_content_unsupported_format(caplog):
    """
    Given an unsupported file type,
    When text extraction is skipped,
    Then the content is set to an empty string and the status is set to SKIPPED.
    """

    # Given
    file = {
        "file_id": 2,
        "file_name": "example.exe",  # Unsupported file type
        "content": "",
        "text_extraction_status": "",
    }
    file_stream = b"Some content that won't be extracted"

    # When
    result = add_text_content(file, file_stream)

    # Then
    assert result["content"] == ""
    assert (
        result["text_extraction_status"] == TextExtractionStatus.SKIPPED.value
    )

    assert (
        "Text extraction skipped for file 2 due to unsupported file type: exe"
        in caplog.text
    )


# Test for text extraction failure
def test_add_text_content_failure(mock_extract_text, caplog):
    """
    Given a supported file type and a failing text extraction,
    When text extraction fails due to an error,
    Then the content is set to an empty string and the status is set to FAILED.
    """

    # Given
    file = {
        "file_id": 3,
        "file_name": "example.txt",  # Supported file type
        "content": "",
        "text_extraction_status": "",
    }
    file_stream = b"Some content"

    # Simulate a failure in text extraction
    mock_extract_text.side_effect = Exception("Text extraction failed")

    # When
    with caplog.at_level("ERROR"):
        result = add_text_content(file, file_stream)

    # Then
    assert result["content"] == ""
    assert result["text_extraction_status"] == TextExtractionStatus.FAILED.value
    mock_extract_text.assert_called_once_with(file_stream, "txt")

    assert (
        "Text extraction failed for file 3: Text extraction failed"
        in caplog.text
    )


# Test for file type without extension
def test_add_text_content_no_extension():
    """
    Given a file without an extension,
    When trying to extract text,
    Then the file is skipped and the status is set to SKIPPED.
    """

    # Given
    file = {
        "file_id": 4,
        "file_name": "example",  # No file extension
        "content": "",
        "text_extraction_status": "",
    }
    file_stream = b"Some content"

    # When
    result = add_text_content(file, file_stream)

    # Then
    assert result["content"] == ""
    assert (
        result["text_extraction_status"] == TextExtractionStatus.SKIPPED.value
    )


def test_extract_text_fallback_conversion_success():
    """
    Given textract fails on the original file but succeeds on converted file,
    Then fallback conversion should succeed and return the converted content.
    """
    file_bytes = b"dummy file content"
    converted_path = "/tmp/converted.xlsx"

    with patch(
        "opensearch_indexer.text_extraction.textract.process"
    ) as mock_textract, patch(
        "opensearch_indexer.text_extraction.convert_file_with_libreoffice"
    ) as mock_convert:
        # Given
        mock_textract.side_effect = [
            Exception("textract failed"),
            b"converted content",
        ]
        mock_convert.return_value = converted_path

        # When
        result = extract_text(file_bytes, "xls")

        # Then
        assert result == "converted content"
        assert mock_textract.call_count == 2
        mock_convert.assert_called_once()


def test_extract_text_fallback_conversion_failure():
    """
    Given textract fails on both original and converted files,
    Then extract_text should raise the second exception.
    """
    file_bytes = b"dummy file content"
    converted_path = "/tmp/converted.xlsx"

    with patch(
        "opensearch_indexer.text_extraction.textract.process"
    ) as mock_textract, patch(
        "opensearch_indexer.text_extraction.convert_file_with_libreoffice"
    ) as mock_convert:

        # Given
        mock_textract.side_effect = [
            Exception("initial textract failed"),
            Exception("converted textract failed"),
        ]
        mock_convert.return_value = converted_path

        # Then
        with pytest.raises(Exception, match="converted textract failed"):
            extract_text(file_bytes, "xls")

        assert mock_textract.call_count == 2
        mock_convert.assert_called_once()
