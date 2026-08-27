import json
import os
from typing import Any
from unittest import mock

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")

os.environ.setdefault("DRI_JSON_BUCKET", "dri-json-bucket")
os.environ.setdefault("WORKER_QUEUE_URL", "worker-queue-url")
os.environ.setdefault("TRACKING_TABLE_NAME", "tracking-table")
os.environ.setdefault("MAX_FILES_PER_FAKE_CONSIGNMENT", "3")


import series_coordinator.handler as coordinator_module
from series_coordinator.handler import (
    get_consignment_tracking_item,
    get_file_tracking_item,
    group_records_by_consignment,
    process_consignment_group,
    process_record,
    put_consignment_tracking_item,
    put_file_tracking_item,
    resolve_run_id,
    series_has_existing_run,
)


@pytest.fixture
def coordinator(monkeypatch):
    monkeypatch.setattr(coordinator_module, "s3", mock.Mock())
    monkeypatch.setattr(coordinator_module, "sqs", mock.Mock())
    monkeypatch.setattr(coordinator_module, "dynamodb", mock.Mock())

    # Keep fake consignment references stable in tests.
    monkeypatch.setattr(
        coordinator_module,
        "DEFAULT_DUMMY_CONSIGNMENT_PREFIX",
        "DRI-TO-AYR-2026",
    )

    return coordinator_module


def record(
    reference: str,
    file_id: str,
    tdr_consignment_id: str | None = None,
) -> dict[str, Any]:
    data = {
        "reference": reference,
        "digitalFiles": [
            {
                "fileId": file_id,
            }
        ],
    }

    if tdr_consignment_id:
        data["tdrConsignmentId"] = tdr_consignment_id

    return data


def create_bucket(s3_client, bucket_name: str) -> None:
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
    )


def create_tracking_table(dynamodb_client, table_name: str) -> None:
    dynamodb_client.create_table(
        TableName=table_name,
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


def put_json_record(
    s3_client, bucket_name: str, key: str, data: dict[str, Any]
) -> None:
    s3_client.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(data).encode("utf-8"),
    )


def get_tracking_item(dynamodb_client, table_name: str, pk: str, sk: str):
    return dynamodb_client.get_item(
        TableName=table_name,
        Key={
            "PK": {"S": pk},
            "SK": {"S": sk},
        },
    ).get("Item")


def read_sqs_messages(sqs_client, queue_url: str) -> list[dict[str, Any]]:
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=0,
    )

    return [
        json.loads(message["Body"]) for message in response.get("Messages", [])
    ]


def patch_moto_clients(monkeypatch, queue_url: str) -> tuple[Any, Any, Any]:
    s3_client = boto3.client("s3", region_name="eu-west-2")
    sqs_client = boto3.client("sqs", region_name="eu-west-2")
    dynamodb_client = boto3.client("dynamodb", region_name="eu-west-2")

    monkeypatch.setattr(coordinator_module, "s3", s3_client)
    monkeypatch.setattr(coordinator_module, "sqs", sqs_client)
    monkeypatch.setattr(coordinator_module, "dynamodb", dynamodb_client)
    monkeypatch.setattr(coordinator_module, "WORKER_QUEUE_URL", queue_url)
    monkeypatch.setattr(
        coordinator_module,
        "DEFAULT_DUMMY_CONSIGNMENT_PREFIX",
        "DRI-TO-AYR-2026",
    )

    return s3_client, sqs_client, dynamodb_client


class TestLambdaHandler:
    """High-level coordinator handler tests"""

    @mock_aws
    def test_lambda_handler_creates_tracking_rows_and_worker_messages(
        self,
        monkeypatch,
    ):
        sqs_client = boto3.client("sqs", region_name="eu-west-2")
        queue_url = sqs_client.create_queue(QueueName="worker-queue")[
            "QueueUrl"
        ]
        s3_client, sqs_client, dynamodb_client = patch_moto_clients(
            monkeypatch,
            queue_url,
        )

        create_bucket(s3_client, "dri-json-bucket")
        create_tracking_table(dynamodb_client, "tracking-table")

        put_json_record(
            s3_client,
            "dri-json-bucket",
            "live/MIG 1-002.json",
            record("MIG 1/002", "file-2", "TDR-1"),
        )
        put_json_record(
            s3_client,
            "dri-json-bucket",
            "live/MIG 1-001.json",
            record("MIG 1/001", "file-1", "TDR-1"),
        )

        response = coordinator_module.lambda_handler(
            {
                "series": "MIG 1",
                "runId": "run-1",
            },
            None,
        )

        assert response["status"] == "started"
        assert response["runId"] == "run-1"
        assert response["series"] == "MIG 1"
        assert response["recordCount"] == 2
        assert response["consignmentCount"] == 1
        assert response["workerMessagesSent"] == 2

        consignment_item = get_tracking_item(
            dynamodb_client,
            "tracking-table",
            "RUN#run-1",
            "CONSIGNMENT#TDR-1",
        )
        assert consignment_item["status"] == {"S": "STAGING"}
        assert consignment_item["expectedFileCount"] == {"N": "2"}

        file_1_item = get_tracking_item(
            dynamodb_client,
            "tracking-table",
            "RUN#run-1#CONSIGNMENT#TDR-1",
            "FILE#file-1",
        )
        file_2_item = get_tracking_item(
            dynamodb_client,
            "tracking-table",
            "RUN#run-1#CONSIGNMENT#TDR-1",
            "FILE#file-2",
        )
        assert file_1_item["status"] == {"S": "PENDING"}
        assert file_2_item["status"] == {"S": "PENDING"}

        messages = sorted(
            read_sqs_messages(sqs_client, queue_url),
            key=lambda message: message["reference"],
        )
        assert messages == [
            {
                "runId": "run-1",
                "series": "MIG 1",
                "reference": "MIG 1/001",
                "consignmentReference": "TDR-1",
                "fileId": "file-1",
            },
            {
                "runId": "run-1",
                "series": "MIG 1",
                "reference": "MIG 1/002",
                "consignmentReference": "TDR-1",
                "fileId": "file-2",
            },
        ]

    @mock_aws
    def test_lambda_handler_skips_terminal_consignment(self, monkeypatch):
        sqs_client = boto3.client("sqs", region_name="eu-west-2")
        queue_url = sqs_client.create_queue(QueueName="worker-queue")[
            "QueueUrl"
        ]
        s3_client, sqs_client, dynamodb_client = patch_moto_clients(
            monkeypatch,
            queue_url,
        )

        create_bucket(s3_client, "dri-json-bucket")
        create_tracking_table(dynamodb_client, "tracking-table")

        put_json_record(
            s3_client,
            "dri-json-bucket",
            "live/MIG 1-001.json",
            record("MIG 1/001", "file-1", "TDR-1"),
        )

        dynamodb_client.put_item(
            TableName="tracking-table",
            Item={
                "PK": {"S": "RUN#run-1"},
                "SK": {"S": "CONSIGNMENT#TDR-1"},
                "entityType": {"S": "CONSIGNMENT"},
                "runId": {"S": "run-1"},
                "series": {"S": "MIG 1"},
                "consignmentReference": {"S": "TDR-1"},
                "expectedFileCount": {"N": "1"},
                "completedFileCount": {"N": "1"},
                "failedFileCount": {"N": "0"},
                "status": {"S": "SENT_TO_DDT"},
                "createdAt": {"S": "2026-08-25T10:00:00Z"},
                "updatedAt": {"S": "2026-08-25T10:00:00Z"},
            },
        )

        response = coordinator_module.lambda_handler(
            {
                "series": "MIG 1",
                "runId": "run-1",
            },
            None,
        )

        assert response["status"] == "started"
        assert response["workerMessagesSent"] == 0
        assert response["consignmentsSkipped"] == [
            {
                "consignmentReference": "TDR-1",
                "status": "SENT_TO_DDT",
            }
        ]
        assert read_sqs_messages(sqs_client, queue_url) == []


class TestConsignmentGrouping:
    """Consignment grouping tests"""

    def test_groups_records_by_real_consignment_reference(self, coordinator):
        records = [
            record("MIG 1/002", "file-2", "TDR-1"),
            record("MIG 1/001", "file-1", "TDR-1"),
            record("MIG 1/003", "file-3", "TDR-2"),
        ]

        result = group_records_by_consignment(records, "MIG 1")

        assert list(result.keys()) == ["TDR-1", "TDR-2"]
        assert [item["reference"] for item in result["TDR-1"]] == [
            "MIG 1/001",
            "MIG 1/002",
        ]
        assert [item["reference"] for item in result["TDR-2"]] == [
            "MIG 1/003",
        ]

    def test_groups_missing_tdr_consignment_id_into_fake_consignment(
        self,
        coordinator,
    ):
        records = [
            record("MIG 3/003", "file-3"),
            record("MIG 3/001", "file-1"),
            record("MIG 3/002", "file-2"),
        ]

        result = group_records_by_consignment(records, "MIG 3")

        assert list(result.keys()) == [
            "DRI-TO-AYR-2026-MIG-3-0001",
        ]
        assert [
            item["reference"] for item in result["DRI-TO-AYR-2026-MIG-3-0001"]
        ] == [
            "MIG 3/001",
            "MIG 3/002",
            "MIG 3/003",
        ]

    def test_chunks_fake_consignments_by_record_count(self, coordinator):
        records = [
            record("MIG 3/001", "file-1"),
            record("MIG 3/002", "file-2"),
            record("MIG 3/003", "file-3"),
            record("MIG 3/004", "file-4"),
        ]

        result = group_records_by_consignment(records, "MIG 3")

        assert list(result.keys()) == [
            "DRI-TO-AYR-2026-MIG-3-0001",
            "DRI-TO-AYR-2026-MIG-3-0002",
        ]
        assert [
            item["reference"] for item in result["DRI-TO-AYR-2026-MIG-3-0001"]
        ] == [
            "MIG 3/001",
            "MIG 3/002",
            "MIG 3/003",
        ]
        assert [
            item["reference"] for item in result["DRI-TO-AYR-2026-MIG-3-0002"]
        ] == [
            "MIG 3/004",
        ]


class TestRunResolution:
    """Run ID resolution tests"""

    def test_series_has_existing_run_returns_true_when_tracking_row_exists(
        self,
        coordinator,
    ):
        paginator = mock.Mock()
        paginator.paginate.return_value = [
            {"Items": []},
            {"Items": [{"runId": {"S": "existing-run-id"}}]},
        ]

        coordinator.dynamodb.get_paginator.return_value = paginator

        result = series_has_existing_run("MIG 1")

        assert result is True
        coordinator.dynamodb.get_paginator.assert_called_once_with("scan")

        paginate_kwargs = paginator.paginate.call_args.kwargs
        assert paginate_kwargs["TableName"] == "tracking-table"
        assert paginate_kwargs["ExpressionAttributeValues"] == {
            ":series": {"S": "MIG 1"},
        }

    def test_series_has_existing_run_returns_false_when_no_tracking_rows_exist(
        self,
        coordinator,
    ):
        paginator = mock.Mock()
        paginator.paginate.return_value = [
            {"Items": []},
            {"Items": []},
        ]

        coordinator.dynamodb.get_paginator.return_value = paginator

        result = series_has_existing_run("MIG 1")

        assert result is False
        coordinator.dynamodb.get_paginator.assert_called_once_with("scan")

    def test_resolve_run_id_returns_supplied_run_id(
        self, coordinator, monkeypatch
    ):
        existing_run_mock = mock.Mock(
            side_effect=AssertionError(
                "series_has_existing_run should not be called"
            )
        )

        monkeypatch.setattr(
            coordinator_module,
            "series_has_existing_run",
            existing_run_mock,
        )

        result = resolve_run_id(
            {
                "series": "MIG 1",
                "runId": " existing-run-id ",
            },
            "MIG 1",
        )

        assert result == "existing-run-id"
        existing_run_mock.assert_not_called()

    def test_resolve_run_id_blocks_new_run_when_series_already_exists(
        self,
        coordinator,
        monkeypatch,
    ):
        monkeypatch.setattr(
            coordinator_module,
            "series_has_existing_run",
            lambda series: True,
        )

        with pytest.raises(ValueError, match="Existing migration run found"):
            resolve_run_id(
                {
                    "series": "MIG 1",
                },
                "MIG 1",
            )

    def test_resolve_run_id_allows_force_new_run(
        self, coordinator, monkeypatch
    ):
        monkeypatch.setattr(
            coordinator_module,
            "series_has_existing_run",
            lambda series: True,
        )
        monkeypatch.setattr(
            coordinator_module,
            "build_run_id",
            lambda series: "new-run-id",
        )

        result = resolve_run_id(
            {
                "series": "MIG 1",
                "forceNewRun": True,
            },
            "MIG 1",
        )

        assert result == "new-run-id"


class TestDynamoDbTracking:
    """DynamoDB tracking item tests"""

    def test_get_consignment_tracking_item_uses_expected_keys(
        self, coordinator
    ):
        coordinator.dynamodb.get_item.return_value = {
            "Item": {
                "status": {"S": "STAGING"},
            }
        }

        result = get_consignment_tracking_item(
            run_id="run-1",
            consignment_reference="TDR-1",
        )

        assert result == {
            "status": {"S": "STAGING"},
        }
        coordinator.dynamodb.get_item.assert_called_once_with(
            TableName="tracking-table",
            Key={
                "PK": {"S": "RUN#run-1"},
                "SK": {"S": "CONSIGNMENT#TDR-1"},
            },
        )

    def test_get_file_tracking_item_uses_expected_keys(self, coordinator):
        coordinator.dynamodb.get_item.return_value = {
            "Item": {
                "status": {"S": "PENDING"},
            }
        }

        result = get_file_tracking_item(
            run_id="run-1",
            consignment_reference="TDR-1",
            file_id="file-1",
        )

        assert result == {
            "status": {"S": "PENDING"},
        }
        coordinator.dynamodb.get_item.assert_called_once_with(
            TableName="tracking-table",
            Key={
                "PK": {"S": "RUN#run-1#CONSIGNMENT#TDR-1"},
                "SK": {"S": "FILE#file-1"},
            },
        )

    def test_put_consignment_tracking_item_writes_expected_item(
        self,
        coordinator,
        monkeypatch,
    ):
        monkeypatch.setattr(
            coordinator_module,
            "utc_now_text",
            lambda: "2026-08-25T10:00:00Z",
        )

        put_consignment_tracking_item(
            run_id="run-1",
            series="MIG 1",
            consignment_reference="TDR-1",
            expected_file_count=2,
        )

        coordinator.dynamodb.put_item.assert_called_once_with(
            TableName="tracking-table",
            ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
            Item={
                "PK": {"S": "RUN#run-1"},
                "SK": {"S": "CONSIGNMENT#TDR-1"},
                "entityType": {"S": "CONSIGNMENT"},
                "runId": {"S": "run-1"},
                "series": {"S": "MIG 1"},
                "consignmentReference": {"S": "TDR-1"},
                "expectedFileCount": {"N": "2"},
                "completedFileCount": {"N": "0"},
                "failedFileCount": {"N": "0"},
                "status": {"S": "STAGING"},
                "createdAt": {"S": "2026-08-25T10:00:00Z"},
                "updatedAt": {"S": "2026-08-25T10:00:00Z"},
            },
        )

    def test_put_file_tracking_item_writes_expected_item(
        self,
        coordinator,
        monkeypatch,
    ):
        monkeypatch.setattr(
            coordinator_module,
            "utc_now_text",
            lambda: "2026-08-25T10:00:00Z",
        )

        put_file_tracking_item(
            run_id="run-1",
            series="MIG 1",
            consignment_reference="TDR-1",
            record={"reference": "MIG 1/001"},
            file_id="file-1",
        )

        coordinator.dynamodb.put_item.assert_called_once_with(
            TableName="tracking-table",
            ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
            Item={
                "PK": {"S": "RUN#run-1#CONSIGNMENT#TDR-1"},
                "SK": {"S": "FILE#file-1"},
                "entityType": {"S": "FILE"},
                "runId": {"S": "run-1"},
                "series": {"S": "MIG 1"},
                "consignmentReference": {"S": "TDR-1"},
                "reference": {"S": "MIG 1/001"},
                "fileId": {"S": "file-1"},
                "status": {"S": "PENDING"},
                "createdAt": {"S": "2026-08-25T10:00:00Z"},
                "updatedAt": {"S": "2026-08-25T10:00:00Z"},
            },
        )

    def test_put_consignment_tracking_item_ignores_conditional_check_failure(
        self,
        coordinator,
    ):
        coordinator.dynamodb.put_item.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ConditionalCheckFailedException",
                    "Message": "item already exists",
                }
            },
            "PutItem",
        )

        put_consignment_tracking_item(
            run_id="run-1",
            series="MIG 1",
            consignment_reference="TDR-1",
            expected_file_count=2,
        )

        coordinator.dynamodb.put_item.assert_called_once()

    def test_put_file_tracking_item_ignores_conditional_check_failure(
        self,
        coordinator,
    ):
        coordinator.dynamodb.put_item.side_effect = ClientError(
            {
                "Error": {
                    "Code": "ConditionalCheckFailedException",
                    "Message": "item already exists",
                }
            },
            "PutItem",
        )

        put_file_tracking_item(
            run_id="run-1",
            series="MIG 1",
            consignment_reference="TDR-1",
            record={"reference": "MIG 1/001"},
            file_id="file-1",
        )

        coordinator.dynamodb.put_item.assert_called_once()


class TestProcessingLoops:
    """Lower-level processing tests for consignment and file loops"""

    def test_process_consignment_group_creates_tracking_and_processes_records(
        self,
        coordinator,
        monkeypatch,
    ):
        records = [
            record("MIG 1/001", "file-1", "TDR-1"),
            record("MIG 1/002", "file-2", "TDR-1"),
        ]

        monkeypatch.setattr(
            coordinator_module,
            "get_consignment_tracking_item",
            mock.Mock(return_value=None),
        )
        put_consignment_tracking_item_mock = mock.Mock()
        process_record_mock = mock.Mock(
            return_value={
                "workerMessageSent": 1,
                "fileSkipped": 0,
            }
        )

        monkeypatch.setattr(
            coordinator_module,
            "put_consignment_tracking_item",
            put_consignment_tracking_item_mock,
        )
        monkeypatch.setattr(
            coordinator_module,
            "process_record",
            process_record_mock,
        )

        result = process_consignment_group(
            run_id="run-1",
            series="MIG 1",
            consignment_reference="TDR-1",
            group_records=records,
        )

        assert result == {
            "workerMessagesSent": 2,
            "filesSkipped": 0,
            "consignmentSkipped": None,
        }
        put_consignment_tracking_item_mock.assert_called_once_with(
            run_id="run-1",
            series="MIG 1",
            consignment_reference="TDR-1",
            expected_file_count=2,
        )
        assert process_record_mock.call_count == 2

    def test_process_consignment_group_skips_terminal_consignment(
        self,
        coordinator,
        monkeypatch,
    ):
        process_record_mock = mock.Mock()
        monkeypatch.setattr(
            coordinator_module,
            "get_consignment_tracking_item",
            mock.Mock(return_value={"status": {"S": "SENT_TO_DDT"}}),
        )
        monkeypatch.setattr(
            coordinator_module,
            "process_record",
            process_record_mock,
        )

        result = process_consignment_group(
            run_id="run-1",
            series="MIG 1",
            consignment_reference="TDR-1",
            group_records=[record("MIG 1/001", "file-1", "TDR-1")],
        )

        assert result == {
            "workerMessagesSent": 0,
            "filesSkipped": 0,
            "consignmentSkipped": {
                "consignmentReference": "TDR-1",
                "status": "SENT_TO_DDT",
            },
        }
        process_record_mock.assert_not_called()

    def test_process_record_creates_tracking_and_sends_worker_message(
        self,
        coordinator,
        monkeypatch,
    ):
        monkeypatch.setattr(
            coordinator_module,
            "get_file_tracking_item",
            mock.Mock(return_value=None),
        )
        put_file_tracking_item_mock = mock.Mock()
        send_worker_message_mock = mock.Mock()

        monkeypatch.setattr(
            coordinator_module,
            "put_file_tracking_item",
            put_file_tracking_item_mock,
        )
        monkeypatch.setattr(
            coordinator_module,
            "send_worker_message",
            send_worker_message_mock,
        )

        result = process_record(
            run_id="run-1",
            series="MIG 1",
            consignment_reference="TDR-1",
            record=record("MIG 1/001", "file-1", "TDR-1"),
        )

        assert result == {
            "workerMessageSent": 1,
            "fileSkipped": 0,
        }
        put_file_tracking_item_mock.assert_called_once()
        send_worker_message_mock.assert_called_once_with(
            run_id="run-1",
            series="MIG 1",
            reference="MIG 1/001",
            consignment_reference="TDR-1",
            file_id="file-1",
        )

    def test_process_record_skips_completed_file(
        self,
        coordinator,
        monkeypatch,
    ):
        put_file_tracking_item_mock = mock.Mock()
        send_worker_message_mock = mock.Mock()

        monkeypatch.setattr(
            coordinator_module,
            "get_file_tracking_item",
            mock.Mock(return_value={"status": {"S": "COMPLETE"}}),
        )
        monkeypatch.setattr(
            coordinator_module,
            "put_file_tracking_item",
            put_file_tracking_item_mock,
        )
        monkeypatch.setattr(
            coordinator_module,
            "send_worker_message",
            send_worker_message_mock,
        )

        result = process_record(
            run_id="run-1",
            series="MIG 1",
            consignment_reference="TDR-1",
            record=record("MIG 1/001", "file-1", "TDR-1"),
        )

        assert result == {
            "workerMessageSent": 0,
            "fileSkipped": 1,
        }
        put_file_tracking_item_mock.assert_not_called()
        send_worker_message_mock.assert_not_called()
