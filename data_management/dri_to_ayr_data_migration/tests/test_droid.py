import csv
import json
import os
import re
import socket
import subprocess
import tempfile
from io import StringIO
from pathlib import Path
from unittest import mock
from urllib.parse import urlsplit
from uuid import uuid4

import boto3
import pytest
from botocore.config import Config
from botocore.exceptions import ClientError
from moto import mock_aws

os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")

os.environ.setdefault("DROID_VERSION", "6.9.13")
os.environ.setdefault("DROID_COMMAND", "/opt/droid/droid.sh")
os.environ.setdefault("DROID_TIMEOUT_SECONDS", "120")
os.environ.setdefault("DDT_TEMP_DATA_BUCKET", "temp-data-bucket")
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


DROID_METADATA_ROW = {
    "EXT": "pdf",
    "PUID": "fmt/18",
    "FORMAT_NAME": "Acrobat PDF 1.4 - Portable Document Format",
    "EXTENSION_MISMATCH": "false",
}


def droid_message() -> dict[str, str]:
    return {
        "runId": RUN_ID,
        "series": SERIES,
        "consignmentReference": CONSIGNMENT_REFERENCE,
        "key": DATA_KEY,
        "fileId": FILE_ID,
        "extension": "pdf",
    }


def mock_droid_command(
    monkeypatch, csv_output, *, stdout="", stderr="", returncode=0
):
    """Simulate DROID writing CSV to the path supplied after -o."""

    def execute(command, **kwargs):
        assert command[2] == "-o"
        output = Path(command[3])
        assert output.parent.is_dir()
        output.write_text(csv_output, encoding="utf-8")
        return subprocess.CompletedProcess(command, returncode, stdout, stderr)

    run = mock.Mock(side_effect=execute)
    monkeypatch.setattr(subprocess, "run", run)
    return run


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
    """Return the handler module with its AWS clients replaced by mocks."""
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

    @pytest.mark.parametrize("flag", ["true", 1, None])
    def test_process_message_rejects_non_boolean_partial_override(
        self, droid, flag
    ):
        with pytest.raises(ValueError, match="must be a boolean"):
            droid.process_message(
                {**droid_message(), "allowPartialIdentification": flag}
            )
        droid.s3.copy.assert_not_called()
        droid.dynamodb.get_item.assert_not_called()

    @mock_aws
    def test_process_message_logs_partial_identification_and_completes_once(
        self, droid, monkeypatch, caplog
    ):
        db = boto3.client("dynamodb", region_name="eu-west-2")
        db.create_table(
            TableName="tracking-table",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        file_key = {
            "PK": {"S": f"RUN#{RUN_ID}#CONSIGNMENT#{CONSIGNMENT_REFERENCE}"},
            "SK": {"S": f"FILE#{FILE_ID}"},
        }
        consignment_key = {
            "PK": {"S": f"RUN#{RUN_ID}"},
            "SK": {"S": f"CONSIGNMENT#{CONSIGNMENT_REFERENCE}"},
        }
        db.put_item(
            TableName="tracking-table",
            Item={**file_key, "status": {"S": "PENDING"}},
        )
        db.put_item(
            TableName="tracking-table",
            Item={**consignment_key, **consignment_item(completed=0)},
        )
        monkeypatch.setattr(droid, "dynamodb", db)
        monkeypatch.setattr(droid, "utc_now_text", lambda: FIXED_NOW)
        monkeypatch.setattr(
            droid, "uuid4", mock.Mock(return_value=mock.Mock(hex="attempt-1"))
        )
        uri = "s3://temp-data-bucket/_ayr-droid-inputs/attempt-1/file-1.xls"
        subprocess_run = mock_droid_command(
            monkeypatch,
            (
                "ID,URI,STATUS,EXT,PUID,FORMAT_NAME,EXTENSION_MISMATCH\n"
                f"1,{uri},Done,xls,fmt/111,OLE2 Compound Document Format,false\n"
            ),
            stdout="2026-11-09T11:59:40,335 ERROR [core-thread-1] "
            "Ole2IdentifierEngine:133 - No reader was obtained\n",
        )
        droid.sqs.send_message.return_value = {"MessageId": "finaliser-message"}
        message = {
            **droid_message(),
            "extension": "xls",
            "allowPartialIdentification": True,
        }

        # Default retries cannot complete or upload an FFID result after an ERROR.
        with pytest.raises(RuntimeError, match="identification errors"):
            droid.process_message({**droid_message(), "extension": "xls"})
        droid.s3.put_object.assert_not_called()
        assert db.get_item(TableName="tracking-table", Key=file_key)["Item"][
            "status"
        ] == {"S": "PENDING"}

        result = droid.process_message(message)
        assert result["finaliserTriggered"] is True
        item = db.get_item(TableName="tracking-table", Key=file_key)["Item"]
        assert item == {
            **file_key,
            "status": {"S": "COMPLETE"},
            "completedAt": {"S": FIXED_NOW},
            "updatedAt": {"S": FIXED_NOW},
        }
        assert "Partial DROID identification override requested" in caplog.text
        assert "Accepting partial DROID identification" in caplog.text
        assert "No reader was obtained" in caplog.text
        csv_rows = list(
            csv.DictReader(
                StringIO(
                    droid.s3.put_object.call_args.kwargs["Body"].decode("utf-8")
                )
            )
        )
        assert csv_rows[0]["PUID"] == "fmt/111"
        assert csv_rows[0]["FormatName"] == "OLE2 Compound Document Format"

        # Both approved and original duplicate messages preserve the counter.
        assert droid.process_message(message)["skipped"] is True
        assert droid.process_message(droid_message())["skipped"] is True
        consignment = db.get_item(
            TableName="tracking-table", Key=consignment_key
        )["Item"]
        assert consignment["completedFileCount"] == {"N": "1"}
        assert consignment["status"] == {"S": "READY_TO_FINALISE"}
        droid.sqs.send_message.assert_called_once()
        droid.s3.put_object.assert_called_once()
        assert subprocess_run.call_count == 2

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
        run_s3_droid = mock.Mock()
        upload_ffid = mock.Mock()
        mark_complete = mock.Mock()

        monkeypatch.setattr(droid, "is_file_already_complete", is_complete)
        monkeypatch.setattr(
            droid,
            "trigger_finaliser_if_ready",
            trigger_finaliser,
        )
        monkeypatch.setattr(droid, "run_droid_for_s3_object", run_s3_droid)
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
        run_s3_droid.assert_not_called()
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
        run_s3_droid = mock.Mock(return_value=DROID_METADATA_ROW)
        upload_ffid = mock.Mock(return_value=ffid_key)
        mark_complete = mock.Mock(return_value=True)
        monkeypatch.setattr(droid, "run_droid_for_s3_object", run_s3_droid)
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
        run_s3_droid.assert_called_once_with(
            key=DATA_KEY,
            file_id=FILE_ID,
            extension="pdf",
            allow_partial_identification=False,
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

    @pytest.mark.parametrize(
        "key",
        [
            "../secret.pdf",
            "folder/../../secret.pdf",
            "folder/./file.pdf",
            "folder//file.pdf",
            "folder/",
            "",
        ],
    )
    def test_validate_s3_object_key_rejects_unsafe_keys(self, droid, key):
        with pytest.raises(ValueError, match="Unsafe S3 object key"):
            droid.validate_s3_object_key(key)

    def test_build_droid_input_alias_key_sanitises_name_and_extension(
        self,
        droid,
        monkeypatch,
    ):
        monkeypatch.setattr(
            droid,
            "uuid4",
            mock.Mock(return_value=mock.Mock(hex="attempt-1")),
        )

        result = droid.build_droid_input_alias_key("file/../1", ".P-D_F")

        assert result == "_ayr-droid-inputs/attempt-1/file1.pdf"

    def test_build_droid_input_alias_key_rejects_empty_safe_file_id(
        self,
        droid,
    ):
        with pytest.raises(ValueError, match="cannot form a safe DROID alias"):
            droid.build_droid_input_alias_key("../", "pdf")

    def test_run_droid_for_s3_object_copies_runs_and_deletes_alias(
        self,
        droid,
        monkeypatch,
    ):
        alias_key = "_ayr-droid-inputs/attempt-1/file1.pdf"
        alias_uri = f"s3://temp-data-bucket/{alias_key}"
        monkeypatch.setattr(
            droid,
            "uuid4",
            mock.Mock(return_value=mock.Mock(hex="attempt-1")),
        )
        run_droid = mock.Mock(return_value=DROID_METADATA_ROW)
        monkeypatch.setattr(droid, "run_droid", run_droid)

        result = droid.run_droid_for_s3_object(
            key=DATA_KEY,
            file_id="file/../1",
            extension=".pdf",
        )

        assert result == DROID_METADATA_ROW
        droid.s3.copy.assert_called_once_with(
            {"Bucket": "temp-data-bucket", "Key": DATA_KEY},
            "temp-data-bucket",
            alias_key,
            Config=droid.DROID_ALIAS_COPY_CONFIG,
        )
        run_droid.assert_called_once_with(
            alias_uri,
            expected_uri=alias_uri,
            allow_partial_identification=False,
        )
        droid.s3.delete_object.assert_called_once_with(
            Bucket="temp-data-bucket",
            Key=alias_key,
        )

    def test_droid_alias_copy_config_uses_multipart_for_large_objects(
        self, droid
    ):
        config = droid.DROID_ALIAS_COPY_CONFIG

        assert config.multipart_threshold == 4 * 1024**3
        assert config.multipart_chunksize == 1024**3
        assert config.max_concurrency == 4

    def test_run_droid_for_s3_object_deletes_alias_after_droid_failure(
        self,
        droid,
        monkeypatch,
    ):
        alias_key = "_ayr-droid-inputs/attempt-1/file1.pdf"
        error = RuntimeError("DROID failed")
        monkeypatch.setattr(
            droid,
            "uuid4",
            mock.Mock(return_value=mock.Mock(hex="attempt-1")),
        )
        monkeypatch.setattr(
            droid,
            "run_droid",
            mock.Mock(side_effect=error),
        )

        with pytest.raises(RuntimeError, match="DROID failed"):
            droid.run_droid_for_s3_object(
                key=DATA_KEY,
                file_id="file/../1",
                extension=".pdf",
            )

        droid.s3.delete_object.assert_called_once_with(
            Bucket="temp-data-bucket",
            Key=alias_key,
        )

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
    def test_is_file_already_complete_returns_status_check(
        self, droid, item, expected
    ):
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

    def test_read_droid_csv_accepts_reordered_columns(self):
        rows = droid_module.read_droid_csv(
            StringIO(
                "FORMAT_NAME,PUID,URI,ID\nPDF,fmt/18,s3://bucket/file.pdf,1\n"
            )
        )
        assert rows == [
            {
                "ID": "1",
                "URI": "s3://bucket/file.pdf",
                "PUID": "fmt/18",
                "FORMAT_NAME": "PDF",
            }
        ]

    def test_run_droid_requires_override_for_ole2_reader_error(
        self, monkeypatch, caplog
    ):
        uri = "s3://temp-data-bucket/_ayr-droid-inputs/attempt/file.xls"
        diagnostic = (
            "2026-11-09T11:59:40,335 ERROR [core-thread-1] "
            f"Ole2IdentifierEngine:133 - No reader was obtained for {uri}. "
            "This may be due to low memory conditions. Try running with a larger heap size!\n"
        )
        output = (
            '"ID","PARENT_ID","URI","FILE_PATH","NAME","METHOD","STATUS","SIZE",'
            '"TYPE","EXT","LAST_MODIFIED","EXTENSION_MISMATCH","HASH",'
            '"FORMAT_COUNT","PUID","MIME_TYPE","FORMAT_NAME","FORMAT_VERSION"\n'
            f'"1","","{uri}","{uri}","file.xls","Signature","Done","7449867",'
            '"File","xls","2026-11-09T11:59:31","false","","1","fmt/111","",'
            '"OLE2 Compound Document Format",""\n'
        )
        mock_droid_command(
            monkeypatch,
            output,
            stdout=diagnostic,
        )
        with pytest.raises(RuntimeError, match="identification errors"):
            run_droid(uri, uri)
        row = run_droid(uri, uri, allow_partial_identification=True)
        assert row["URI"] == uri
        assert row["STATUS"] == "Done"
        assert row["PUID"] == "fmt/111"
        assert row["FORMAT_NAME"] == "OLE2 Compound Document Format"
        assert row["FORMAT_COUNT"] == "1"
        assert "Accepting partial DROID identification" in caplog.text
        assert "No reader was obtained" in caplog.text

    def test_run_droid_requires_override_for_stderr_fatal_error(
        self, monkeypatch
    ):
        uri = "s3://temp-data-bucket/file.xls"
        mock_droid_command(
            monkeypatch,
            f"ID,URI,STATUS,PUID,FORMAT_NAME\n1,{uri},Done,fmt/111,OLE2\n",
            stderr="2026-11-09T11:59:40,335 FATAL [main] Container reader failed\n",
        )
        with pytest.raises(RuntimeError, match="identification errors"):
            run_droid(uri, uri)
        assert (
            run_droid(uri, uri, allow_partial_identification=True)["PUID"]
            == "fmt/111"
        )

    @pytest.mark.parametrize(
        "output,expected_error",
        [
            ("not CSV\n", "CSV header"),
            ("URI,PUID,FORMAT_NAME\n{uri},fmt/111,OLE2\n", "CSV header"),
            ("ID,URI,PUID,FORMAT_NAME\n1,wrong,fmt/111,OLE2\n", "exactly one"),
            (
                "ID,URI,STATUS,PUID,FORMAT_NAME\n1,{uri},Error,fmt/111,OLE2\n",
                "status",
            ),
            (
                "ID,URI,STATUS,PUID,FORMAT_NAME\n1,{uri},Done,,OLE2\n",
                "identification",
            ),
            (
                "ID,URI,STATUS,PUID,FORMAT_NAME\n1,{uri},Done,   ,OLE2\n",
                "identification",
            ),
            (
                "ID,URI,STATUS,PUID,FORMAT_NAME\n1,{uri},Done,fmt/111,   \n",
                "identification",
            ),
            (
                "ID,URI,PUID,FORMAT_NAME\n1,{uri},fmt/111,OLE2\n",
                "identification",
            ),
            (
                "ID,URI,STATUS,PUID,FORMAT_NAME\n",
                "no CSV rows",
            ),
            (
                "ID,URI,URI,PUID,FORMAT_NAME\n1,{uri},{uri},fmt/111,OLE2\n",
                "CSV header",
            ),
            (
                'ID,URI,STATUS,PUID,FORMAT_NAME\n1,{uri},Done,fmt/111,"unterminated\n',
                "Malformed",
            ),
            (
                "ID,URI,STATUS,PUID,FORMAT_NAME\n1,{uri},Done,fmt/111,OLE2,extra\n",
                "Malformed",
            ),
            (
                "ID,URI,STATUS,PUID,FORMAT_NAME\n"
                "1,{uri},Done,fmt/111,OLE2\n2,{uri},Done,fmt/111,OLE2\n",
                "exactly one",
            ),
        ],
    )
    def test_run_droid_rejects_invalid_results_despite_partial_override(
        self, monkeypatch, output, expected_error
    ):
        uri = "s3://temp-data-bucket/file.xls"
        mock_droid_command(
            monkeypatch,
            output.format(uri=uri),
            stdout="ERROR No reader was obtained\n",
        )
        with pytest.raises(RuntimeError, match=expected_error):
            run_droid(uri, expected_uri=uri, allow_partial_identification=True)

    def test_run_droid_rejects_nonzero_exit_despite_partial_override(
        self, monkeypatch
    ):
        monkeypatch.setattr(
            subprocess,
            "run",
            mock.Mock(
                return_value=mock.Mock(
                    returncode=1,
                    stdout="ERROR container failure",
                    stderr="failed",
                )
            ),
        )
        with pytest.raises(RuntimeError, match="return code 1"):
            run_droid("s3://bucket/file", "s3://bucket/file", True)

    def test_run_droid_preserves_multiline_and_log_like_csv_values(
        self, monkeypatch
    ):
        uri = "s3://temp-data-bucket/file"
        mock_droid_command(
            monkeypatch,
            (
                "ID,URI,STATUS,PUID,FORMAT_NAME\n"
                f'1,{uri},Done,fmt/111,"OLE2\nERROR is metadata here"\n'
            ),
            stdout="2026-11-09T11:59:40,335 INFO [main] Starting DROID\n",
        )
        row = run_droid(uri, uri)
        assert row["PUID"] == "fmt/111"
        assert row["FORMAT_NAME"] == "OLE2\nERROR is metadata here"

    def test_run_droid_checks_diagnostics_separately_from_csv_results(
        self, monkeypatch
    ):
        uri = "s3://temp-data-bucket/file.xls"
        mock_droid_command(
            monkeypatch,
            (
                "ID,URI,STATUS,PUID,FORMAT_NAME\n"
                "1,s3://other/file,Done,fmt/111,OLE2\n"
                f"2,{uri},Done,fmt/111,OLE2\n"
            ),
            stdout='2026-11-09T11:59:40,335 ERROR [main] reader,"failed".\n',
        )
        with pytest.raises(RuntimeError, match="identification errors"):
            run_droid(uri, uri)
        assert run_droid(uri, uri, True)["ID"] == "2"

    def test_run_droid_parses_csv_output(self, monkeypatch):
        source_uri = "s3://temp-data-bucket/_ayr-droid-inputs/run/file.pdf"

        completed_process = mock.Mock()
        completed_process.returncode = 0
        completed_process.stderr = ""
        completed_process.stdout = (
            "ID,URI,EXT,PUID,FORMAT_NAME,EXTENSION_MISMATCH\n"
            "1,s3://temp-data-bucket/_ayr-droid-inputs/run/file.pdf.old,"
            "old,fmt/999,Other,false\n"
            "2,s3://temp-data-bucket/_ayr-droid-inputs/run/file.pdf,"
            "pdf,fmt/18,Acrobat PDF 1.4 - Portable Document Format,false\n"
        )

        subprocess_run_mock = mock_droid_command(
            monkeypatch, completed_process.stdout
        )

        result = run_droid(source_uri, expected_uri=source_uri)

        assert result == {
            "ID": "2",
            "URI": source_uri,
            "EXT": "pdf",
            "PUID": "fmt/18",
            "FORMAT_NAME": "Acrobat PDF 1.4 - Portable Document Format",
            "EXTENSION_MISMATCH": "false",
        }

        subprocess_run_mock.assert_called_once()
        call_args = subprocess_run_mock.call_args

        assert call_args.args[0][:3] == [
            "/opt/droid/droid.sh",
            source_uri,
            "-o",
        ]
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

    def test_run_droid_requires_a_row_for_the_requested_uri(self, monkeypatch):
        source_uri = "s3://temp-data-bucket/_ayr-droid-inputs/run/file.pdf"
        completed_process = mock.Mock()
        completed_process.returncode = 0
        completed_process.stderr = ""
        completed_process.stdout = (
            "ID,URI,EXT,PUID,FORMAT_NAME\n"
            "1,s3://temp-data-bucket/_ayr-droid-inputs/run/file.pdf.old,"
            "old,fmt/999,Other\n"
        )
        mock_droid_command(monkeypatch, completed_process.stdout)

        with pytest.raises(
            RuntimeError,
            match="did not produce exactly one result",
        ):
            run_droid(source_uri, expected_uri=source_uri)

    def test_run_droid_raises_when_droid_fails(
        self,
        monkeypatch,
    ):
        source_uri = "s3://temp-data-bucket/_ayr-droid-inputs/run/file.pdf"

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
            run_droid(source_uri, expected_uri=source_uri)

    def test_run_droid_raises_when_no_csv_rows_returned(
        self,
        monkeypatch,
    ):
        source_uri = "s3://temp-data-bucket/_ayr-droid-inputs/run/file.pdf"

        completed_process = mock.Mock()
        completed_process.returncode = 0
        completed_process.stderr = ""
        completed_process.stdout = "ID,URI,EXT,PUID,FORMAT_NAME\n"

        mock_droid_command(monkeypatch, completed_process.stdout)

        with pytest.raises(RuntimeError, match="DROID produced no CSV rows"):
            run_droid(source_uri, expected_uri=source_uri)

    def test_run_droid_uses_unique_temp_directories_and_cleans_up_on_success(
        self, monkeypatch
    ):
        uri = "s3://temp-data-bucket/file.pdf"
        output_directories = []

        def execute(command, **kwargs):
            output_path = Path(command[command.index("-o") + 1])
            output_directories.append(output_path.parent)
            assert output_path.parent.is_dir()
            assert output_path.parent.parent == Path(tempfile.gettempdir())
            output_path.write_text(
                f"ID,URI,PUID,FORMAT_NAME\n1,{uri},fmt/18,PDF\n",
                encoding="utf-8",
            )
            return subprocess.CompletedProcess(command, 0, "", "")

        monkeypatch.setattr(subprocess, "run", execute)
        run_droid(uri, uri)
        run_droid(uri, uri)

        first_directory, second_directory = output_directories
        assert first_directory != second_directory
        assert not first_directory.exists(), (
            "First run left temporary files behind"
        )
        assert not second_directory.exists(), (
            "Second run left temporary files behind"
        )

    def test_run_droid_cleans_up_temp_directory_on_timeout(self, monkeypatch):
        def execute(command, **kwargs):
            Path(command[3]).write_text("partial output", encoding="utf-8")
            raise subprocess.TimeoutExpired(command, 120)

        run = mock.Mock(side_effect=execute)
        monkeypatch.setattr(subprocess, "run", run)
        with pytest.raises(subprocess.TimeoutExpired):
            run_droid("s3://bucket/file", "s3://bucket/file", True)
        command = run.call_args.args[0]
        output_path = Path(command[command.index("-o") + 1])
        temporary_directory = output_path.parent
        assert not temporary_directory.exists(), (
            "Temporary directory was not removed after timeout"
        )

    def test_run_droid_cleans_up_temp_directory_when_output_is_missing(
        self, monkeypatch
    ):
        run = mock.Mock(return_value=subprocess.CompletedProcess([], 0, "", ""))
        monkeypatch.setattr(subprocess, "run", run)
        with pytest.raises(
            RuntimeError, match="did not create its CSV output file"
        ):
            run_droid("s3://bucket/file", "s3://bucket/file", True)
        output_path = Path(run.call_args.args[0][3])
        assert not output_path.parent.exists(), (
            "Temporary directory was not removed after missing output"
        )

    def test_run_droid_cleans_up_temp_directory_on_nonzero_exit(
        self, monkeypatch
    ):
        run = mock_droid_command(monkeypatch, "partial output", returncode=1)
        with pytest.raises(RuntimeError, match="return code 1"):
            run_droid("s3://bucket/file", "s3://bucket/file", True)
        output_path = Path(run.call_args.args[0][3])
        assert not output_path.parent.exists(), (
            "Temporary directory was not removed after nonzero exit"
        )


@pytest.fixture
def damaged_ole2_uri(monkeypatch):
    """Upload synthetic corruption to the isolated Compose RustFS service."""
    endpoint_url = urlsplit(os.environ["RUSTFS_ENDPOINT_URL"])
    assert endpoint_url.hostname, "RUSTFS_ENDPOINT_URL requires a hostname"
    # An IP endpoint makes DROID's Java SDK use path-style S3 addressing,
    # rather than trying to resolve <random-bucket>.migration-rustfs.
    address = socket.gethostbyname(endpoint_url.hostname)
    endpoint = endpoint_url._replace(
        netloc=f"{address}:{endpoint_url.port or 9000}"
    ).geturl()
    monkeypatch.setenv("AWS_ENDPOINT_URL_S3", endpoint)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "migration-test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "migration-test-secret")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id="migration-test",
        aws_secret_access_key="migration-test-secret",  # pragma: allowlist secret
        region_name="us-east-1",
        config=Config(
            connect_timeout=2,
            read_timeout=2,
            retries={"max_attempts": 0},
            s3={"addressing_style": "path"},
        ),
    )
    bucket = f"droid-integration-{uuid4().hex}"
    key = "damaged.xls"
    client.create_bucket(Bucket=bucket)
    try:
        client.upload_file(
            str(Path(__file__).parent / "fixtures" / "damaged-ole2.xls"),
            bucket,
            key,
        )
        yield f"s3://{bucket}/{key}"
    finally:
        try:
            client.delete_object(Bucket=bucket, Key=key)
        finally:
            client.delete_bucket(Bucket=bucket)
            client.close()


@pytest.fixture
def installed_droid(monkeypatch):
    """Fail rather than skip if the integration-test image lacks DROID."""
    command = Path(droid_module.DROID_COMMAND)
    assert command.is_file(), f"DROID command is not installed at {command}"
    assert os.access(command, os.X_OK), (
        f"DROID command is not executable: {command}"
    )
    monkeypatch.setattr(droid_module, "DROID_TIMEOUT_SECONDS", 60)


@pytest.mark.integration
def test_run_droid_identifies_damaged_ole2_with_installed_droid(
    installed_droid, damaged_ole2_uri, caplog
):
    row = run_droid(
        damaged_ole2_uri,
        expected_uri=damaged_ole2_uri,
        allow_partial_identification=True,
    )
    result = droid_module.map_droid_row_to_ffid_metadata("damaged-file", row)

    assert re.search(
        r"\bERROR\b[^\r\n]*Ole2IdentifierEngine[^\r\n]*No reader was obtained",
        caplog.text,
    ), caplog.text
    assert row["URI"] == damaged_ole2_uri
    assert row["STATUS"] == "Done"
    assert result["FileId"] == "damaged-file"
    assert result["PUID"] == "fmt/111"
    assert result["FormatName"] == "OLE2 Compound Document Format"
    assert result["FFID-SoftwareVersion"] == "6.9.13"


@pytest.mark.integration
def test_run_droid_identifies_local_pdf_with_installed_droid(
    installed_droid, tmp_path
):
    """
    Given a valid local PDF and DROID installed
    When it is identified with the real DROID command
    Then the expected FFID metadata is returned
    """
    file_id = "droid-integration-file"
    local_path = tmp_path / f"{file_id}.pdf"
    pdf_bytes = (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog >>\n"
        b"endobj\n"
        b"trailer\n"
        b"<< /Root 1 0 R >>\n"
        b"%%EOF\n"
    )

    local_path.write_bytes(pdf_bytes)
    droid_row = run_droid(
        str(local_path),
        expected_uri=f"file:{local_path}",
    )
    result = droid_module.map_droid_row_to_ffid_metadata(file_id, droid_row)

    assert local_path.read_bytes() == pdf_bytes
    assert result["FileId"] == file_id
    assert result["Extension"] == "pdf"
    assert result["PUID"] == "fmt/18"
    assert result["FormatName"] == "Acrobat PDF 1.4 - Portable Document Format"
    assert result["ExtensionMismatch"] == "false"
    assert result["FFID-Software"] == "DROID"
    assert result["FFID-SoftwareVersion"] == "6.9.13"
