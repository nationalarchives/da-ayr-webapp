from pathlib import Path

import pytest
from opensearch_indexer.text_extraction import extract_text


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
                "multiline.pdf",
                "pdf",
                "This is line 1\nThis is line 2\nThis is line 3\nThis is line 4, the ﬁnal line.\n\n\x0c",
            ),
            (
                "multiline.odt",
                "odt",
                "This is line 1\nThis is line 2\nThis is line 3\nThis is line 4, the final odt line.\n",
            ),
            (
                "multiline.html",
                "html",
                "\nThis is line 1\n    This is line 2\n    This is line 3, the final html line.\n",
            ),
            (
                "multiline.htm",
                "html",
                "\nThis is line 1\n        This is line 2\n        This is line 3, the final htm line.\n",
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
