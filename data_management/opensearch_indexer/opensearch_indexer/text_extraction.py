import logging
import os
import subprocess
import tempfile
from enum import Enum
from typing import Dict

import textract

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TextExtractionStatus(Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


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
    file_id = file["file_id"]

    if file_type not in SUPPORTED_TEXTRACT_FORMATS:
        logger.info(
            f"Text extraction skipped for file {file_id} due to unsupported file type: {file_type}"
        )
        file["content"] = ""
        file["text_extraction_status"] = TextExtractionStatus.SKIPPED.value
    else:
        try:
            file["content"] = extract_text(file_stream, file_type)
            logger.info(f"Text extraction succeeded for file {file_id}")
            file["text_extraction_status"] = (
                TextExtractionStatus.SUCCEEDED.value
            )
        except Exception as e:
            logger.error(f"Text extraction failed for file {file_id}: {e}")
            file["content"] = ""
            file["text_extraction_status"] = TextExtractionStatus.FAILED.value

    return file


def extract_text(file_stream: bytes, file_extension: str) -> str:
    with tempfile.NamedTemporaryFile(
        suffix=f".{file_extension}", delete=True
    ) as temp:
        temp.write(file_stream)
        temp.flush()
        file_path = temp.name

        try:
            context = textract.process(file_path)
            return context.decode("utf-8")

        except Exception as e:
            logger.warning(f"Textract failed on {file_path}: {e}")

            if file_extension == "xls":
                try:
                    logger.info(
                        "Attempting to convert .xls to .xlsx via LibreOffice..."
                    )
                    converted_path = convert_xls_to_xlsx(file_path)
                    logger.info(f"Converted to: {converted_path}")
                    text = textract.process(converted_path)
                    return text.decode("utf-8")
                except Exception as convert_err:
                    logger.error(
                        f"LibreOffice conversion failed: {convert_err}"
                    )
                    raise convert_err
            else:
                raise e


def convert_xls_to_xlsx(input_path: str) -> str:
    output_dir = tempfile.gettempdir()
    result = subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "xlsx",
            "--outdir",
            output_dir,
            input_path,
        ],
        capture_output=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice conversion failed: {result.stderr.decode()}"
        )

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, base_name + ".xlsx")

    if not os.path.exists(output_path):
        raise FileNotFoundError(
            f"Expected LibreOffice output not found: {output_path}"
        )

    return output_path
