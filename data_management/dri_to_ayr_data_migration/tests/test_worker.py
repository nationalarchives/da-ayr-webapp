import csv
import json
import os
from pathlib import Path
from unittest.mock import Mock, call

import pytest

os.environ.setdefault("AWS_DEFAULT_REGION", "eu-west-2")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")

os.environ.setdefault("DRI_JSON_BUCKET", "dri-json-bucket")
os.environ.setdefault("DRI_DATA_BUCKET", "dri-data-bucket")
os.environ.setdefault("DDT_TEMP_CSV_BUCKET", "temp-csv-bucket")
os.environ.setdefault("DDT_TEMP_DATA_BUCKET", "temp-data-bucket")
os.environ.setdefault("DROID_QUEUE_URL", "https://sqs.example.com/droid")
os.environ.setdefault("TRACKING_TABLE_NAME", "tracking-table")

import worker.dri_to_ayr_csv as csv_module
import worker.handler as worker_module

ENVIRONMENT = {
    "DRI_JSON_BUCKET": "dri-json-bucket",
    "DRI_DATA_BUCKET": "dri-data-bucket",
    "DDT_TEMP_CSV_BUCKET": "temp-csv-bucket",
    "DDT_TEMP_DATA_BUCKET": "temp-data-bucket",
    "DROID_QUEUE_URL": "https://sqs.example.com/droid",
    "TRACKING_TABLE_NAME": "tracking-table",
}

FIXED_NOW = "2026-08-27T10:40:00Z"
FILE_ID = "6be8b424-6f9a-4f34-91e2-bde01bdf7f8b"
RECORD_ID = "dc2da3fd-62ef-41fd-8b44-6574097b7951"
CONSIGNMENT_REFERENCE = "TDR-2026-7333"


@pytest.fixture
def handler_module(monkeypatch):
    for key, value in ENVIRONMENT.items():
        monkeypatch.setenv(key, value)
        monkeypatch.setattr(worker_module, key, value)

    monkeypatch.setattr(worker_module, "s3", Mock(name="s3_client"))
    monkeypatch.setattr(worker_module, "sqs", Mock(name="sqs_client"))
    monkeypatch.setattr(worker_module, "dynamodb", Mock(name="dynamodb_client"))

    return worker_module


def worker_message() -> dict[str, str | bool]:
    return {
        "runId": "run-1",
        "series": "LEV 2",
        "reference": "LEV 2/2BD/Z",
        "consignmentReference": CONSIGNMENT_REFERENCE,
        "fileId": FILE_ID,
        "includeBodyAndSeries": True,
        "includeConsignment": True,
    }


def make_digital_file() -> dict:
    return {
        "fileId": FILE_ID,
        "fileName": "example.txt",
        "filePath": "LEV 2/2BD/example.txt",
        "sizeBytes": 1234,
        "checksums": [
            {"hash": "MD5", "value": "md5-checksum"},
            {"hash": "SHA-256", "value": "sha256-checksum"},
        ],
        "extraDigitalFileField": "extra file value",
    }


def make_record() -> dict:
    return {
        "recordId": RECORD_ID,
        "reference": "LEV 2/2BD/Z",
        "transferredBy": "Ministry of Test Data",
        "title": "Closed original title",
        "publicTitle": "Open public title",
        "description": "Closed original description",
        "publicDescription": "Open public description",
        "dateLastModified": "2026-08-27T10:40:00Z",
        "coveringDateEnd": "2026-08-27",
        "evidenceProvider": "Evidence provider",
        "formerReferenceDepartment": "TEST 123",
        "heldBy": "The National Archives",
        "language": "English",
        "legalStatus": "Public Record(s)",
        "note": "Test note",
        "copyrightHolders": ["Crown copyright", "Test copyright"],
        "customRecordField": "keep this source value",
        "sensitivity": {
            "isRecordClosed": True,
            "closurePeriod": 20,
            "closureStartDate": "2020-01-01",
            "closureReviewDate": "2040-01-01",
            "foiAssertedDate": "2020-01-02",
            "foiExemptions": [
                {"reference": "FOI 23"},
                {"reference": "FOI 40"},
            ],
        },
        "digitalFiles": [make_digital_file()],
    }


def read_rows(output_dir: Path, file_name: str) -> list[dict[str, str]]:
    with (output_dir / file_name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def metadata_values(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for row in rows:
        values.setdefault(row["PropertyName"], []).append(row["Value"])
    return values


class TestWorkerHandler:
    def test_lambda_handler_supports_direct_retry(
        self, handler_module, monkeypatch
    ):
        module = handler_module
        process_message = Mock()
        monkeypatch.setattr(module, "process_message", process_message)

        result = module.lambda_handler(worker_message(), None)

        assert result == {"batchItemFailures": []}
        process_message.assert_called_once_with(worker_message())

    def test_lambda_handler_processes_successful_sqs_message(
        self, handler_module, monkeypatch
    ):
        module = handler_module
        process_message = Mock()
        monkeypatch.setattr(module, "process_message", process_message)

        result = module.lambda_handler(
            {
                "Records": [
                    {
                        "messageId": "message-1",
                        "body": json.dumps(worker_message()),
                    }
                ]
            },
            None,
        )

        assert result == {"batchItemFailures": []}
        process_message.assert_called_once_with(worker_message())

    def test_lambda_handler_reports_failed_sqs_message(
        self, handler_module, monkeypatch
    ):
        module = handler_module

        def fail(_message):
            raise RuntimeError("boom")

        monkeypatch.setattr(module, "process_message", fail)

        result = module.lambda_handler(
            {
                "Records": [
                    {
                        "messageId": "message-1",
                        "body": json.dumps(worker_message()),
                    }
                ]
            },
            None,
        )

        assert result == {
            "batchItemFailures": [{"itemIdentifier": "message-1"}]
        }

    @pytest.mark.parametrize(
        "flag_name",
        ["includeBodyAndSeries", "includeConsignment"],
    )
    def test_process_message_requires_boolean_include_flags(
        self, handler_module, flag_name
    ):
        message = worker_message()
        message[flag_name] = "true"

        with pytest.raises(
            ValueError,
            match=f"Missing or invalid boolean field: {flag_name}",
        ):
            handler_module.process_message(message)

    def test_process_message_skips_terminal_consignment(
        self, handler_module, monkeypatch
    ):
        module = handler_module
        monkeypatch.setattr(
            module, "get_consignment_status", Mock(return_value="SENT_TO_DDT")
        )
        monkeypatch.setattr(module, "is_file_already_complete", Mock())
        monkeypatch.setattr(module, "process_file", Mock())

        module.process_message(worker_message())

        module.get_consignment_status.assert_called_once_with(
            run_id="run-1",
            consignment_reference=CONSIGNMENT_REFERENCE,
        )
        module.is_file_already_complete.assert_not_called()
        module.process_file.assert_not_called()

    def test_process_message_skips_completed_file(
        self, handler_module, monkeypatch
    ):
        module = handler_module
        monkeypatch.setattr(
            module, "get_consignment_status", Mock(return_value=None)
        )
        monkeypatch.setattr(
            module, "is_file_already_complete", Mock(return_value=True)
        )
        monkeypatch.setattr(module, "process_file", Mock())

        module.process_message(worker_message())

        module.is_file_already_complete.assert_called_once_with(
            run_id="run-1",
            consignment_reference=CONSIGNMENT_REFERENCE,
            file_id=FILE_ID,
        )
        module.process_file.assert_not_called()

    def test_process_message_passes_include_flags_to_process_file(
        self, handler_module, monkeypatch
    ):
        module = handler_module
        monkeypatch.setattr(
            module, "get_consignment_status", Mock(return_value="STAGING")
        )
        monkeypatch.setattr(
            module, "is_file_already_complete", Mock(return_value=False)
        )
        monkeypatch.setattr(module, "process_file", Mock())

        module.process_message(worker_message())

        module.process_file.assert_called_once_with(
            run_id="run-1",
            series="LEV 2",
            reference="LEV 2/2BD/Z",
            consignment_reference=CONSIGNMENT_REFERENCE,
            expected_file_id=FILE_ID,
            include_body_and_series=True,
            include_consignment=True,
        )

    def test_process_file_stages_metadata_and_sends_droid_message(
        self, handler_module, monkeypatch
    ):
        module = handler_module
        record = make_record()

        def download_file(bucket, key, destination):
            assert bucket == ENVIRONMENT["DRI_JSON_BUCKET"]
            assert key == "live/LEV 2-2BD-Z.json"
            Path(destination).write_text(json.dumps(record), encoding="utf-8")

        module.s3.download_file.side_effect = download_file

        copied_key = f"LEV 2/{CONSIGNMENT_REFERENCE}/{FILE_ID}"
        copy_data_file = Mock(return_value=copied_key)
        convert_record_to_csv = Mock()
        upload_metadata_files = Mock()
        send_droid_message = Mock()

        monkeypatch.setattr(module, "copy_data_file", copy_data_file)
        monkeypatch.setattr(
            module, "convert_record_to_csv", convert_record_to_csv
        )
        monkeypatch.setattr(
            module, "upload_metadata_files", upload_metadata_files
        )
        monkeypatch.setattr(module, "send_droid_message", send_droid_message)

        module.process_file(
            run_id="run-1",
            series="LEV 2",
            reference="LEV 2/2BD/Z",
            consignment_reference=CONSIGNMENT_REFERENCE,
            expected_file_id=FILE_ID,
            include_body_and_series=True,
            include_consignment=True,
        )

        copy_data_file.assert_called_once_with(
            record_id=RECORD_ID,
            file_id=FILE_ID,
            series="LEV 2",
            consignment_reference=CONSIGNMENT_REFERENCE,
        )
        convert_record_to_csv.assert_called_once()
        convert_kwargs = convert_record_to_csv.call_args.kwargs
        assert convert_kwargs["record"] == record
        assert convert_kwargs["digital_file"] == record["digitalFiles"][0]
        assert Path(convert_kwargs["output_dir"]).name == "csv-output"
        assert convert_kwargs["consignment_reference"] == CONSIGNMENT_REFERENCE
        assert convert_kwargs["include_body_and_series"] is True
        assert convert_kwargs["include_consignment"] is True

        upload_metadata_files.assert_called_once_with(
            local_dir=Path(convert_kwargs["output_dir"]),
            bucket=ENVIRONMENT["DDT_TEMP_CSV_BUCKET"],
            shared_prefix="LEV 2/ayr-mds-staging/shared",
            consignment_prefix=(
                f"LEV 2/ayr-mds-staging/{CONSIGNMENT_REFERENCE}"
            ),
            file_prefix=(
                f"LEV 2/ayr-mds-staging/{CONSIGNMENT_REFERENCE}/{FILE_ID}"
            ),
        )
        send_droid_message.assert_called_once_with(
            run_id="run-1",
            series="LEV 2",
            consignment_reference=CONSIGNMENT_REFERENCE,
            file_id=FILE_ID,
            bucket=ENVIRONMENT["DDT_TEMP_DATA_BUCKET"],
            key=copied_key,
            extension="txt",
        )

    def test_copy_data_file_copies_file_and_returns_destination_key(
        self, handler_module
    ):
        module = handler_module

        result = module.copy_data_file(
            record_id=RECORD_ID,
            file_id=FILE_ID,
            series="LEV 2",
            consignment_reference=CONSIGNMENT_REFERENCE,
        )

        assert result == f"LEV 2/{CONSIGNMENT_REFERENCE}/{FILE_ID}"
        module.s3.copy_object.assert_called_once_with(
            Bucket=ENVIRONMENT["DDT_TEMP_DATA_BUCKET"],
            CopySource={
                "Bucket": ENVIRONMENT["DRI_DATA_BUCKET"],
                "Key": f"v1/{RECORD_ID}/{FILE_ID}",
            },
            Key=f"LEV 2/{CONSIGNMENT_REFERENCE}/{FILE_ID}",
            TaggingDirective="REPLACE",
        )

    def test_send_droid_message_sends_expected_sqs_message(
        self, handler_module
    ):
        module = handler_module
        module.sqs.send_message.return_value = {"MessageId": "message-1"}

        module.send_droid_message(
            run_id="run-1",
            series="LEV 2",
            consignment_reference=CONSIGNMENT_REFERENCE,
            file_id=FILE_ID,
            bucket="temp-data-bucket",
            key=f"LEV 2/{CONSIGNMENT_REFERENCE}/{FILE_ID}",
            extension="txt",
        )

        module.sqs.send_message.assert_called_once()
        send_kwargs = module.sqs.send_message.call_args.kwargs
        assert send_kwargs["QueueUrl"] == ENVIRONMENT["DROID_QUEUE_URL"]
        assert json.loads(send_kwargs["MessageBody"]) == {
            "runId": "run-1",
            "series": "LEV 2",
            "consignmentReference": CONSIGNMENT_REFERENCE,
            "bucket": "temp-data-bucket",
            "key": f"LEV 2/{CONSIGNMENT_REFERENCE}/{FILE_ID}",
            "fileId": FILE_ID,
            "extension": "txt",
        }

    def test_get_consignment_status_returns_none_when_tracking_item_missing(
        self, handler_module
    ):
        module = handler_module
        module.dynamodb.get_item.return_value = {}

        result = module.get_consignment_status(
            run_id="run-1",
            consignment_reference=CONSIGNMENT_REFERENCE,
        )

        assert result is None

    def test_get_consignment_status_returns_trimmed_status(
        self, handler_module
    ):
        module = handler_module
        module.dynamodb.get_item.return_value = {
            "Item": {
                "status": {"S": " STAGING "},
            }
        }

        result = module.get_consignment_status(
            run_id="run-1",
            consignment_reference=CONSIGNMENT_REFERENCE,
        )

        assert result == "STAGING"

    def test_is_file_already_complete_returns_false_when_tracking_item_missing(
        self, handler_module
    ):
        module = handler_module
        module.dynamodb.get_item.return_value = {}

        result = module.is_file_already_complete(
            run_id="run-1",
            consignment_reference=CONSIGNMENT_REFERENCE,
            file_id=FILE_ID,
        )

        assert result is False

    def test_is_file_already_complete_returns_true_for_complete_file(
        self, handler_module
    ):
        module = handler_module
        module.dynamodb.get_item.return_value = {
            "Item": {
                "status": {"S": "COMPLETE"},
            }
        }

        result = module.is_file_already_complete(
            run_id="run-1",
            consignment_reference=CONSIGNMENT_REFERENCE,
            file_id=FILE_ID,
        )

        assert result is True

    def test_upload_metadata_files_routes_each_csv_to_its_staging_prefix(
        self, handler_module, tmp_path
    ):
        module = handler_module

        body_csv = tmp_path / csv_module.BODY_CSV_NAME
        series_csv = tmp_path / csv_module.SERIES_CSV_NAME
        consignment_csv = tmp_path / csv_module.CONSIGNMENT_CSV_NAME
        file_csv = tmp_path / "AYR-file.csv"

        for csv_file in (body_csv, series_csv, consignment_csv, file_csv):
            csv_file.write_text("header\nvalue\n", encoding="utf-8")

        nested_dir = tmp_path / "nested"
        nested_dir.mkdir()

        module.upload_metadata_files(
            local_dir=tmp_path,
            bucket="temp-csv-bucket",
            shared_prefix="LEV 2/ayr-mds-staging/shared",
            consignment_prefix=(
                f"LEV 2/ayr-mds-staging/{CONSIGNMENT_REFERENCE}"
            ),
            file_prefix=(
                f"LEV 2/ayr-mds-staging/{CONSIGNMENT_REFERENCE}/{FILE_ID}"
            ),
        )

        module.s3.upload_file.assert_has_calls(
            [
                call(
                    str(body_csv),
                    "temp-csv-bucket",
                    "LEV 2/ayr-mds-staging/shared/AYR-body-metadata.csv",
                ),
                call(
                    str(series_csv),
                    "temp-csv-bucket",
                    "LEV 2/ayr-mds-staging/shared/AYR-series-metadata.csv",
                ),
                call(
                    str(consignment_csv),
                    "temp-csv-bucket",
                    f"LEV 2/ayr-mds-staging/{CONSIGNMENT_REFERENCE}/"
                    "AYR-consignment-metadata.csv",
                ),
                call(
                    str(file_csv),
                    "temp-csv-bucket",
                    f"LEV 2/ayr-mds-staging/{CONSIGNMENT_REFERENCE}/"
                    f"{FILE_ID}/AYR-file.csv",
                ),
            ],
            any_order=True,
        )
        assert module.s3.upload_file.call_count == 4


class TestCsvConversion:
    def test_convert_record_to_csv_writes_expected_csv_files(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(csv_module, "utc_now_text", lambda: FIXED_NOW)

        record = make_record()
        digital_file = record["digitalFiles"][0]

        csv_module.convert_record_to_csv(
            record=record,
            digital_file=digital_file,
            output_dir=str(tmp_path),
            consignment_reference=CONSIGNMENT_REFERENCE,
            include_body_and_series=True,
            include_consignment=True,
        )

        assert (tmp_path / csv_module.BODY_CSV_NAME).exists()
        assert (tmp_path / csv_module.SERIES_CSV_NAME).exists()
        assert (tmp_path / csv_module.CONSIGNMENT_CSV_NAME).exists()
        assert (tmp_path / "AYR-file.csv").exists()
        assert (tmp_path / "AYR-file-metadata.csv").exists()
        assert (tmp_path / "AYR-av-metadata.csv").exists()

        body_row = read_rows(tmp_path, "AYR-body-metadata.csv")[0]
        assert body_row == {
            "BodyId": "",
            "Name": "Ministry of Test Data",
            "Description": "Ministry of Test Data",
        }

        series_row = read_rows(tmp_path, "AYR-series-metadata.csv")[0]
        assert series_row["Name"] == "LEV 2"
        assert series_row["Description"] == "LEV 2"

        consignment_row = read_rows(tmp_path, "AYR-consignment-metadata.csv")[0]
        assert consignment_row["ConsignmentReference"] == CONSIGNMENT_REFERENCE
        assert consignment_row["ConsignmentType"] == "Standard"
        assert consignment_row["IncludeTopLevelFolder"] == "false"
        assert consignment_row["CreatedDatetime"] == FIXED_NOW

        file_row = read_rows(tmp_path, "AYR-file.csv")[0]
        assert file_row["FileId"] == FILE_ID
        assert file_row["ConsignmentId"] == consignment_row["ConsignmentId"]
        assert file_row["FileName"] == "example.txt"
        assert file_row["FilePath"] == "LEV 2/2BD/example.txt"
        assert file_row["FileReference"] == "2BD/Z"
        assert file_row["CiteableReference"] == "LEV 2/2BD/Z"
        assert file_row["Checksum"] == "sha256-checksum"
        assert file_row["CreatedDatetime"] == FIXED_NOW

        assert read_rows(tmp_path, "AYR-av-metadata.csv") == []

    def test_convert_record_to_csv_writes_known_and_unmapped_metadata(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(csv_module, "utc_now_text", lambda: FIXED_NOW)

        record = make_record()
        digital_file = record["digitalFiles"][0]

        csv_module.convert_record_to_csv(
            record=record,
            digital_file=digital_file,
            output_dir=str(tmp_path),
            consignment_reference=CONSIGNMENT_REFERENCE,
            include_body_and_series=True,
            include_consignment=True,
        )

        metadata = metadata_values(read_rows(tmp_path, "AYR-file-metadata.csv"))

        assert metadata["description"] == ["Open public description"]
        assert metadata["description_alternate"] == [
            "Closed original description"
        ]
        assert metadata["description_closed"] == ["true"]
        assert metadata["title_alternate"] == ["Closed original title"]
        assert metadata["title_closed"] == ["true"]
        assert metadata["closure_type"] == ["Closed"]
        assert metadata["opening_date"] == ["2040-01-01"]
        assert metadata["foi_exemption_code"] == ["FOI 23;FOI 40"]
        assert metadata["rights_copyright"] == [
            "Crown copyright, Test copyright"
        ]

        assert metadata["dri_custom_record_field"] == ["keep this source value"]
        assert metadata["dri_digital_file_extra_digital_file_field"] == [
            "extra file value"
        ]

        checksum_metadata = json.loads(
            metadata["dri_digital_file_checksums"][0]
        )
        assert checksum_metadata == digital_file["checksums"]

    def test_convert_record_to_csv_ignores_list_containing_only_none(
        self, tmp_path
    ):
        record = make_record()
        record["nullableList"] = [None]

        csv_module.convert_record_to_csv(
            record=record,
            digital_file=record["digitalFiles"][0],
            output_dir=str(tmp_path),
            consignment_reference=CONSIGNMENT_REFERENCE,
            include_body_and_series=True,
            include_consignment=True,
        )

        metadata = metadata_values(read_rows(tmp_path, "AYR-file-metadata.csv"))

        assert "dri_nullable_list" not in metadata

    def test_convert_record_to_csv_omits_shared_and_consignment_csvs(
        self, tmp_path
    ):
        record = make_record()

        csv_module.convert_record_to_csv(
            record=record,
            digital_file=record["digitalFiles"][0],
            output_dir=str(tmp_path),
            consignment_reference=CONSIGNMENT_REFERENCE,
            include_body_and_series=False,
            include_consignment=False,
        )

        assert not (tmp_path / csv_module.BODY_CSV_NAME).exists()
        assert not (tmp_path / csv_module.SERIES_CSV_NAME).exists()
        assert not (tmp_path / csv_module.CONSIGNMENT_CSV_NAME).exists()
        assert (tmp_path / "AYR-file.csv").exists()
        assert (tmp_path / "AYR-file-metadata.csv").exists()
        assert (tmp_path / "AYR-av-metadata.csv").exists()

    def test_convert_record_to_csv_writes_consignment_without_shared_csvs(
        self, tmp_path
    ):
        record = make_record()

        csv_module.convert_record_to_csv(
            record=record,
            digital_file=record["digitalFiles"][0],
            output_dir=str(tmp_path),
            consignment_reference=CONSIGNMENT_REFERENCE,
            include_body_and_series=False,
            include_consignment=True,
        )

        assert not (tmp_path / csv_module.BODY_CSV_NAME).exists()
        assert not (tmp_path / csv_module.SERIES_CSV_NAME).exists()
        assert (tmp_path / csv_module.CONSIGNMENT_CSV_NAME).exists()

    def test_convert_record_to_csv_requires_consignment_reference(
        self, tmp_path
    ):
        record = make_record()

        with pytest.raises(ValueError, match="consignment_reference"):
            csv_module.convert_record_to_csv(
                record=record,
                digital_file=record["digitalFiles"][0],
                output_dir=str(tmp_path),
                consignment_reference=None,
                include_body_and_series=True,
                include_consignment=True,
            )

    def test_create_file_row_requires_file_name(self, tmp_path):
        record = make_record()
        digital_file = make_digital_file()
        del digital_file["fileName"]

        with pytest.raises(ValueError, match=r"digitalFiles\[\]\.fileName"):
            csv_module.convert_record_to_csv(
                record=record,
                digital_file=digital_file,
                output_dir=str(tmp_path),
                consignment_reference=CONSIGNMENT_REFERENCE,
                include_body_and_series=True,
                include_consignment=True,
            )

    def test_missing_is_record_closed_fails(self, tmp_path):
        record = make_record()
        del record["sensitivity"]["isRecordClosed"]

        with pytest.raises(ValueError, match=r"sensitivity\.isRecordClosed"):
            csv_module.convert_record_to_csv(
                record=record,
                digital_file=record["digitalFiles"][0],
                output_dir=str(tmp_path),
                consignment_reference=CONSIGNMENT_REFERENCE,
                include_body_and_series=True,
                include_consignment=True,
            )
