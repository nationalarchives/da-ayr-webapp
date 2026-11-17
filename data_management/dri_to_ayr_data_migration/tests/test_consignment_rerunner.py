import importlib
import json
import os
import unittest.mock as mock
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import boto3
import pytest
from botocore.exceptions import ClientError
from consignment_rerunner.handler import (
    delete_prefix,
    lambda_handler,
    prepare_consignment_rerun,
    require_text,
    reset_tracking_for_rerun,
)
from moto import mock_aws


@pytest.fixture(autouse=True, scope="module")
def mock_environment_variables():
    with mock.patch.dict(
        os.environ,
        {
            "AWS_DEFAULT_REGION": "eu-west-2",
            "AWS_REGION": "eu-west-2",
            "AWS_EC2_METADATA_DISABLED": "true",
            "AWS_ACCESS_KEY_ID": "test",
            "AWS_SECRET_ACCESS_KEY": "test",  # pragma: allowlist secret
            "DDT_TEMP_CSV_BUCKET": "ddt-temp-csv-bucket",
            "DDT_TEMP_DATA_BUCKET": "ddt-temp-data-bucket",
            "TRACKING_TABLE_NAME": "tracking-table",
            "OUTPUT_PREFIX": "ayr-mds-csv",
            "STAGING_PREFIX": "ayr-mds-staging",
            "WORKER_QUEUE_URL": "https://sqs.eu-west-2.amazonaws.com/123456789012/worker-queue",
        },
    ):
        yield


@pytest.fixture
def completed_consignment(request, monkeypatch):
    with mock_aws():
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
        table = boto3.resource("dynamodb").Table("tracking-table")
        file_count = getattr(request, "param", 2)
        key = {"PK": "RUN#run-1", "SK": "CONSIGNMENT#TDR-1"}
        table.put_item(
            Item={
                **key,
                "series": "MIG 1",
                "status": "SENT_TO_DDT",
                "expectedFileCount": file_count,
                "completedFileCount": file_count,
                "finaliserMessageSentAt": "old-time",
                "finaliserSqsMessageId": "old-message",
                "rerunCount": 3,
            }
        )
        files = [
            {"fileId": f"file-{index:03}", "reference": f"MIG 1/{index}"}
            for index in range(file_count)
        ]
        for file in files:
            table.put_item(
                Item={
                    "PK": "RUN#run-1#CONSIGNMENT#TDR-1",
                    "SK": f"FILE#{file['fileId']}",
                    "entityType": "FILE",
                    **file,
                    "status": "COMPLETE",
                    "completedAt": "old-time",
                }
            )
        sqs = Mock()
        monkeypatch.setattr(
            "consignment_rerunner.handler.boto3.client",
            lambda service: {"dynamodb": db, "sqs": sqs}[service],
        )
        monkeypatch.setattr(
            "consignment_rerunner.handler.prepare_consignment_rerun",
            Mock(return_value={}),
        )
        yield db, table, key, files, sqs


def rerun_event():
    return {
        "runId": "run-1",
        "series": "MIG 1",
        "consignmentReference": "TDR-1",
    }


def rerun_event_as_droid_args():
    return {
        "run_id": "run-1",
        "series": "MIG 1",
        "consignment_reference": "TDR-1",
    }


def reset_args(db, files):
    return {
        **rerun_event_as_droid_args(),
        "reason": "Manual rerun",
        "triggered_by": "unknown",
        "files": files,
        "tracking_table_name": "tracking-table",
        "dynamodb": db,
    }


class TestLambdaHandler:
    @pytest.mark.parametrize("completed_consignment", [1, 100], indirect=True)
    def test_rerun_rejects_wrong_series_without_changing_tracking(
        self, completed_consignment
    ):
        """Given a tracked consignment, when the requested series differs,
        then tracking is unchanged and no cleanup or dispatch occurs.
        """
        _, table, key, files, sqs = completed_consignment
        before = table.get_item(Key=key)["Item"]

        with patch(
            "consignment_rerunner.handler.prepare_consignment_rerun"
        ) as cleanup:
            with pytest.raises(
                ValueError, match="does not match tracked series"
            ):
                lambda_handler({**rerun_event(), "series": "WRONG SERIES"}, {})
            cleanup.assert_not_called()

        assert table.get_item(Key=key)["Item"] == before
        for file in files:
            item = table.get_item(
                Key={
                    "PK": "RUN#run-1#CONSIGNMENT#TDR-1",
                    "SK": f"FILE#{file['fileId']}",
                }
            )["Item"]
            assert item["status"] == "COMPLETE"
        sqs.send_message.assert_not_called()

    def test_partial_dispatch_can_restart_from_scratch_after_quiescence(
        self, completed_consignment
    ):
        """Given a dispatch failure after one message and subsequent completion,
        when the quiescent consignment is rerun, then all files are reset and
        queued again.
        """
        _, table, key, files, sqs = completed_consignment
        sqs.send_message.side_effect = [
            {"MessageId": "first"},
            RuntimeError("queue unavailable"),
        ]
        with pytest.raises(RuntimeError, match="queue unavailable"):
            lambda_handler(rerun_event(), {})

        file_key = {
            "PK": "RUN#run-1#CONSIGNMENT#TDR-1",
            "SK": f"FILE#{files[0]['fileId']}",
        }
        table.update_item(
            Key=file_key,
            UpdateExpression="SET #status = :complete, completedAt = :now",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":complete": "COMPLETE",
                ":now": "completed-after-dispatch",
            },
        )
        table.update_item(
            Key=key,
            UpdateExpression="SET completedFileCount = :one",
            ExpressionAttributeValues={":one": 1},
        )
        sqs.send_message.reset_mock(side_effect=True)
        with patch(
            "consignment_rerunner.handler.prepare_consignment_rerun"
        ) as cleanup:
            cleanup.return_value = {}
            result = lambda_handler(rerun_event(), {})
        cleanup.assert_called_once()
        assert result["filesQueued"] == 2
        item = table.get_item(Key=key)["Item"]
        assert item["completedFileCount"] == 0
        assert item["rerunCount"] == 5
        assert table.get_item(Key=file_key)["Item"]["status"] == "PENDING"
        assert "completedAt" not in table.get_item(Key=file_key)["Item"]
        assert all(
            "forceRerun" not in json.loads(call.kwargs["MessageBody"])
            for call in sqs.send_message.call_args_list
        )

    def test_failed_cleanup_can_restart_from_scratch(
        self, completed_consignment
    ):
        """Given cleanup fails after a reset, when the rerun is retried,
        then cleanup is repeated and all files are queued.
        """
        _, table, key, _, sqs = completed_consignment
        cleanup = Mock(
            side_effect=[
                RuntimeError("cleanup failed"),
                {"deletedStagingObjects": 1, "deletedOutputObjects": 1},
            ]
        )
        with patch(
            "consignment_rerunner.handler.prepare_consignment_rerun", cleanup
        ):
            with pytest.raises(RuntimeError, match="cleanup failed"):
                lambda_handler(rerun_event(), {})
            sqs.send_message.assert_not_called()
            lambda_handler(rerun_event(), {})

        assert table.get_item(Key=key)["Item"]["rerunCount"] == 5
        assert cleanup.call_count == 2
        assert sqs.send_message.call_count == 2

    def test_rerun_rejects_finalising_consignment(self, completed_consignment):
        """Given a finalising consignment, when a rerun is requested,
        then the reset fails and no workers are queued.
        """
        _, table, key, _, sqs = completed_consignment
        table.update_item(
            Key=key,
            UpdateExpression="SET #status = :finalising",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":finalising": "FINALISING"},
        )
        with pytest.raises(ClientError, match="TransactionCanceledException"):
            lambda_handler(rerun_event(), {})
        sqs.send_message.assert_not_called()

    def test_partial_s3_delete_failure_stops_before_worker_dispatch(
        self, completed_consignment, monkeypatch
    ):
        """Given S3 reports a failed deletion, when the rerunner cleans up,
        then it raises and does not queue workers.
        """
        db, _, _, _, sqs = completed_consignment
        s3 = Mock()
        s3.get_paginator.return_value.paginate.return_value = [
            {"Contents": [{"Key": "MIG 1/ayr-mds-staging/TDR-1/file.csv"}]}
        ]
        s3.delete_objects.return_value = {
            "Errors": [
                {
                    "Key": "MIG 1/ayr-mds-staging/TDR-1/file.csv",
                    "Code": "AccessDenied",
                    "Message": "Deletion denied",
                }
            ]
        }
        monkeypatch.setattr(
            "consignment_rerunner.handler.boto3.client",
            lambda service: {"dynamodb": db, "sqs": sqs, "s3": s3}[service],
        )
        # Restore the real cleanup function, which the fixture replaces.
        monkeypatch.setattr(
            "consignment_rerunner.handler.prepare_consignment_rerun",
            prepare_consignment_rerun,
        )
        with pytest.raises(RuntimeError, match="AccessDenied"):
            lambda_handler(rerun_event(), {})
        sqs.send_message.assert_not_called()

    def test_rerun_allows_new_droid_completion(
        self, completed_consignment, monkeypatch
    ):
        """Given a sent consignment, when it is rerun and DROID completes its
        files, then tracking is reset before dispatch and a finaliser is queued
        once, even if a completion is repeated.
        """
        db, table, key, files, sqs = completed_consignment

        def verify_reset_before_queueing(**kwargs):
            sqs.send_message.side_effect = None
            item = table.get_item(Key=key)["Item"]
            assert item["status"] == "STAGING"
            assert item["completedFileCount"] == 0
            assert "finaliserMessageSentAt" not in item
            assert "finaliserSqsMessageId" not in item
            for file in files:
                item = table.get_item(
                    Key={
                        "PK": "RUN#run-1#CONSIGNMENT#TDR-1",
                        "SK": f"FILE#{file['fileId']}",
                    }
                )["Item"]
                assert item["status"] == "PENDING"
                assert "completedAt" not in item

        sqs.send_message.side_effect = verify_reset_before_queueing
        result = lambda_handler(rerun_event(), {})
        assert result["filesQueued"] == len(files)
        assert sqs.send_message.call_count == len(files)
        payloads = [
            json.loads(call.kwargs["MessageBody"])
            for call in sqs.send_message.call_args_list
        ]
        assert {payload["fileId"] for payload in payloads} == {
            file["fileId"] for file in files
        }
        assert all("forceRerun" not in payload for payload in payloads)
        assert sum(payload["includeConsignment"] for payload in payloads) == 1
        assert not any(payload["includeBodyAndSeries"] for payload in payloads)
        assert table.get_item(Key=key)["Item"]["rerunCount"] == 4

        monkeypatch.setenv("DROID_COMMAND", "/opt/droid/droid.sh")
        monkeypatch.setenv("DROID_VERSION", "6.9.13")
        monkeypatch.setenv("FINALISER_QUEUE_URL", "finaliser-queue")
        # Import-time clients must also be mocked when this test runs alone.
        with patch("boto3.client", return_value=Mock()):
            droid = importlib.import_module("droid.handler")
        monkeypatch.setattr(droid, "dynamodb", db)
        monkeypatch.setattr(droid, "TRACKING_TABLE_NAME", "tracking-table")
        finaliser_queue = Mock()
        finaliser_queue.send_message.return_value = {"MessageId": "new-message"}
        monkeypatch.setattr(droid, "sqs", finaliser_queue)
        monkeypatch.setattr(droid, "ensure_required_staged_csvs_exist", Mock())

        for index, file in enumerate(files):
            triggered = droid.mark_file_complete_and_trigger_finaliser_if_consignment_ready(
                **rerun_event_as_droid_args(), file_id=file["fileId"]
            )
            assert triggered is (index == len(files) - 1)

        item = table.get_item(Key=key)["Item"]
        assert item["status"] == "READY_TO_FINALISE"
        assert item["completedFileCount"] == len(files)
        assert item["finaliserSqsMessageId"] == "new-message"
        finaliser_queue.send_message.assert_called_once()

        assert not droid.mark_file_complete_and_trigger_finaliser_if_consignment_ready(
            **rerun_event_as_droid_args(), file_id=files[0]["fileId"]
        )
        assert table.get_item(Key=key)["Item"]["completedFileCount"] == len(
            files
        )
        finaliser_queue.send_message.assert_called_once()

    def test_failed_reset_is_atomic_and_queues_nothing(
        self, completed_consignment, monkeypatch
    ):
        """Given a file disappears after discovery, when the reset is attempted,
        then the transaction leaves tracking unchanged and queues no workers.
        """
        _, table, key, files, sqs = completed_consignment
        table.delete_item(
            Key={
                "PK": "RUN#run-1#CONSIGNMENT#TDR-1",
                "SK": f"FILE#{files[-1]['fileId']}",
            }
        )
        monkeypatch.setattr(
            "consignment_rerunner.handler.get_files", Mock(return_value=files)
        )
        before = table.get_item(Key=key)["Item"]

        with pytest.raises(ClientError, match="TransactionCanceledException"):
            lambda_handler(rerun_event(), {})

        assert table.get_item(Key=key)["Item"] == before
        file = table.get_item(
            Key={
                "PK": "RUN#run-1#CONSIGNMENT#TDR-1",
                "SK": f"FILE#{files[0]['fileId']}",
            }
        )["Item"]
        assert file["status"] == "COMPLETE"
        assert file["completedAt"] == "old-time"
        sqs.send_message.assert_not_called()

    @mock_aws
    @patch("consignment_rerunner.handler.datetime")
    def test_handler_does_as_expected(self, datetime_mock):
        """Given a sent consignment with staged and output objects, when the
        handler runs, then it resets tracking, deletes only its objects, and
        queues its files.
        """
        datetime_mock.now = Mock(
            return_value=datetime.strptime("Jun 1 2005", "%b %d %Y")
        )

        event = {
            "runId": "test-run-id",
            "series": "Test Series",
            "consignmentReference": "test-consignment-reference",
        }

        context = {}

        sqs = boto3.client("sqs", region_name="eu-west-2")
        sqs.create_queue(QueueName="worker-queue")
        s3 = boto3.client("s3", region_name="eu-west-2")
        s3.create_bucket(
            Bucket="ddt-temp-csv-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        s3.put_object(
            Bucket="ddt-temp-csv-bucket",
            Key="Test Series/ayr-mds-staging/test-consignment-reference/test-file.csv",
            Body="test content",
        )
        s3.put_object(
            Bucket="ddt-temp-csv-bucket",
            Key="Test Series/ayr-mds-csv/test-consignment-reference/test-file.csv",
            Body="test content",
        )
        s3.put_object(
            Bucket="ddt-temp-csv-bucket",
            Key="Test Series/ayr-mds-staging/shared/AYR-series-metadata.csv",
            Body="test content",
        )
        s3.put_object(
            Bucket="ddt-temp-csv-bucket",
            Key="Test Series/ayr-mds-staging/shared/AYR-body-metadata.csv",
            Body="test content",
        )
        s3.put_object(
            Bucket="ddt-temp-csv-bucket",
            Key="Test Series/ayr-mds-staging/other-consignment/test-file.csv",
            Body="test content",
        )

        dynamo_db = boto3.resource("dynamodb", region_name="eu-west-2")
        dynamo_db.create_table(
            TableName="tracking-table",
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5,
            },
        )

        dynamo_db.Table("tracking-table").put_item(
            Item={
                "PK": "RUN#test-run-id",
                "SK": "CONSIGNMENT#test-consignment-reference",
                "entityType": "CONSIGNMENT",
                "series": "Test Series",
                "status": "SENT_TO_DDT",
                "expectedFileCount": 2,
                "completedFileCount": 2,
                "finaliserMessageSentAt": "2005-05-01T00:00:00Z",
                "finaliserSqsMessageId": "old-message",
                "readyAt": "2005-05-01T00:00:00Z",
                "finalisingStartedAt": "2005-05-01T00:00:00Z",
                "sentToDdtAt": "2005-05-01T00:00:00Z",
                "ddtSnsMessageId": "old-publication",
            }
        )

        dynamo_db.Table("tracking-table").put_item(
            Item={
                "PK": "RUN#test-run-id#CONSIGNMENT#test-consignment-reference",
                "SK": "FILE#file1",
                "entityType": "FILE",
                "reference": "TEST/1",
                "fileId": "file1",
                "status": "COMPLETE",
                "completedAt": "2005-05-01T00:00:00Z",
            }
        )

        dynamo_db.Table("tracking-table").put_item(
            Item={
                "PK": "RUN#test-run-id#CONSIGNMENT#test-consignment-reference",
                "SK": "FILE#file2",
                "entityType": "FILE",
                "reference": "TEST/2",
                "fileId": "file2",
                "status": "COMPLETE",
                "completedAt": "2005-05-01T00:00:00Z",
            }
        )

        result = lambda_handler(event, context)

        sqs_messages = sqs.receive_message(QueueUrl="worker-queue")["Messages"]
        assert len(sqs_messages) == 1
        sqs_message = sqs_messages[0]
        assert (
            sqs_message["Body"]
            == '{"runId": "test-run-id", "series": "Test Series", "reference": "TEST/1", "consignmentReference": "test-consignment-reference", "fileId": "file1", "includeBodyAndSeries": false, "includeConsignment": true}'
        )

        s3_objects = s3.list_objects_v2(Bucket="ddt-temp-csv-bucket")[
            "Contents"
        ]
        assert len(s3_objects) == 3
        assert all(
            not obj["Key"].startswith(
                "Test Series/ayr-mds-staging/test-consignment-reference/"
            )
            for obj in s3_objects
        )
        assert all(
            not obj["Key"].startswith(
                "Test Series/ayr-mds-csv/test-consignment-reference/"
            )
            for obj in s3_objects
        )

        assert dynamo_db.Table("tracking-table").get_item(
            Key={
                "PK": "RUN#test-run-id",
                "SK": "CONSIGNMENT#test-consignment-reference",
            }
        )["Item"] == {
            "PK": "RUN#test-run-id",
            "SK": "CONSIGNMENT#test-consignment-reference",
            "entityType": "CONSIGNMENT",
            "series": "Test Series",
            "status": "STAGING",
            "expectedFileCount": Decimal("2"),
            "completedFileCount": Decimal("0"),
            "lastRerunAt": "2005-06-01T00:00:00Z",
            "lastRerunReason": "Manual rerun",
            "lastRerunTriggeredBy": "unknown",
            "lastRerunFileCount": Decimal("2"),
            "rerunType": "WORKER_REPROCESS",
            "updatedAt": "2005-06-01T00:00:00Z",
            "rerunCount": Decimal("1"),
        }

        for file_id in ("file1", "file2"):
            item = dynamo_db.Table("tracking-table").get_item(
                Key={
                    "PK": "RUN#test-run-id#CONSIGNMENT#test-consignment-reference",
                    "SK": f"FILE#{file_id}",
                }
            )["Item"]
            assert item["status"] == "PENDING"
            assert "completedAt" not in item

        assert result == {
            "consignmentReference": "test-consignment-reference",
            "filesQueued": 2,
            "deletedStagingObjects": 1,
            "deletedOutputObjects": 1,
        }

    def test_handler_raises_for_missing_run_id(self):
        """Given an event without a run ID, when the handler runs,
        then it raises a validation error.
        """
        event = {
            "series": "test-series",
            "consignmentReference": "test-consignment-reference",
        }

        with pytest.raises(ValueError, match="Missing required field: runId"):
            lambda_handler(event, {})


class TestRequireText:
    @pytest.mark.parametrize(
        "data", [{}, {"series": ""}, {"series": "  "}, {"series": None}]
    )
    def test_require_text_rejects_missing_or_invalid_values(self, data):
        """Given a missing or blank series, when text is required,
        then validation raises an error.
        """
        with pytest.raises(ValueError, match="Missing required field: series"):
            require_text(data, "series")

    def test_require_text_trims_valid_value(self):
        """Given a series with surrounding whitespace, when text is required,
        then the trimmed value is returned.
        """
        assert require_text({"series": " MIG 1 "}, "series") == "MIG 1"


class TestDeletePrefix:
    def test_delete_prefix_raises_on_partial_failure(self):
        """Given S3 reports a per-object deletion failure, when a prefix is
        deleted, then the error identifies the failed object.
        """
        s3 = Mock()
        s3.get_paginator.return_value.paginate.return_value = [
            {"Contents": [{"Key": "staging/file.csv"}]}
        ]
        s3.delete_objects.return_value = {
            "Errors": [
                {
                    "Key": "staging/file.csv",
                    "Code": "AccessDenied",
                    "Message": "Deletion denied",
                }
            ]
        }

        with pytest.raises(
            RuntimeError, match="staging/file.csv: AccessDenied Deletion denied"
        ):
            delete_prefix(s3=s3, bucket="test-bucket", prefix="staging")

        s3.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket="test-bucket", Prefix="staging/"
        )
        s3.delete_objects.assert_called_once_with(
            Bucket="test-bucket",
            Delete={"Objects": [{"Key": "staging/file.csv"}]},
        )


class TestResetTrackingForRerun:
    @pytest.mark.parametrize(
        "completed_consignment", [1, 99, 100, 201], indirect=True
    )
    def test_reset_tracking_for_rerun_at_transaction_boundaries(
        self, completed_consignment
    ):
        """Given completed consignments of different sizes, when tracking is
        reset, then all files are pending and transactions fit the action limit.
        """
        db, table, key, files, _ = completed_consignment

        with patch.object(
            db, "transact_write_items", wraps=db.transact_write_items
        ) as transaction:
            reset_tracking_for_rerun(**reset_args(db, files))

        item = table.get_item(Key=key)["Item"]
        assert item["status"] == "STAGING"
        assert item["completedFileCount"] == 0
        assert item["rerunCount"] == 4
        assert "finaliserMessageSentAt" not in item
        assert "finaliserSqsMessageId" not in item
        for file in files:
            item = table.get_item(
                Key={
                    "PK": "RUN#run-1#CONSIGNMENT#TDR-1",
                    "SK": f"FILE#{file['fileId']}",
                }
            )["Item"]
            assert item["status"] == "PENDING"
            assert "completedAt" not in item

        transaction_sizes = [
            len(call.kwargs["TransactItems"])
            for call in transaction.call_args_list
        ]
        assert transaction_sizes == [
            min(99, len(files) - offset) + 1
            for offset in range(0, len(files), 99)
        ]

    def test_reset_tracking_is_atomic_when_a_file_is_missing(
        self, completed_consignment
    ):
        """Given a missing file in a single-transaction reset, when the reset
        is attempted, then the consignment and remaining file stay unchanged.
        """
        db, table, key, files, _ = completed_consignment
        table.delete_item(
            Key={
                "PK": "RUN#run-1#CONSIGNMENT#TDR-1",
                "SK": f"FILE#{files[-1]['fileId']}",
            }
        )
        before = table.get_item(Key=key)["Item"]

        with pytest.raises(ClientError, match="TransactionCanceledException"):
            reset_tracking_for_rerun(**reset_args(db, files))

        assert table.get_item(Key=key)["Item"] == before
        item = table.get_item(
            Key={
                "PK": "RUN#run-1#CONSIGNMENT#TDR-1",
                "SK": f"FILE#{files[0]['fileId']}",
            }
        )["Item"]
        assert item["status"] == "COMPLETE"
        assert item["completedAt"] == "old-time"

    @pytest.mark.parametrize("completed_consignment", [101], indirect=True)
    def test_failed_large_reset_blocks_completion_and_can_be_retried(
        self, completed_consignment
    ):
        """Given a large reset fails after its first batch, when it is retried,
        then the consignment leaves RERUN_PREPARING with every file pending.
        """
        db, table, key, files, _ = completed_consignment
        transact_write = db.transact_write_items
        failure = ClientError(
            {"Error": {"Code": "TransactionCanceledException"}},
            "TransactWriteItems",
        )

        def complete_first_transaction(**kwargs):
            transaction.side_effect = failure
            return transact_write(**kwargs)

        with patch.object(
            db, "transact_write_items", side_effect=complete_first_transaction
        ) as transaction:
            with pytest.raises(
                ClientError, match="TransactionCanceledException"
            ):
                reset_tracking_for_rerun(**reset_args(db, files))

        item = table.get_item(Key=key)["Item"]
        assert item["status"] == "RERUN_PREPARING"
        assert item["rerunCount"] == 3
        reset_tracking_for_rerun(**reset_args(db, files))
        item = table.get_item(Key=key)["Item"]
        assert item["status"] == "STAGING"
        assert item["completedFileCount"] == 0
        assert item["rerunCount"] == 4
        for file in files:
            item = table.get_item(
                Key={
                    "PK": "RUN#run-1#CONSIGNMENT#TDR-1",
                    "SK": f"FILE#{file['fileId']}",
                }
            )["Item"]
            assert item["status"] == "PENDING"
            assert "completedAt" not in item
