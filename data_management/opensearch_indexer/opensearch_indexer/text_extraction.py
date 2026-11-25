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

from format_policy import (
    SUPPORTED_TEXTRACT_PUIDS,
    TEXTRACT_FILE_PUIDS_CONVERT_TO_SUPPORTED_MAP,
    TEXTRACT_FILE_PUIDS_FALLBACK_CONVERSION_MAP,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
libreoffice_lock = threading.Lock()


SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")


class TextExtractionStatus(Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class EncryptedDocumentError(Exception):
    pass


def convert_file_and_extract_text_in_memory(
    file_stream: bytes, file_puid: str, file_id: str
) -> str:
    target_puid = TEXTRACT_FILE_PUIDS_CONVERT_TO_SUPPORTED_MAP[file_puid]
    target_ext = SUPPORTED_TEXTRACT_PUIDS[target_puid]
    logger.info(f"Converting {file_id} to {target_ext}")
    with tempfile.NamedTemporaryFile(delete=True) as src:
        src.write(file_stream)
        src.flush()

        converted_path = convert_file_with_libreoffice(src.name, target_ext)

        return extract_text(converted_path, target_puid, file_id)


def extract_text_in_memory(
    file_stream: bytes, file_puid: str, file_id: str
) -> str:
    ext = SUPPORTED_TEXTRACT_PUIDS[file_puid]
    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=True) as temp:
        temp.write(file_stream)
        temp.flush()
        return extract_text(temp.name, file_puid, file_id)


def add_text_content(file: Dict, file_stream: bytes) -> Dict:
    file_puid = file["file_puid"] if file["file_puid"] else None
    file_id = file["file_id"]

    try:
        if (
            file_puid not in SUPPORTED_TEXTRACT_PUIDS
            and file_puid not in TEXTRACT_FILE_PUIDS_CONVERT_TO_SUPPORTED_MAP
        ):
            logger.info(
                f"Text extraction skipped for file {file_id} due to unsupported file type: {file_puid}"
            )
            file["content"] = ""
            file["text_extraction_status"] = TextExtractionStatus.SKIPPED.value
            return file

        if file_puid in TEXTRACT_FILE_PUIDS_CONVERT_TO_SUPPORTED_MAP:
            file["content"] = convert_file_and_extract_text_in_memory(
                file_stream, file_puid, file_id
            )
        else:
            file["content"] = extract_text_in_memory(
                file_stream, file_puid, file_id
            )

        file["text_extraction_status"] = TextExtractionStatus.SUCCEEDED.value
        logger.info(f"Text extraction succeeded for file {file_id}")

    except EncryptedDocumentError as e:
        logger.warning(
            f"Text extraction skipped for encrypted file {file_id}: {e}"
        )
        file["content"] = ""
        file["text_extraction_status"] = TextExtractionStatus.SKIPPED.value

    except Exception as e:
        logger.error(f"Text extraction failed for file {file_id}: {e}")
        file["content"] = ""
        file["text_extraction_status"] = TextExtractionStatus.FAILED.value

    return file


def extract_text(file_path: str, file_puid: str, file_id: str) -> str:
    try:
        context = textract.process(file_path)
        return context.decode("utf-8")

    except Exception as e:
        encrypted = "encrypted" in str(e).lower()

        if file_puid not in TEXTRACT_FILE_PUIDS_FALLBACK_CONVERSION_MAP:
            if encrypted:
                raise EncryptedDocumentError(e)
            logger.warning(f"Textract failed on {file_id}: {e}")
            raise e

        output_file_type = SUPPORTED_TEXTRACT_PUIDS[
            TEXTRACT_FILE_PUIDS_FALLBACK_CONVERSION_MAP[file_puid]
        ]
        logger.info(
            f"Failed to textract, attempting to convert {file_id} to {output_file_type} before trying textract again.."
        )

        try:
            converted_path = convert_file_with_libreoffice(
                file_path, output_file_type
            )
            logger.info(f"Converted {file_id} to {output_file_type}")
            text = textract.process(converted_path)
            return text.decode("utf-8")
        except Exception as convert_err:
            logger.warning(f"Failed to convert {file_id}")
            if encrypted:
                raise EncryptedDocumentError(e) from e
            raise convert_err from e


def convert_file_with_libreoffice(
    input_path: str, output_file_type: str
) -> str:
    output_dir = tempfile.gettempdir()
    with libreoffice_lock:
        result = subprocess.run(  # nosec
            [
                "soffice",
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
