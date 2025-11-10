import json
import logging
import os
import subprocess  # nosec
import tempfile
from enum import Enum
from typing import Dict

import boto3

# import requests
import textract

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TEXTRACT_FILE_FORMAT_FALLBACK_CONVERSION_MAP = {"xls": "xlsx", "doc": "docx"}
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")
ENVIRONMENT = os.getenv("ENVIRONMENT")


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

    if file["file_extension"] is None:
        file_type = file["file_name"].split(".")[-1].lower()
    else:
        file_type = file["file_extension"].lower()
    file_id = file["file_id"]

    if file_type not in SUPPORTED_TEXTRACT_FORMATS:
        logger.info(
            f"Text extraction skipped for file {file_id} due to unsupported file type: {file_type}"
        )
        file["content"] = ""
        file["text_extraction_status"] = TextExtractionStatus.SKIPPED.value
        # send_slack_alert(
        #     f"Text extraction *SKIPPED* for file `{file_id}`\n"
        #     f"*Environment:* `{ENVIRONMENT.upper()}`\n"
        #     f"*Reason:* Unsupported file type - `{file_type}`"
        # )
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
            # send_slack_alert(
            #     f"Text extraction *FAILED* for file `{file_id}`\n"
            #     f"*Environment:* `{ENVIRONMENT.upper()}`\n"
            #     f"*Reason:* `{e}`"
            # )
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

            if (
                file_extension
                not in TEXTRACT_FILE_FORMAT_FALLBACK_CONVERSION_MAP
            ):
                raise e

            output_file_type = TEXTRACT_FILE_FORMAT_FALLBACK_CONVERSION_MAP[
                file_extension
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


# Commented out because no egress to internet

# def send_slack_alert(message: str):
#     try:
#         webhook_url = get_slack_webhook()
#     except Exception:
#         logger.warning("Slack alert not sent due to webhook fetch failure.")
#         return

#     try:
#         response = requests.post(
#             webhook_url,
#             data=json.dumps({"text": message, "channel": SLACK_CHANNEL}),
#             timeout=5,
#         )
#         response.raise_for_status()
#     except Exception as e:
#         logger.error(f"Failed to send Slack alert: {e}")
