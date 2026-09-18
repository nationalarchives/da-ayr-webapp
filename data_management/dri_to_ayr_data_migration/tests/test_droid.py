import csv
import json
import os
import subprocess
from io import StringIO
from pathlib import Path
from unittest import mock

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")

os.environ.setdefault("DROID_VERSION", "6.9.13")
os.environ.setdefault("DROID_COMMAND", "/opt/droid/droid.sh")
os.environ.setdefault("DROID_TIMEOUT_SECONDS", "120")
os.environ.setdefault("DDT_TEMP_CSV_BUCKET", "temp-csv-bucket")
os.environ.setdefault("TRACKING_TABLE_NAME", "tracking-table")
os.environ.setdefault(
    "FINALISER_QUEUE_URL",
    "https://sqs.example.com/finaliser",
)

import droid.handler as droid_module
from droid.handler import run_droid

RUN_ID = "run-1"
SERIES = "MIG 1"
CONSIGNMENT_REFERENCE = "TDR-1"
FILE_ID = "file-1"
DATA_BUCKET = "temp-data-bucket"
DATA_KEY = f"{SERIES}/{CONSIGNMENT_REFERENCE}/{FILE_ID}"
FIXED_NOW = "2026-09-16T08:00:00Z"

FFID_METADATA_ROW = {
    "FileId": FILE_ID,
    "Extension": "pdf",
    "PUID": "fmt/18",
    "FormatName": "Acrobat PDF 1.4 - Portable Document Format",
    "ExtensionMismatch": "false",
    "FFID-Software": "DROID",
    "FFID-SoftwareVersion": "6.9.13",
    "FFID-BinarySignatureFileVersion": "",
    "FFID-ContainerSignatureFileVersion": "",
}


def droid_message() -> dict[str, str]:
    return {
        "runId": RUN_ID,
        "series": SERIES,
        "consignmentReference": CONSIGNMENT_REFERENCE,
        "bucket": DATA_BUCKET,
        "key": DATA_KEY,
        "fileId": FILE_ID,
        "extension": "pdf",
    }


def consignment_item(
    *,
    status: str = "STAGING",
    expected: int = 1,
    completed: int = 1,
    finaliser_sent_at: str | None = None,
) -> dict[str, dict[str, str]]:
    item = {
        "status": {"S": status},
        "expectedFileCount": {"N": str(expected)},
        "completedFileCount": {"N": str(completed)},
    }

    if finaliser_sent_at:
        item["finaliserMessageSentAt"] = {"S": finaliser_sent_at}

    return item


@pytest.fixture
def droid(monkeypatch):
    monkeypatch.setattr(droid_module, "s3", mock.Mock(name="s3_client"))
    monkeypatch.setattr(droid_module, "sqs", mock.Mock(name="sqs_client"))
    monkeypatch.setattr(
        droid_module,
        "dynamodb",
        mock.Mock(name="dynamodb_client"),
    )
    return droid_module


class TestDroidHandler:
    """DROID Lambda handler and orchestration tests."""

    def test_lambda_handler_supports_direct_retry(
        self,
        droid,
        monkeypatch,
    ):
        expected = {
            "fileId": FILE_ID,
            "ffidMetadataKey": "staging/AYR-ffid-metadata.csv",
            "finaliserTriggered": False,
        }
        process_message = mock.Mock(return_value=expected)
        monkeypatch.setattr(droid, "process_message", process_message)

        result = droid.lambda_handler(droid_message(), None)

        assert result == expected
        process_message.assert_called_once_with(droid_message())

    def test_lambda_handler_processes_successful_sqs_message(
        self,
        droid,
        monkeypatch,
    ):
        process_message = mock.Mock()
        monkeypatch.setattr(droid, "process_message", process_message)

        result = droid.lambda_handler(
            {
                "Records": [
                    {
                        "messageId": "message-1",
                        "body": json.dumps(droid_message()),
                    }
                ]
            },
            None,
        )

        assert result == {"batchItemFailures": []}
        process_message.assert_called_once_with(droid_message())

    def test_lambda_handler_reports_failed_sqs_message(
        self,
        droid,
        monkeypatch,
    ):
        process_message = mock.Mock(side_effect=RuntimeError("DROID failed"))
        monkeypatch.setattr(droid, "process_message", process_message)

        result = droid.lambda_handler(
            {
                "Records": [
                    {
                        "messageId": "message-1",
                        "body": json.dumps(droid_message()),
                    }
                ]
            },
            None,
        )

        assert result == {
            "batchItemFailures": [{"itemIdentifier": "message-1"}]
        }

    def test_process_message_skips_completed_file_and_rechecks_finaliser(
        self,
        droid,
        monkeypatch,
    ):
        is_complete = mock.Mock(return_value=True)
        trigger_finaliser = mock.Mock(return_value=True)
        identify = mock.Mock()
        upload_ffid = mock.Mock()
        mark_complete = mock.Mock()

        monkeypatch.setattr(droid, "is_file_already_complete", is_complete)
        monkeypatch.setattr(
            droid,
            "trigger_finaliser_if_ready",
            trigger_finaliser,
        )
        monkeypatch.setattr(droid, "identify_s3_object", identify)
        monkeypatch.setattr(droid, "upload_ffid_metadata_csv", upload_ffid)
        monkeypatch.setattr(
            droid,
            "mark_file_complete_and_trigger_finaliser_if_consignment_ready",
            mark_complete,
        )

        result = droid.process_message(droid_message())

        assert result == {
            "fileId": FILE_ID,
            "skipped": True,
            "finaliserTriggered": True,
        }
        is_complete.assert_called_once_with(
            run_id=RUN_ID,
            consignment_reference=CONSIGNMENT_REFERENCE,
            file_id=FILE_ID,
        )
        trigger_finaliser.assert_called_once_with(
            run_id=RUN_ID,
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
        )
        identify.assert_not_called()
        upload_ffid.assert_not_called()
        mark_complete.assert_not_called()

    def test_process_message_uploads_ffid_and_marks_file_complete(
        self,
        droid,
        monkeypatch,
    ):
        ffid_key = (
            f"{SERIES}/ayr-mds-staging/{CONSIGNMENT_REFERENCE}/{FILE_ID}/"
            "AYR-ffid-metadata.csv"
        )
        monkeypatch.setattr(
            droid,
            "is_file_already_complete",
            mock.Mock(return_value=False),
        )
        identify = mock.Mock(return_value=FFID_METADATA_ROW)
        upload_ffid = mock.Mock(return_value=ffid_key)
        mark_complete = mock.Mock(return_value=True)
        monkeypatch.setattr(droid, "identify_s3_object", identify)
        monkeypatch.setattr(droid, "upload_ffid_metadata_csv", upload_ffid)
        monkeypatch.setattr(
            droid,
            "mark_file_complete_and_trigger_finaliser_if_consignment_ready",
            mark_complete,
        )

        result = droid.process_message(droid_message())

        assert result == {
            "fileId": FILE_ID,
            "ffidMetadataKey": ffid_key,
            "finaliserTriggered": True,
        }
        identify.assert_called_once_with(
            bucket=DATA_BUCKET,
            key=DATA_KEY,
            file_id=FILE_ID,
            extension="pdf",
        )
        upload_ffid.assert_called_once_with(
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
            file_id=FILE_ID,
            row=FFID_METADATA_ROW,
        )
        mark_complete.assert_called_once_with(
            run_id=RUN_ID,
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
            file_id=FILE_ID,
        )

    def test_identify_s3_object_downloads_maps_and_removes_local_file(
        self,
        droid,
        monkeypatch,
        tmp_path,
    ):
        local_path = tmp_path / "file-1.pdf"

        def download_file(bucket, key, destination):
            assert bucket == DATA_BUCKET
            assert key == DATA_KEY
            Path(destination).write_bytes(b"PDF")

        droid.s3.download_file.side_effect = download_file
        monkeypatch.setattr(
            droid,
            "build_local_path",
            mock.Mock(return_value=local_path),
        )
        run_droid_mock = mock.Mock(
            return_value={
                "EXT": "pdf",
                "PUID": "fmt/18",
                "FORMAT_NAME": ("Acrobat PDF 1.4 - Portable Document Format"),
                "EXTENSION_MISMATCH": "false",
            }
        )
        monkeypatch.setattr(droid, "run_droid", run_droid_mock)

        result = droid.identify_s3_object(
            bucket=DATA_BUCKET,
            key=DATA_KEY,
            file_id=FILE_ID,
            extension="pdf",
        )

        assert result == FFID_METADATA_ROW
        droid.s3.download_file.assert_called_once_with(
            DATA_BUCKET,
            DATA_KEY,
            str(local_path),
        )
        run_droid_mock.assert_called_once_with(local_path)
        assert not local_path.exists()

    def test_build_local_path_sanitises_file_id_and_extension(self, droid):
        result = droid.build_local_path("file/../1", ".P-D_F")

        assert result == Path("/tmp/file1.pdf")

    def test_upload_ffid_metadata_csv_writes_expected_s3_object(self, droid):
        result = droid.upload_ffid_metadata_csv(
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
            file_id=FILE_ID,
            row=FFID_METADATA_ROW,
        )

        expected_key = (
            f"{SERIES}/ayr-mds-staging/{CONSIGNMENT_REFERENCE}/{FILE_ID}/"
            "AYR-ffid-metadata.csv"
        )
        assert result == expected_key

        droid.s3.put_object.assert_called_once()
        put_kwargs = droid.s3.put_object.call_args.kwargs
        assert put_kwargs["Bucket"] == "temp-csv-bucket"
        assert put_kwargs["Key"] == expected_key
        assert put_kwargs["ContentType"] == "text/csv"

        csv_rows = list(
            csv.DictReader(StringIO(put_kwargs["Body"].decode("utf-8")))
        )
        assert csv_rows == [FFID_METADATA_ROW]

    @pytest.mark.parametrize(
        ("item", "expected"),
        [
            ({}, False),
            ({"Item": {"status": {"S": "PROCESSING"}}}, False),
            ({"Item": {"status": {"S": "COMPLETE"}}}, True),
        ],
    )
    def test_is_file_already_complete(self, droid, item, expected):
        droid.dynamodb.get_item.return_value = item

        result = droid.is_file_already_complete(
            run_id=RUN_ID,
            consignment_reference=CONSIGNMENT_REFERENCE,
            file_id=FILE_ID,
        )

        assert result is expected

    def test_mark_file_complete_updates_tracking_and_checks_finaliser(
        self,
        droid,
        monkeypatch,
    ):
        monkeypatch.setattr(droid, "utc_now_text", lambda: FIXED_NOW)
        trigger_finaliser = mock.Mock(return_value=True)
        monkeypatch.setattr(
            droid,
            "trigger_finaliser_if_ready",
            trigger_finaliser,
        )

        result = (
            droid.mark_file_complete_and_trigger_finaliser_if_consignment_ready(
                run_id=RUN_ID,
                series=SERIES,
                consignment_reference=CONSIGNMENT_REFERENCE,
                file_id=FILE_ID,
            )
        )

        assert result is True
        droid.dynamodb.transact_write_items.assert_called_once()
        transaction = droid.dynamodb.transact_write_items.call_args.kwargs
        updates = transaction["TransactItems"]
        assert len(updates) == 2
        assert updates[0]["Update"]["Key"] == {
            "PK": {"S": f"RUN#{RUN_ID}#CONSIGNMENT#{CONSIGNMENT_REFERENCE}"},
            "SK": {"S": f"FILE#{FILE_ID}"},
        }
        assert updates[1]["Update"]["Key"] == {
            "PK": {"S": f"RUN#{RUN_ID}"},
            "SK": {"S": f"CONSIGNMENT#{CONSIGNMENT_REFERENCE}"},
        }
        trigger_finaliser.assert_called_once_with(
            run_id=RUN_ID,
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
        )

    def test_mark_file_complete_rechecks_finaliser_after_duplicate(
        self,
        droid,
        monkeypatch,
    ):
        droid.dynamodb.transact_write_items.side_effect = ClientError(
            {
                "Error": {
                    "Code": "TransactionCanceledException",
                    "Message": "Already complete",
                }
            },
            "TransactWriteItems",
        )
        monkeypatch.setattr(
            droid,
            "is_file_already_complete",
            mock.Mock(return_value=True),
        )
        trigger_finaliser = mock.Mock(return_value=False)
        monkeypatch.setattr(
            droid,
            "trigger_finaliser_if_ready",
            trigger_finaliser,
        )

        result = (
            droid.mark_file_complete_and_trigger_finaliser_if_consignment_ready(
                run_id=RUN_ID,
                series=SERIES,
                consignment_reference=CONSIGNMENT_REFERENCE,
                file_id=FILE_ID,
            )
        )

        assert result is False
        trigger_finaliser.assert_called_once_with(
            run_id=RUN_ID,
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
        )

    def test_mark_file_complete_reraises_unexpected_transaction_failure(
        self,
        droid,
        monkeypatch,
    ):
        error = ClientError(
            {
                "Error": {
                    "Code": "TransactionCanceledException",
                    "Message": "Consignment is not staging",
                }
            },
            "TransactWriteItems",
        )
        droid.dynamodb.transact_write_items.side_effect = error
        monkeypatch.setattr(
            droid,
            "is_file_already_complete",
            mock.Mock(return_value=False),
        )

        with pytest.raises(ClientError):
            droid.mark_file_complete_and_trigger_finaliser_if_consignment_ready(
                run_id=RUN_ID,
                series=SERIES,
                consignment_reference=CONSIGNMENT_REFERENCE,
                file_id=FILE_ID,
            )

    def test_trigger_finaliser_returns_false_until_consignment_is_ready(
        self,
        droid,
        monkeypatch,
    ):
        droid.dynamodb.get_item.return_value = {
            "Item": consignment_item(expected=2, completed=1)
        }
        ensure_required = mock.Mock()
        send_finaliser = mock.Mock()
        record_sent = mock.Mock()
        monkeypatch.setattr(
            droid,
            "ensure_required_staged_csvs_exist",
            ensure_required,
        )
        monkeypatch.setattr(
            droid,
            "send_finaliser_message",
            send_finaliser,
        )
        monkeypatch.setattr(
            droid,
            "record_finaliser_message_sent",
            record_sent,
        )

        result = droid.trigger_finaliser_if_ready(
            run_id=RUN_ID,
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
        )

        assert result is False
        droid.dynamodb.update_item.assert_not_called()
        ensure_required.assert_not_called()
        send_finaliser.assert_not_called()
        record_sent.assert_not_called()

    def test_trigger_finaliser_marks_ready_checks_csvs_and_sends_message(
        self,
        droid,
        monkeypatch,
    ):
        droid.dynamodb.get_item.return_value = {"Item": consignment_item()}
        monkeypatch.setattr(droid, "utc_now_text", lambda: FIXED_NOW)
        ensure_required = mock.Mock()
        send_finaliser = mock.Mock(return_value="finaliser-message-1")
        record_sent = mock.Mock()
        monkeypatch.setattr(
            droid,
            "ensure_required_staged_csvs_exist",
            ensure_required,
        )
        monkeypatch.setattr(
            droid,
            "send_finaliser_message",
            send_finaliser,
        )
        monkeypatch.setattr(
            droid,
            "record_finaliser_message_sent",
            record_sent,
        )

        result = droid.trigger_finaliser_if_ready(
            run_id=RUN_ID,
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
        )

        assert result is True
        droid.dynamodb.update_item.assert_called_once()
        update_kwargs = droid.dynamodb.update_item.call_args.kwargs
        assert update_kwargs["TableName"] == "tracking-table"
        assert update_kwargs["ExpressionAttributeValues"][":ready"] == {
            "S": "READY_TO_FINALISE"
        }
        ensure_required.assert_called_once_with(
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
        )
        send_finaliser.assert_called_once_with(
            run_id=RUN_ID,
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
        )
        record_sent.assert_called_once_with(
            consignment_key={
                "PK": {"S": f"RUN#{RUN_ID}"},
                "SK": {"S": f"CONSIGNMENT#{CONSIGNMENT_REFERENCE}"},
            },
            message_id="finaliser-message-1",
        )

    def test_trigger_finaliser_does_not_resend_recorded_message(
        self,
        droid,
        monkeypatch,
    ):
        droid.dynamodb.get_item.return_value = {
            "Item": consignment_item(
                status="READY_TO_FINALISE",
                finaliser_sent_at=FIXED_NOW,
            )
        }
        send_finaliser = mock.Mock()
        monkeypatch.setattr(
            droid,
            "send_finaliser_message",
            send_finaliser,
        )

        result = droid.trigger_finaliser_if_ready(
            run_id=RUN_ID,
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
        )

        assert result is False
        send_finaliser.assert_not_called()

    def test_trigger_finaliser_handles_concurrent_ready_transition(
        self,
        droid,
        monkeypatch,
    ):
        droid.dynamodb.get_item.side_effect = [
            {"Item": consignment_item()},
            {
                "Item": consignment_item(
                    status="READY_TO_FINALISE",
                    finaliser_sent_at=FIXED_NOW,
                )
            },
        ]
        droid.dynamodb.update_item.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ConditionalCheckFailedException",
                    "Message": "Already transitioned",
                }
            },
            "UpdateItem",
        )
        send_finaliser = mock.Mock()
        monkeypatch.setattr(
            droid,
            "send_finaliser_message",
            send_finaliser,
        )

        result = droid.trigger_finaliser_if_ready(
            run_id=RUN_ID,
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
        )

        assert result is False
        assert droid.dynamodb.get_item.call_count == 2
        send_finaliser.assert_not_called()

    def test_ensure_required_staged_csvs_exist_checks_all_required_files(
        self,
        droid,
    ):
        droid.ensure_required_staged_csvs_exist(
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
        )

        droid.s3.head_object.assert_has_calls(
            [
                mock.call(
                    Bucket="temp-csv-bucket",
                    Key=(
                        f"{SERIES}/ayr-mds-staging/shared/AYR-body-metadata.csv"
                    ),
                ),
                mock.call(
                    Bucket="temp-csv-bucket",
                    Key=(
                        f"{SERIES}/ayr-mds-staging/shared/"
                        "AYR-series-metadata.csv"
                    ),
                ),
                mock.call(
                    Bucket="temp-csv-bucket",
                    Key=(
                        f"{SERIES}/ayr-mds-staging/"
                        f"{CONSIGNMENT_REFERENCE}/"
                        "AYR-consignment-metadata.csv"
                    ),
                ),
            ]
        )
        assert droid.s3.head_object.call_count == 3

    def test_ensure_required_staged_csvs_exist_propagates_missing_file(
        self,
        droid,
    ):
        droid.s3.head_object.side_effect = ClientError(
            {
                "Error": {
                    "Code": "404",
                    "Message": "Not Found",
                }
            },
            "HeadObject",
        )

        with pytest.raises(ClientError):
            droid.ensure_required_staged_csvs_exist(
                series=SERIES,
                consignment_reference=CONSIGNMENT_REFERENCE,
            )

    def test_send_finaliser_message_sends_expected_sqs_message(self, droid):
        droid.sqs.send_message.return_value = {
            "MessageId": "finaliser-message-1"
        }

        result = droid.send_finaliser_message(
            run_id=RUN_ID,
            series=SERIES,
            consignment_reference=CONSIGNMENT_REFERENCE,
        )

        assert result == "finaliser-message-1"
        droid.sqs.send_message.assert_called_once()
        send_kwargs = droid.sqs.send_message.call_args.kwargs
        assert send_kwargs["QueueUrl"] == ("https://sqs.example.com/finaliser")
        assert json.loads(send_kwargs["MessageBody"]) == {
            "runId": RUN_ID,
            "series": SERIES,
            "consignmentReference": CONSIGNMENT_REFERENCE,
        }

    def test_record_finaliser_message_sent_updates_tracking_item(
        self,
        droid,
        monkeypatch,
    ):
        monkeypatch.setattr(droid, "utc_now_text", lambda: FIXED_NOW)
        key = {
            "PK": {"S": f"RUN#{RUN_ID}"},
            "SK": {"S": f"CONSIGNMENT#{CONSIGNMENT_REFERENCE}"},
        }

        droid.record_finaliser_message_sent(
            consignment_key=key,
            message_id="finaliser-message-1",
        )

        droid.dynamodb.update_item.assert_called_once_with(
            TableName="tracking-table",
            Key=key,
            UpdateExpression=(
                "SET finaliserMessageSentAt = :now, "
                "finaliserSqsMessageId = :message_id, updatedAt = :now"
            ),
            ConditionExpression=(
                "attribute_not_exists(finaliserMessageSentAt)"
            ),
            ExpressionAttributeValues={
                ":now": {"S": FIXED_NOW},
                ":message_id": {"S": "finaliser-message-1"},
            },
        )

    def test_record_finaliser_message_sent_ignores_duplicate_record(
        self,
        droid,
    ):
        droid.dynamodb.update_item.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ConditionalCheckFailedException",
                    "Message": "Already recorded",
                }
            },
            "UpdateItem",
        )

        droid.record_finaliser_message_sent(
            consignment_key={
                "PK": {"S": f"RUN#{RUN_ID}"},
                "SK": {"S": f"CONSIGNMENT#{CONSIGNMENT_REFERENCE}"},
            },
            message_id="finaliser-message-1",
        )

    def test_get_consignment_tracking_item_requires_existing_item(self, droid):
        droid.dynamodb.get_item.return_value = {}

        with pytest.raises(ValueError, match="Missing consignment tracking"):
            droid.get_consignment_tracking_item(
                {
                    "PK": {"S": f"RUN#{RUN_ID}"},
                    "SK": {"S": f"CONSIGNMENT#{CONSIGNMENT_REFERENCE}"},
                }
            )


class TestRunDroid:
    """DROID subprocess tests."""

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

    def test_run_droid_raises_when_droid_fails(
        self,
        monkeypatch,
        tmp_path,
    ):
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
            RuntimeError,
            match="DROID failed with return code 1",
        ):
            run_droid(local_path)

    def test_run_droid_raises_when_no_csv_rows_returned(
        self,
        monkeypatch,
        tmp_path,
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
def test_identify_s3_object_with_moto_and_installed_droid(monkeypatch):
    """Exercise Moto download and the real DROID installation end to end."""
    region = "eu-west-2"
    bucket = "droid-integration-test-bucket"
    key = "MIG 1/TDR-1/integration-file"
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
        result = droid_module.identify_s3_object(
            bucket=bucket,
            key=key,
            file_id=file_id,
            extension="pdf",
        )

        assert not local_path.exists()
        assert result["FileId"] == file_id
        assert result["Extension"] == "pdf"
        assert result["PUID"] == "fmt/18"
        assert (
            result["FormatName"] == "Acrobat PDF 1.4 - Portable Document Format"
        )
        assert result["ExtensionMismatch"] == "false"
        assert result["FFID-Software"] == "DROID"
        assert result["FFID-SoftwareVersion"] == "6.9.13"
    finally:
        local_path.unlink(missing_ok=True)
