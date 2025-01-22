import pytest

from app.main.util.download_utils import get_download_endpoint_filename
from app.tests.factories import FileFactory


@pytest.mark.parametrize(
    "file_name, citeable_reference, expected",
    [
        ("document.txt", "REF123", "REF123.txt"),
        ("document", "REF123", "document"),
        ("document.txt", None, "document.txt"),
        ("document", None, "document"),
    ],
)
def test_get_download_filename(app, file_name, citeable_reference, expected):
    file = FileFactory(FileName=file_name, CiteableReference=citeable_reference)
    result = get_download_endpoint_filename(file)
    assert result == expected
