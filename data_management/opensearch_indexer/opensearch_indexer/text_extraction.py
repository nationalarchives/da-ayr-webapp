import json
import logging
import os
import subprocess  # nosec
import tempfile
import threading
from enum import Enum
from typing import Dict

import boto3

# import requests
import textract

logger = logging.getLogger()
logger.setLevel(logging.INFO)
libreoffice_lock = threading.Lock()

TEXTRACT_FILE_PUIDS_FALLBACK_CONVERSION_MAP = {
    "fmt/59": "fmt/214",
    "fmt/61": "fmt/214",
    "fmt/39": "fmt/412",
    "fmt/40": "fmt/412",
    "x-fmt/44": "fmt/412",
    "x-fmt/45": "fmt/412",
}
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")


class TextExtractionStatus(Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


SUPPORTED_TEXTRACT_PUIDS = {
    "x-fmt/111": "txt",
    "x-fmt/18": "csv",
    "fmt/39": "doc",
    "fmt/40": "doc",
    "fmt/609": "doc",
    "fmt/412": "docx",
    "fmt/45": "rtf",
    "fmt/50": "rtf",
    "fmt/52": "rtf",
    "fmt/53": "rtf",
    "fmt/355": "rtf",
    "fmt/136": "odt",
    "fmt/290": "odt",
    "fmt/291": "odt",
    "fmt/14": "pdf",
    "fmt/15": "pdf",
    "fmt/16": "pdf",
    "fmt/17": "pdf",
    "fmt/18": "pdf",
    "fmt/19": "pdf",
    "fmt/20": "pdf",
    "fmt/276": "pdf",
    "fmt/95": "pdf",
    "fmt/354": "pdf",
    "fmt/476": "pdf",
    "fmt/477": "pdf",
    "fmt/478": "pdf",
    "fmt/479": "pdf",
    "fmt/480": "pdf",
    "fmt/481": "pdf",
    "fmt/488": "pdf",
    "fmt/489": "pdf",
    "fmt/490": "pdf",
    "fmt/491": "pdf",
    "fmt/492": "pdf",
    "fmt/493": "pdf",
    "fmt/144": "pdf",
    "fmt/145": "pdf",
    "fmt/146": "pdf",
    "fmt/147": "pdf",
    "fmt/148": "pdf",
    "fmt/157": "pdf",
    "fmt/158": "pdf",
    "x-fmt/394": "html",
    "fmt/278": "eml",
    "x-fmt/430": "msg",
    "fmt/3": "gif",
    "fmt/4": "gif",
    "fmt/42": "jpg",
    "fmt/43": "jpg",
    "fmt/44": "jpg",
    "fmt/391": "jpg",
    "fmt/11": "png",
    "fmt/12": "png",
    "fmt/13": "png",
    "fmt/353": "tif",
    "fmt/59": "xls",
    "fmt/61": "xls",
    "fmt/214": "xlsx",
    "fmt/215": "pptx",
}


def add_text_content(file: Dict, file_stream: bytes) -> Dict:

    file_puid = file["file_puid"] if file["file_puid"] else None
    file_id = file["file_id"]

    if file_puid not in SUPPORTED_TEXTRACT_PUIDS:
        logger.info(
            f"Text extraction skipped for file {file_id} due to unsupported file type: {file_puid}"
        )
        file["content"] = ""
        file["text_extraction_status"] = TextExtractionStatus.SKIPPED.value
    else:
        try:
            file["content"] = extract_text(file_stream, file_puid)
            logger.info(f"Text extraction succeeded for file {file_id}")
            file["text_extraction_status"] = (
                TextExtractionStatus.SUCCEEDED.value
            )
        except Exception as e:
            logger.error(f"Text extraction failed for file {file_id}: {e}")
            file["content"] = ""
            file["text_extraction_status"] = TextExtractionStatus.FAILED.value
    return file


def extract_text(file_stream: bytes, file_puid: str) -> str:
    with tempfile.NamedTemporaryFile(
        suffix=f".{SUPPORTED_TEXTRACT_PUIDS[file_puid]}", delete=True
    ) as temp:
        temp.write(file_stream)
        temp.flush()
        file_path = temp.name

        try:
            context = textract.process(file_path)
            return context.decode("utf-8")

        except Exception as e:
            logger.warning(f"Textract failed on {file_path}: {e}")

            if file_puid not in TEXTRACT_FILE_PUIDS_FALLBACK_CONVERSION_MAP:
                raise e

            output_file_type = SUPPORTED_TEXTRACT_PUIDS[
                TEXTRACT_FILE_PUIDS_FALLBACK_CONVERSION_MAP[file_puid]
            ]
            logger.info(
                f"Attempting to convert to {output_file_type} before trying textract again..."
            )

            try:
                converted_path = convert_file_with_libreoffice(
                    file_path, output_file_type
                )
                logger.info(f"Converted to: {converted_path}")
                text = textract.process(converted_path)
                return text.decode("utf-8")
            except Exception as convert_err:
                logger.error(f"LibreOffice fallback also failed: {convert_err}")
                raise Exception(
                    f"Textract failed on original file: {e}: LibreOffice fallback also failed: {convert_err}"
                )


def convert_file_with_libreoffice(
    input_path: str, output_file_type: str
) -> str:
    output_dir = tempfile.gettempdir()
    with libreoffice_lock:
        result = subprocess.run(  # nosec
            [
                "libreoffice",
                "--headless",
                "--convert-to",
                output_file_type,
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
    output_path = os.path.join(output_dir, base_name + f".{output_file_type}")

    if not os.path.exists(output_path):
        raise FileNotFoundError(
            f"Expected LibreOffice output not found: {output_path}"
        )

    return output_path


def get_slack_webhook():
    sm = boto3.client("secretsmanager")
    response = sm.get_secret_value(
        SecretId="slack-webhook"  # pragma: allowlist secret
    )
    secret_string = json.loads(response["SecretString"])
    slack_webhook = secret_string["slack-webhook"]
    return slack_webhook
