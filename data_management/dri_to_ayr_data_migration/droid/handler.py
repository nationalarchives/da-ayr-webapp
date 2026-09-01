import csv
import logging
import os
import subprocess  # nosec
from io import StringIO
from pathlib import Path
from typing import Any

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

DROID_COMMAND = os.environ["DROID_COMMAND"]
DROID_VERSION = os.environ["DROID_VERSION"]
DROID_TIMEOUT_SECONDS = int(os.getenv("DROID_TIMEOUT_SECONDS", "120"))


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    Run DROID against one staged S3 object and return the FFID metadata row.

    Expected event:
    {
      "bucket": "ddt-temp-data-bucket",
      "key": "LEV 2/TDR-2026-7333/<fileId>",
      "fileId": "<fileId>",
      "extension": "pdf"
    }
    """
    bucket = require_text(event, "bucket")
    key = require_text(event, "key")
    file_id = require_text(event, "fileId")
    extension = event.get("extension") or ""

    local_path = build_local_path(file_id, extension)

    logger.info("Downloading s3://%s/%s to %s", bucket, key, local_path)
    s3.download_file(bucket, key, str(local_path))

    droid_row = run_droid(local_path)
    ffid_metadata_row = map_droid_row_to_ffid_metadata(file_id, droid_row)

    return {
        "fileId": file_id,
        "ffid_metadata_row": ffid_metadata_row,
    }


def build_local_path(file_id: str, extension: str) -> Path:
    safe_file_id = "".join(
        char for char in file_id if char.isalnum() or char in "-_"
    )
    safe_extension = "".join(
        char for char in str(extension).lower() if char.isalnum()
    )

    if safe_extension:
        return Path("/tmp") / f"{safe_file_id}.{safe_extension}"  # nosec

    return Path("/tmp") / safe_file_id  # nosec


def run_droid(local_path: Path) -> dict[str, str]:
    # Lambda's filesystem is read-only except /tmp. DROID/Java may try to write
    # temp, cache or config files, so force those locations to /tmp.
    env = {
        **os.environ,
        "HOME": "/tmp",  # nosec
        "TMPDIR": "/tmp",  # nosec
        "XDG_CONFIG_HOME": "/tmp",  # nosec
        "XDG_CACHE_HOME": "/tmp",  # nosec
        "JAVA_TOOL_OPTIONS": " ".join(
            part
            for part in [
                os.environ.get("JAVA_TOOL_OPTIONS", ""),
                "-Duser.home=/tmp",
                "-Djava.io.tmpdir=/tmp",
            ]
            if part
        ),
    }

    logger.info("Running DROID command: %s %s", DROID_COMMAND, local_path)

    result = subprocess.run(  # nosec
        [DROID_COMMAND, str(local_path)],
        cwd="/opt/droid",
        env=env,
        capture_output=True,
        text=True,
        timeout=DROID_TIMEOUT_SECONDS,
        check=False,
    )

    logger.info("DROID returncode=%s", result.returncode)

    if result.stderr:
        logger.info("DROID stderr: %s", result.stderr[:4000])

    if result.returncode != 0:
        raise RuntimeError(
            f"DROID failed with return code {result.returncode}. stderr={result.stderr[:4000]}"
        )

    rows = list(csv.DictReader(StringIO(result.stdout)))

    if not rows:
        raise RuntimeError(
            f"DROID produced no CSV rows. stdout={result.stdout[:4000]}"
        )

    return rows[0]


def map_droid_row_to_ffid_metadata(
    file_id: str, droid_row: dict[str, str]
) -> dict[str, str]:
    return {
        "FileId": file_id,
        "Extension": droid_row.get("EXT", ""),
        "PUID": droid_row.get("PUID", ""),
        "FormatName": droid_row.get("FORMAT_NAME", ""),
        "ExtensionMismatch": droid_row.get("EXTENSION_MISMATCH", ""),
        "FFID-Software": "DROID",
        "FFID-SoftwareVersion": DROID_VERSION,
        "FFID-BinarySignatureFileVersion": "",
        "FFID-ContainerSignatureFileVersion": "",
    }


def require_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing required field: {key}")

    return value.strip()
