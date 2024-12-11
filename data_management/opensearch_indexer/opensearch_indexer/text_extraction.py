import logging
import tempfile
from typing import Dict

import textract

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SUPPORTED_TEXTRACT_FORMATS = [
    "csv",
    "doc",
    "docx",
    "eml",
    "epub",
    "gif",
    "jpg",
    "jpeg",
    "json",
    "html",
    "htm",
    "mp3",
    "msg",
    "odt",
    "ogg",
    "pdf",
    "png",
    "pptx",
    "ps",
    "rtf",
    "tiff",
    "tif",
    "txt",
    "wav",
    "xlsx",
    "xls",
]


def add_text_content(file: Dict, file_stream: bytes) -> Dict:
    file_type = file["file_name"].split(".")[-1].lower()

    if file_type not in SUPPORTED_TEXTRACT_FORMATS:
        logger.info(
            f"Text extraction skipped for unsupported file type: {file_type}"
        )
        file["content"] = ""
        file["text_extraction_status"] = "n/a"
    else:
        try:
            file["content"] = extract_text(file_stream, file_type)
            logger.info(f"Text extraction succeeded for file {file['file_id']}")
            file["text_extraction_status"] = "success"
        except Exception as e:
            logger.error(
                f"Text extraction failed for file {file['file_id']}: {e}"
            )
            file["content"] = ""
            file["text_extraction_status"] = "failed"

    return file


def extract_text(file_stream: bytes, file_extension: str) -> str:
    with tempfile.NamedTemporaryFile(
        suffix=f".{file_extension}", delete=True
    ) as temp:
        temp.write(file_stream)
        temp.flush()
        context = textract.process(temp.name)
    return context.decode("utf-8")
