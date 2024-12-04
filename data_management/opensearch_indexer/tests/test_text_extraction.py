from pathlib import Path

from opensearch_indexer.text_extraction import extract_text


class TestExtractText:
    def test_txt_file(self):
        pdf_path = Path(__file__).parent / "multiline.txt"
        with open(pdf_path, "rb") as file:
            file_stream = file.read()
        file_type = "txt"
        assert (
            extract_text(file_stream, file_type)
            == "This is line 1\nThis is line 2\nThis is line 3\nThis is line 4, the final line.\n"
        )

    def test_docx_file(self):
        path = Path(__file__).parent / "multiline.docx"
        with open(path, "rb") as file:
            file_stream = file.read()
        file_type = "docx"

        assert extract_text(file_stream, file_type) == (
            "This is line 1\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t"
            "This is line 2\n\n\t\t\t\t\t\t\t\t\t\t\t\t\t"
            "This is line 3\n\n"
            "This is line 4, the final line."
        )

    def test_pdf_file(self):
        path = Path(__file__).parent / "multiline.pdf"
        with open(path, "rb") as file:
            file_stream = file.read()

        file_type = "pdf"

        assert (
            extract_text(file_stream, file_type)
            == "This is line 1\nThis is line 2\nThis is line 3\nThis is line 4, the ﬁnal line.\n\n\x0c"
        )
