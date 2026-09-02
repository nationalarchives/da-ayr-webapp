import csv
import json
import os
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest import mock

import pytest
from botocore.exceptions import ClientError

os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")

os.environ.setdefault("DDT_TEMP_CSV_BUCKET", "ddt-temp-csv-bucket")
os.environ.setdefault("DDT_TEMP_DATA_BUCKET", "ddt-temp-data-bucket")
os.environ.setdefault(
    "DA_EVENTBUS_TOPIC_ARN", "arn:aws:sns:eu-west-2:123456789012:da-eventbus"
)
os.environ.setdefault("TRACKING_TABLE_NAME", "tracking-table")

import finaliser.handler as finaliser_module
from finaliser.handler import (
    FINALISING,
    READY_TO_FINALISE,
    SENT_TO_DDT,
    build_ddt_prepared_message,
    consignment_key,
    create_checksum_files,
    get_consignment_status,
    lambda_handler,
    list_staged_csv_keys,
    mark_consignment_sent_to_ddt,
    merge_staged_csvs,
    process_message,
    publish_ddt_message,
    read_csv_from_s3,
    start_finalising_or_skip,
    upload_metadata_files,
)


@pytest.fixture
def finaliser(monkeypatch):
    monkeypatch.setattr(finaliser_module, "s3", mock.Mock())
    monkeypatch.setattr(finaliser_module, "sns", mock.Mock())
    monkeypatch.setattr(finaliser_module, "dynamodb", mock.Mock())

    monkeypatch.setattr(
        finaliser_module, "DDT_TEMP_CSV_BUCKET", "ddt-temp-csv-bucket"
    )
    monkeypatch.setattr(
        finaliser_module, "DDT_TEMP_DATA_BUCKET", "ddt-temp-data-bucket"
    )
    monkeypatch.setattr(
        finaliser_module,
        "DA_EVENTBUS_TOPIC_ARN",
        "arn:aws:sns:eu-west-2:123456789012:da-eventbus",
    )
    monkeypatch.setattr(
        finaliser_module, "TRACKING_TABLE_NAME", "tracking-table"
    )
    monkeypatch.setattr(finaliser_module, "OUTPUT_PREFIX", "ayr-mds-csv")
    monkeypatch.setattr(finaliser_module, "STAGING_PREFIX", "ayr-mds-staging")
    monkeypatch.setattr(finaliser_module, "FUNCTION_NAME", "finaliser-lambda")

    return finaliser_module


class LambdaContext:
    aws_request_id = "aws-request-id-1"


def finaliser_message() -> dict[str, str]:
    return {
        "runId": "run-1",
        "series": "MIG 1",
        "consignmentReference": "TDR-1",
    }


def sqs_event(
    message: dict[str, Any], message_id: str = "message-1"
) -> dict[str, Any]:
    return {
        "Records": [
            {
                "messageId": message_id,
                "body": json.dumps(message),
            }
        ]
    }


def conditional_check_failed() -> ClientError:
    return ClientError(
        {
            "Error": {
                "Code": "ConditionalCheckFailedException",
                "Message": "condition failed",
            }
        },
        "UpdateItem",
    )


def read_csv_file(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class TestLambdaHandler:
    """High-level finaliser handler tests"""

    def test_lambda_handler_supports_direct_invocation(
        self, finaliser, monkeypatch
    ):
        process_message_mock = mock.Mock()
        monkeypatch.setattr(
            finaliser_module, "process_message", process_message_mock
        )

        event = finaliser_message()
        context = LambdaContext()

        result = lambda_handler(event, context)

        assert result == {"batchItemFailures": []}
        process_message_mock.assert_called_once_with(event, context)

    def test_lambda_handler_processes_sqs_message(self, finaliser, monkeypatch):
        process_message_mock = mock.Mock()
        monkeypatch.setattr(
            finaliser_module, "process_message", process_message_mock
        )

        event = sqs_event(finaliser_message())
        context = LambdaContext()

        result = lambda_handler(event, context)

        assert result == {"batchItemFailures": []}
        process_message_mock.assert_called_once_with(
            finaliser_message(), context
        )

    def test_lambda_handler_returns_failed_sqs_message_id(
        self, finaliser, monkeypatch
    ):
        monkeypatch.setattr(
            finaliser_module,
            "process_message",
            mock.Mock(side_effect=RuntimeError("failed")),
        )

        result = lambda_handler(
            sqs_event(finaliser_message(), message_id="sqs-message-1"),
            LambdaContext(),
        )

        assert result == {
            "batchItemFailures": [
                {
                    "itemIdentifier": "sqs-message-1",
                }
            ]
        }


class TestProcessMessage:
    """Finaliser orchestration tests"""

    def test_process_message_skips_when_ddt_message_already_sent(
        self, finaliser, monkeypatch
    ):
        monkeypatch.setattr(
            finaliser_module,
            "start_finalising_or_skip",
            mock.Mock(return_value=False),
        )
        list_staged_csv_keys_mock = mock.Mock()
        publish_ddt_message_mock = mock.Mock()
        mark_consignment_sent_to_ddt_mock = mock.Mock()

        monkeypatch.setattr(
            finaliser_module, "list_staged_csv_keys", list_staged_csv_keys_mock
        )
        monkeypatch.setattr(
            finaliser_module, "publish_ddt_message", publish_ddt_message_mock
        )
        monkeypatch.setattr(
            finaliser_module,
            "mark_consignment_sent_to_ddt",
            mark_consignment_sent_to_ddt_mock,
        )

        process_message(finaliser_message(), LambdaContext())

        list_staged_csv_keys_mock.assert_not_called()
        publish_ddt_message_mock.assert_not_called()
        mark_consignment_sent_to_ddt_mock.assert_not_called()

    def test_process_message_merges_uploads_publishes_and_marks_sent(
        self, finaliser, monkeypatch
    ):
        monkeypatch.setattr(
            finaliser_module,
            "start_finalising_or_skip",
            mock.Mock(return_value=True),
        )
        list_staged_csv_keys_mock = mock.Mock(
            return_value=["MIG 1/ayr-mds-staging/TDR-1/file-1/AYR-file.csv"]
        )
        merge_staged_csvs_mock = mock.Mock(return_value={"AYR-file.csv": 1})
        create_checksum_files_mock = mock.Mock()
        upload_metadata_files_mock = mock.Mock()
        publish_ddt_message_mock = mock.Mock(return_value="sns-message-id-1")
        mark_consignment_sent_to_ddt_mock = mock.Mock()

        monkeypatch.setattr(
            finaliser_module, "list_staged_csv_keys", list_staged_csv_keys_mock
        )
        monkeypatch.setattr(
            finaliser_module, "merge_staged_csvs", merge_staged_csvs_mock
        )
        monkeypatch.setattr(
            finaliser_module,
            "create_checksum_files",
            create_checksum_files_mock,
        )
        monkeypatch.setattr(
            finaliser_module,
            "upload_metadata_files",
            upload_metadata_files_mock,
        )
        monkeypatch.setattr(
            finaliser_module, "publish_ddt_message", publish_ddt_message_mock
        )
        monkeypatch.setattr(
            finaliser_module,
            "mark_consignment_sent_to_ddt",
            mark_consignment_sent_to_ddt_mock,
        )

        process_message(finaliser_message(), LambdaContext())

        list_staged_csv_keys_mock.assert_called_once_with(
            "MIG 1/ayr-mds-staging/TDR-1"
        )
        upload_metadata_files_mock.assert_called_once()
        assert (
            upload_metadata_files_mock.call_args.kwargs["bucket"]
            == "ddt-temp-csv-bucket"
        )
        assert (
            upload_metadata_files_mock.call_args.kwargs["prefix"]
            == "MIG 1/ayr-mds-csv/TDR-1"
        )

        published_message = publish_ddt_message_mock.call_args.args[0]
        assert published_message["parameters"] == {
            "reference": "TDR-1",
            "consignmentType": "STANDARD",
            "s3ObjectsBucket": "ddt-temp-data-bucket",
            "s3ObjectsLocationKey": "MIG 1/",
            "s3MetadataBucket": "ddt-temp-csv-bucket",
            "s3MetadataFileKey": "MIG 1/ayr-mds-csv/",
        }
        mark_consignment_sent_to_ddt_mock.assert_called_once_with(
            run_id="run-1",
            consignment_reference="TDR-1",
            ddt_sns_message_id="sns-message-id-1",
        )

    def test_process_message_fails_when_no_staged_csv_files_found(
        self, finaliser, monkeypatch
    ):
        monkeypatch.setattr(
            finaliser_module,
            "start_finalising_or_skip",
            mock.Mock(return_value=True),
        )
        monkeypatch.setattr(
            finaliser_module, "list_staged_csv_keys", mock.Mock(return_value=[])
        )

        with pytest.raises(ValueError, match="No staged CSV files found"):
            process_message(finaliser_message(), LambdaContext())


class TestCsvDiscoveryAndMerge:
    """CSV listing, merging and checksum tests"""

    def test_list_staged_csv_keys_only_returns_expected_csv_files(
        self, finaliser
    ):
        paginator = mock.Mock()
        paginator.paginate.return_value = [
            {
                "Contents": [
                    {"Key": "MIG 1/ayr-mds-staging/TDR-1/file-1/AYR-file.csv"},
                    {
                        "Key": "MIG 1/ayr-mds-staging/TDR-1/file-1/not-metadata.txt"
                    },
                    {
                        "Key": "MIG 1/ayr-mds-staging/TDR-1/file-1/AYR-manifest.csv"
                    },
                    {
                        "Key": "MIG 1/ayr-mds-staging/TDR-1/file-1/unexpected.csv"
                    },
                    {
                        "Key": "MIG 1/ayr-mds-staging/TDR-1/file-1/AYR-body-metadata.csv"
                    },
                ]
            }
        ]
        finaliser.s3.get_paginator.return_value = paginator

        result = list_staged_csv_keys("MIG 1/ayr-mds-staging/TDR-1")

        assert result == [
            "MIG 1/ayr-mds-staging/TDR-1/file-1/AYR-body-metadata.csv",
            "MIG 1/ayr-mds-staging/TDR-1/file-1/AYR-file.csv",
        ]
        paginator.paginate.assert_called_once_with(
            Bucket="ddt-temp-csv-bucket",
            Prefix="MIG 1/ayr-mds-staging/TDR-1/",
        )

    def test_read_csv_from_s3_returns_rows(self, finaliser):
        finaliser.s3.get_object.return_value = {
            "Body": BytesIO(b"FileId,FileName\nfile-1,test.txt\n")
        }

        result = list(read_csv_from_s3("path/AYR-file.csv"))

        assert result == [
            {
                "FileId": "file-1",
                "FileName": "test.txt",
            }
        ]

    def test_merge_staged_csvs_deduplicates_rows(
        self, finaliser, monkeypatch, tmp_path
    ):
        def fake_read_csv_from_s3(key: str):
            file_name = Path(key).name

            if file_name == "AYR-body-metadata.csv":
                return [
                    {"BodyId": "", "Name": "Body 1", "Description": "Body 1"},
                    {"BodyId": "", "Name": "Body 1", "Description": "Body 1"},
                ]

            if file_name == "AYR-file.csv":
                return [
                    {
                        "FileId": "file-1",
                        "ConsignmentId": "consignment-1",
                        "FileType": "File",
                        "FileName": "file-1.txt",
                        "FilePath": "",
                        "FileReference": "001",
                        "CiteableReference": "MIG 1/001",
                        "ParentReference": "",
                        "OriginalFilePath": "",
                        "Checksum": "checksum-1",
                        "CreatedDatetime": "2026-09-01T10:00:00Z",
                    },
                    {
                        "FileId": "file-2",
                        "ConsignmentId": "consignment-1",
                        "FileType": "File",
                        "FileName": "file-2.txt",
                        "FilePath": "",
                        "FileReference": "002",
                        "CiteableReference": "MIG 1/002",
                        "ParentReference": "",
                        "OriginalFilePath": "",
                        "Checksum": "checksum-2",
                        "CreatedDatetime": "2026-09-01T10:00:00Z",
                    },
                    {
                        "FileId": "file-2",
                        "ConsignmentId": "consignment-1",
                        "FileType": "File",
                        "FileName": "file-2.txt",
                        "FilePath": "",
                        "FileReference": "002",
                        "CiteableReference": "MIG 1/002",
                        "ParentReference": "",
                        "OriginalFilePath": "",
                        "Checksum": "checksum-2",
                        "CreatedDatetime": "2026-09-01T10:00:00Z",
                    },
                ]

            return []

        monkeypatch.setattr(
            finaliser_module, "read_csv_from_s3", fake_read_csv_from_s3
        )

        counts = merge_staged_csvs(
            [
                "staging/file-1/AYR-body-metadata.csv",
                "staging/file-1/AYR-file.csv",
            ],
            tmp_path,
        )

        assert counts["AYR-body-metadata.csv"] == 1
        assert counts["AYR-file.csv"] == 2
        assert read_csv_file(tmp_path / "AYR-body-metadata.csv") == [
            {
                "BodyId": "",
                "Name": "Body 1",
                "Description": "Body 1",
            }
        ]
        assert [
            row["FileId"] for row in read_csv_file(tmp_path / "AYR-file.csv")
        ] == [
            "file-1",
            "file-2",
        ]

    def test_create_checksum_files_writes_manifest_and_manifest_checksum(
        self, tmp_path
    ):
        (tmp_path / "AYR-body-metadata.csv").write_text(
            "Name\nBody 1\n", encoding="utf-8"
        )
        (tmp_path / "AYR-file.csv").write_text(
            "FileId\nfile-1\n", encoding="utf-8"
        )

        create_checksum_files(tmp_path)

        manifest_rows = read_csv_file(tmp_path / "AYR-manifest.csv")
        assert [row["file_name"] for row in manifest_rows] == [
            "AYR-body-metadata.csv",
            "AYR-file.csv",
        ]
        assert (
            (tmp_path / "AYR-manifest.csv.sha256")
            .read_text(encoding="utf-8")
            .endswith("  AYR-manifest.csv\n")
        )

    def test_upload_metadata_files_uploads_files_only(
        self, finaliser, tmp_path
    ):
        (tmp_path / "AYR-file.csv").write_text(
            "FileId\nfile-1\n", encoding="utf-8"
        )
        (tmp_path / "AYR-body-metadata.csv").write_text(
            "Name\nBody 1\n", encoding="utf-8"
        )
        (tmp_path / "nested").mkdir()

        upload_metadata_files(tmp_path, "csv-bucket", "MIG 1/ayr-mds-csv/TDR-1")

        assert finaliser.s3.upload_file.call_args_list == [
            mock.call(
                str(tmp_path / "AYR-body-metadata.csv"),
                "csv-bucket",
                "MIG 1/ayr-mds-csv/TDR-1/AYR-body-metadata.csv",
            ),
            mock.call(
                str(tmp_path / "AYR-file.csv"),
                "csv-bucket",
                "MIG 1/ayr-mds-csv/TDR-1/AYR-file.csv",
            ),
        ]


class TestDdtMessage:
    """DDT prepared message tests"""

    def test_build_ddt_prepared_message_uses_base_keys(
        self, finaliser, monkeypatch
    ):
        monkeypatch.setattr(
            finaliser_module, "utc_now_text", lambda: "2026-09-01T10:00:00Z"
        )
        monkeypatch.setattr(
            finaliser_module.uuid, "uuid4", lambda: "message-id-1"
        )

        message = build_ddt_prepared_message(
            reference="TDR-1",
            s3_objects_bucket="data-bucket",
            s3_objects_location_key="MIG 1/",
            s3_metadata_bucket="metadata-bucket",
            s3_metadata_file_key="MIG 1/ayr-mds-csv/",
            context=LambdaContext(),
        )

        assert message["properties"] == {
            "messageType": "uk.gov.nationalarchives.da.messages.ayrmetadata.prepared",
            "timestamp": "2026-09-01T10:00:00Z",
            "function": "finaliser-lambda",
            "producer": "AYR",
            "messageId": "message-id-1",
            "parentMessageId": "",
            "executionId": "aws-request-id-1",
        }
        assert message["parameters"] == {
            "reference": "TDR-1",
            "consignmentType": "STANDARD",
            "s3ObjectsBucket": "data-bucket",
            "s3ObjectsLocationKey": "MIG 1/",
            "s3MetadataBucket": "metadata-bucket",
            "s3MetadataFileKey": "MIG 1/ayr-mds-csv/",
        }

    def test_publish_ddt_message_publishes_with_message_type_attribute(
        self, finaliser
    ):
        finaliser.sns.publish.return_value = {"MessageId": "sns-message-id-1"}
        message = {
            "properties": {
                "messageType": "uk.gov.nationalarchives.da.messages.ayrmetadata.prepared",
            },
            "parameters": {},
        }

        result = publish_ddt_message(message)

        assert result == "sns-message-id-1"
        finaliser.sns.publish.assert_called_once_with(
            TopicArn="arn:aws:sns:eu-west-2:123456789012:da-eventbus",
            Message=json.dumps(message),
            MessageAttributes={
                "messageType": {
                    "DataType": "String",
                    "StringValue": "uk.gov.nationalarchives.da.messages.ayrmetadata.prepared",
                }
            },
        )


class TestDynamoDbState:
    """DynamoDB finaliser lock and status tests"""

    def test_start_finalising_or_skip_marks_consignment_finalising(
        self, finaliser, monkeypatch
    ):
        monkeypatch.setattr(
            finaliser_module, "utc_now_text", lambda: "2026-09-01T10:00:00Z"
        )

        result = start_finalising_or_skip("run-1", "TDR-1")

        assert result
        finaliser.dynamodb.update_item.assert_called_once()
        update_kwargs = finaliser.dynamodb.update_item.call_args.kwargs
        assert update_kwargs["TableName"] == "tracking-table"
        assert update_kwargs["Key"] == consignment_key("run-1", "TDR-1")
        assert "#status = :ready" in update_kwargs["ConditionExpression"]
        assert update_kwargs["ExpressionAttributeValues"][":ready"] == {
            "S": READY_TO_FINALISE,
        }
        assert update_kwargs["ExpressionAttributeValues"][":finalising"] == {
            "S": FINALISING,
        }

    def test_start_finalising_or_skip_returns_already_sent_when_status_is_sent_to_ddt(
        self,
        finaliser,
        monkeypatch,
    ):
        finaliser.dynamodb.update_item.side_effect = conditional_check_failed()
        monkeypatch.setattr(
            finaliser_module,
            "get_consignment_status",
            mock.Mock(return_value=SENT_TO_DDT),
        )

        result = start_finalising_or_skip("run-1", "TDR-1")

        assert not result

    def test_start_finalising_or_skip_raises_when_status_is_finalising(
        self,
        finaliser,
        monkeypatch,
    ):
        finaliser.dynamodb.update_item.side_effect = conditional_check_failed()
        monkeypatch.setattr(
            finaliser_module,
            "get_consignment_status",
            mock.Mock(return_value=FINALISING),
        )

        with pytest.raises(RuntimeError, match="already FINALISING"):
            start_finalising_or_skip("run-1", "TDR-1")

    def test_get_consignment_status_reads_tracking_item(self, finaliser):
        finaliser.dynamodb.get_item.return_value = {
            "Item": {
                "status": {"S": READY_TO_FINALISE},
            }
        }

        result = get_consignment_status("run-1", "TDR-1")

        assert result == READY_TO_FINALISE
        finaliser.dynamodb.get_item.assert_called_once_with(
            TableName="tracking-table",
            Key=consignment_key("run-1", "TDR-1"),
            ConsistentRead=True,
        )

    def test_get_consignment_status_raises_when_tracking_item_missing(
        self, finaliser
    ):
        finaliser.dynamodb.get_item.return_value = {}

        with pytest.raises(
            ValueError, match="Missing consignment tracking item"
        ):
            get_consignment_status("run-1", "TDR-1")

    def test_mark_consignment_sent_to_ddt_updates_status(
        self, finaliser, monkeypatch
    ):
        monkeypatch.setattr(
            finaliser_module, "utc_now_text", lambda: "2026-09-01T10:00:00Z"
        )

        mark_consignment_sent_to_ddt(
            run_id="run-1",
            consignment_reference="TDR-1",
            ddt_sns_message_id="sns-message-id-1",
        )

        finaliser.dynamodb.update_item.assert_called_once()
        update_kwargs = finaliser.dynamodb.update_item.call_args.kwargs
        assert update_kwargs["TableName"] == "tracking-table"
        assert update_kwargs["Key"] == consignment_key("run-1", "TDR-1")
        assert update_kwargs["ConditionExpression"] == "#status = :finalising"
        assert update_kwargs["ExpressionAttributeValues"][":finalising"] == {
            "S": FINALISING,
        }
        assert update_kwargs["ExpressionAttributeValues"][":sent"] == {
            "S": SENT_TO_DDT,
        }
        assert update_kwargs["ExpressionAttributeValues"][":message_id"] == {
            "S": "sns-message-id-1",
        }

    def test_mark_consignment_sent_to_ddt_ignores_already_sent_status(
        self,
        finaliser,
        monkeypatch,
    ):
        finaliser.dynamodb.update_item.side_effect = conditional_check_failed()
        monkeypatch.setattr(
            finaliser_module,
            "get_consignment_status",
            mock.Mock(return_value=SENT_TO_DDT),
        )

        mark_consignment_sent_to_ddt(
            run_id="run-1",
            consignment_reference="TDR-1",
            ddt_sns_message_id="sns-message-id-1",
        )

        finaliser.dynamodb.update_item.assert_called_once()
