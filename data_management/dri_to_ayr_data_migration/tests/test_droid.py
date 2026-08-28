import os
import subprocess
from pathlib import Path
from unittest import mock

import boto3
import pytest
from moto import mock_aws

os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")

os.environ.setdefault("DROID_VERSION", "6.9.13")
os.environ.setdefault("DROID_COMMAND", "/opt/droid/droid.sh")
os.environ.setdefault("DROID_TIMEOUT_SECONDS", "120")

import droid.handler as droid_module
from droid.handler import (
    lambda_handler,
    run_droid,
)


@pytest.fixture
def droid(monkeypatch):
    monkeypatch.setattr(droid_module, "s3", mock.Mock())
    return droid_module


class TestDroidHandler:
    """DROID Lambda handler unit tests."""

    def test_lambda_handler_downloads_file_and_returns_ffid_metadata(
        self,
        droid,
        monkeypatch,
    ):
        run_droid_mock = mock.Mock(
            return_value={
                "EXT": "pdf",
                "PUID": "fmt/18",
                "FORMAT_NAME": "Acrobat PDF 1.4 - Portable Document Format",
                "EXTENSION_MISMATCH": "false",
            }
        )
        monkeypatch.setattr(droid_module, "run_droid", run_droid_mock)

        result = lambda_handler(
            {
                "bucket": "temp-data-bucket",
                "key": "MIG 1/TDR-1/file-1",
                "fileId": "file-1",
                "extension": "pdf",
            },
            None,
        )

        droid.s3.download_file.assert_called_once_with(
            "temp-data-bucket",
            "MIG 1/TDR-1/file-1",
            "/tmp/file-1.pdf",
        )

        run_droid_mock.assert_called_once_with(Path("/tmp/file-1.pdf"))

        assert result == {
            "fileId": "file-1",
            "ffid_metadata_row": {
                "FileId": "file-1",
                "Extension": "pdf",
                "PUID": "fmt/18",
                "FormatName": "Acrobat PDF 1.4 - Portable Document Format",
                "ExtensionMismatch": "false",
                "FFID-Software": "DROID",
                "FFID-SoftwareVersion": "6.9.13",
                "FFID-BinarySignatureFileVersion": "",
                "FFID-ContainerSignatureFileVersion": "",
            },
        }


class TestRunDroid:
    """DROID subprocess tests"""

    def test_run_droid_parses_csv_output(self, monkeypatch, tmp_path):
        local_path = tmp_path / "file.pdf"
        local_path.write_bytes(b"dummy")

        completed_process = mock.Mock()
        completed_process.returncode = 0
        completed_process.stderr = ""
        completed_process.stdout = (
            "ID,EXT,PUID,FORMAT_NAME,EXTENSION_MISMATCH\n"
            "1,pdf,fmt/18,Acrobat PDF 1.4 - Portable Document Format,false\n"
        )

        subprocess_run_mock = mock.Mock(return_value=completed_process)
        monkeypatch.setattr(subprocess, "run", subprocess_run_mock)

        result = run_droid(local_path)

        assert result == {
            "ID": "1",
            "EXT": "pdf",
            "PUID": "fmt/18",
            "FORMAT_NAME": "Acrobat PDF 1.4 - Portable Document Format",
            "EXTENSION_MISMATCH": "false",
        }

        subprocess_run_mock.assert_called_once()
        call_args = subprocess_run_mock.call_args

        assert call_args.args[0] == ["/opt/droid/droid.sh", str(local_path)]
        assert call_args.kwargs["cwd"] == "/opt/droid"
        assert call_args.kwargs["capture_output"] is True
        assert call_args.kwargs["text"] is True
        assert call_args.kwargs["timeout"] == 120
        assert call_args.kwargs["check"] is False

        env = call_args.kwargs["env"]
        assert env["HOME"] == "/tmp"
        assert env["TMPDIR"] == "/tmp"
        assert env["XDG_CONFIG_HOME"] == "/tmp"
        assert env["XDG_CACHE_HOME"] == "/tmp"
        assert "-Duser.home=/tmp" in env["JAVA_TOOL_OPTIONS"]
        assert "-Djava.io.tmpdir=/tmp" in env["JAVA_TOOL_OPTIONS"]

    def test_run_droid_raises_when_droid_fails(self, monkeypatch, tmp_path):
        local_path = tmp_path / "file.pdf"
        local_path.write_bytes(b"dummy")

        completed_process = mock.Mock()
        completed_process.returncode = 1
        completed_process.stderr = "DROID failed"
        completed_process.stdout = ""

        monkeypatch.setattr(
            subprocess,
            "run",
            mock.Mock(return_value=completed_process),
        )

        with pytest.raises(
            RuntimeError, match="DROID failed with return code 1"
        ):
            run_droid(local_path)

    def test_run_droid_raises_when_no_csv_rows_returned(
        self, monkeypatch, tmp_path
    ):
        local_path = tmp_path / "file.pdf"
        local_path.write_bytes(b"dummy")

        completed_process = mock.Mock()
        completed_process.returncode = 0
        completed_process.stderr = ""
        completed_process.stdout = (
            "ID,EXT,PUID,FORMAT_NAME,EXTENSION_MISMATCH\n"
        )

        monkeypatch.setattr(
            subprocess,
            "run",
            mock.Mock(return_value=completed_process),
        )

        with pytest.raises(RuntimeError, match="DROID produced no CSV rows"):
            run_droid(local_path)


@pytest.mark.integration
@mock_aws
def test_lambda_handler_with_moto_and_installed_droid(monkeypatch):
    """Exercise Moto download and the real DROID installation end to end."""
    region = "eu-west-2"
    bucket = "droid-integration-test-bucket"
    key = "MIG 1/TDR-1/integration-file"  # Deliberately no extension.
    file_id = "droid-integration-file"
    local_path = Path("/tmp/droid-integration-file.pdf")
    pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog >>\n"
        b"endobj\n"
        b"trailer\n"
        b"<< /Root 1 0 R >>\n"
        b"%%EOF\n"
    )

    droid_command = Path(droid_module.DROID_COMMAND)
    assert droid_command.is_file(), (
        f"DROID command is not installed at {droid_command}"
    )
    assert os.access(droid_command, os.X_OK), (
        f"DROID command is not executable: {droid_command}"
    )

    moto_s3 = boto3.client("s3", region_name=region)
    moto_s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={"LocationConstraint": region},
    )
    moto_s3.put_object(Bucket=bucket, Key=key, Body=pdf_bytes)

    monkeypatch.setattr(droid_module, "s3", moto_s3)

    try:
        result = lambda_handler(
            {
                "bucket": bucket,
                "key": key,
                "fileId": file_id,
                "extension": "pdf",
            },
            None,
        )

        assert local_path.read_bytes() == pdf_bytes
        assert result["fileId"] == file_id

        metadata = result["ffid_metadata_row"]
        assert metadata["FileId"] == file_id
        assert metadata["Extension"] == "pdf"
        assert metadata["PUID"] == "fmt/18"
        assert (
            metadata["FormatName"]
            == "Acrobat PDF 1.4 - Portable Document Format"
        )
        assert metadata["ExtensionMismatch"] == "false"
        assert metadata["FFID-Software"] == "DROID"
        assert metadata["FFID-SoftwareVersion"] == "6.9.13"
    finally:
        local_path.unlink(missing_ok=True)
