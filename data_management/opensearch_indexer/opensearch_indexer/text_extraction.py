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
    "fmt/1": "wav",
    "fmt/2": "wav",
    "fmt/6": "wav",
    "fmt/141": "wav",
    "fmt/142": "wav",
    "fmt/143": "wav",
    "fmt/134": "mp3",
    "fmt/386": "mpg",
    "fmt/278": "elm",
    "fmt/39": "doc",
    "fmt/40": "doc",
    "x-fmt/44": "doc",
    "x-fmt/45": "doc",
    "fmt/50": "rtf",
    "fmt/59": "xls",
    "fmt/61": "xls",
    "fmt/116": "bmp",
    "x-fmt/111": "txt",
    "x-fmt/116": "wk4",
    "fmt/126": "ppt",
    "fmt/214": "xlsx",
    "fmt/215": "pptx",
    "fmt/355": "rtf",
    "x-fmt/394": "wp",
    "fmt/412": "docx",
    "x-fmt/245": "mpp",
    "x-fmt/430": "msg",
    "x-fmt/258": "vsd",
    "fmt/443": "vsd",
    "fmt/1510": "vsd",
    "x-fmt/115": "wk3",
    "x-fmt/255": "pub",
    "x-fmt/332": "fm3",
    "x-fmt/18": "csv",
    "fmt/291": "odt",
    "fmt/203": "ogg",
}


def add_text_content(file: Dict, file_stream: bytes) -> Dict:

    file_puid = file.ffid_metadata.PUID if file.ffid_metadata else None
    file_id = file["file_id"]

    if file_puid not in SUPPORTED_TEXTRACT_PUIDS:
        logger.info(
            f"Text extraction skipped for file {file_id} due to unsupported file type: {file_puid}"
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
            file["content"] = extract_text(file_stream, file_puid)
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
