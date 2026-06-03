import json
import subprocess
from pathlib import Path
from unittest import mock

import access_copy_converter.main as main_module
import boto3
import pytest
from access_copy_converter.main import (
    already_converted,
    convert_excel_to_pdf,
    convert_with_libreoffice,
    get_puid,
    process_consignment,
)
from moto import mock_aws
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    insert,
)
from sqlalchemy.exc import SQLAlchemyError


@pytest.fixture
def sqlite_conn():
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    ffid = Table(
        "FFIDMetadata",
        metadata,
        Column("Id", Integer, primary_key=True),
        Column("FileId", String, index=True),
        Column("PUID", String),
    )
    file_table = Table(
        "File",
        metadata,
        Column("Id", Integer, primary_key=True),
        Column("FileId", String, index=True),
    )
    metadata.create_all(engine)
    conn = engine.connect()
    try:
        yield conn, metadata, ffid, file_table
    finally:
        conn.close()
        engine.dispose()


class TestSetupHelpers:
    """Setup helper tests"""

    def test_get_secret_string(self, monkeypatch):
        fake_sm = mock.Mock()
        fake_sm.get_secret_value.return_value = {
            "SecretString": json.dumps({"username": "user"})
        }
        monkeypatch.setattr(main_module, "sm", fake_sm)

        result = main_module.get_secret_string("secret-id")

        assert result == {"username": "user"}

    def test_get_iam_connection(self, monkeypatch):
        fake_rds = mock.Mock()
        fake_rds.generate_db_auth_token.return_value = "token123"
        monkeypatch.setattr(main_module, "rds", fake_rds)

        result = main_module.get_iam_connection(
            {
                "proxy": "db.proxy",
                "port": "5432",
                "username": "dbuser",
            }
        )

        assert result == "token123"

    def test_get_engine_missing_db_secret_id(self, monkeypatch):
        monkeypatch.delenv("DB_SECRET_ID", raising=False)

        with pytest.raises(Exception) as exc:
            main_module.get_engine()

        assert "DB_SECRET_ID environment variable not found" in str(exc.value)

    def test_get_engine_success(self, monkeypatch):
        monkeypatch.setenv("DB_SECRET_ID", "db-secret")

        monkeypatch.setattr(
            main_module,
            "get_secret_string",
            lambda secret_id: {
                "username": "dbuser",
                "proxy": "db.proxy",
                "port": "5432",
                "dbname": "testdb",
            },
        )
        monkeypatch.setattr(
            main_module, "get_iam_connection", lambda creds: "token123"
        )

        create_engine_mock = mock.Mock(return_value="engine")
        monkeypatch.setattr(main_module, "create_engine", create_engine_mock)

        result = main_module.get_engine()

        assert result == "engine"
        create_engine_mock.assert_called_once()


class TestConvertedFiles:
    """S3 duplicate checking tests"""

    @mock_aws
    def test_already_converted_exists(self, monkeypatch):
        s3_client = boto3.client("s3", region_name="eu-west-2")
        s3_client.create_bucket(
            Bucket="bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        s3_client.put_object(Bucket="bucket", Key="key", Body=b"test")

        monkeypatch.setattr(main_module, "s3", s3_client)

        assert already_converted("bucket", "key") is True

    @mock_aws
    def test_already_converted_not_found(self, monkeypatch):
        s3_client = boto3.client("s3", region_name="eu-west-2")
        s3_client.create_bucket(
            Bucket="bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )

        monkeypatch.setattr(main_module, "s3", s3_client)

        assert already_converted("bucket", "key") is False

    @mock_aws
    def test_already_converted_other_error_logged(self, monkeypatch, caplog):
        s3_client = boto3.client("s3", region_name="eu-west-2")
        monkeypatch.setattr(main_module, "s3", s3_client)

        result = already_converted("nonexistent-bucket", "key")
        assert result is False
        assert "Error checking if key already converted" in caplog.text


class TestGetPUID:
    """File PUID detection tests"""

    def test_get_puid_from_ffid(self, sqlite_conn):
        conn, metadata, ffid, file_table = sqlite_conn
        conn.execute(insert(ffid).values(FileId="file123", PUID="fmt/40"))
        conn.commit()
        puid = get_puid("file123", conn, metadata)
        assert puid == "fmt/40"

    def test_get_puid_ffid_query_failure(self, monkeypatch, sqlite_conn):
        conn, metadata, ffid, file_table = sqlite_conn

        def execute_raise(stmt, *args, **kwargs):
            raise SQLAlchemyError("ffid error")

        monkeypatch.setattr(conn, "execute", execute_raise)
        with pytest.raises(Exception) as exc:
            get_puid("file123", conn, metadata)
        assert "Error querying FFIDMetadata table" in str(exc.value)

    def test_get_puid_returns_none_when_puid_is_null(self, sqlite_conn):
        conn, metadata, ffid, file_table = sqlite_conn
        conn.execute(insert(ffid).values(FileId="file123", PUID=None))
        conn.commit()

        puid = get_puid("file123", conn, metadata)

        assert puid is None


class TestConvertWithLibreoffice:
    """LibreOffice conversion tests"""

    def test_convert_with_libreoffice_success(self, monkeypatch, tmp_path):
        def fake_run(*args, **kwargs):
            mock_result = mock.Mock()
            mock_result.stderr = b""
            return mock_result

        monkeypatch.setattr(subprocess, "run", fake_run)
        in_path = str(tmp_path / "in.docx")
        out_path = str(tmp_path / "out.pdf")
        (tmp_path / "in.docx").write_text("dummy")
        convert_with_libreoffice(in_path, out_path)

    def test_convert_with_libreoffice_failure(self, monkeypatch, tmp_path):
        def fake_run(args, check, stderr):
            raise subprocess.CalledProcessError(
                1, args, stderr=b"conversion error"
            )

        monkeypatch.setattr(subprocess, "run", fake_run)
        in_path = str(tmp_path / "in.docx")
        out_path = str(tmp_path / "out.pdf")
        (tmp_path / "in.docx").write_text("dummy")
        with pytest.raises(RuntimeError):
            convert_with_libreoffice(in_path, out_path)

    def test_convert_with_libreoffice_stderr_triggers_error(
        self, monkeypatch, tmp_path
    ):
        def fake_run(*args, **kwargs):
            result = mock.Mock()
            result.stderr = b"conversion failed"
            return result

        monkeypatch.setattr(subprocess, "run", fake_run)

        in_path = str(tmp_path / "in.docx")
        out_path = str(tmp_path / "out.pdf")

        (tmp_path / "in.docx").write_text("dummy")

        with pytest.raises(RuntimeError) as exc:
            convert_with_libreoffice(in_path, out_path)

        assert "LibreOffice conversion failed" in str(exc.value)

    def test_convert_with_libreoffice_timeout(self, monkeypatch, tmp_path):
        def fake_run(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="soffice", timeout=300)

        monkeypatch.setattr(subprocess, "run", fake_run)

        in_path = str(tmp_path / "in.docx")
        out_path = str(tmp_path / "out.pdf")
        (tmp_path / "in.docx").write_text("dummy")

        with pytest.raises(RuntimeError) as exc:
            convert_with_libreoffice(in_path, out_path)

        assert "LibreOffice timed out after 300s converting" in str(exc.value)

    def test_convert_excel_to_pdf(self, monkeypatch, tmp_path):
        calls = []

        def fake_convert(input_path, output_path, convert_to="pdf"):
            calls.append((input_path, output_path, convert_to))

            from pathlib import Path

            Path(output_path).write_bytes(b"%PDF-1.4")

        monkeypatch.setattr(
            main_module, "convert_with_libreoffice", fake_convert
        )
        tmpdir = str(tmp_path)
        in_file = str(tmp_path / "input")
        out_file = str(tmp_path / "output.pdf")
        (tmp_path / "input.xlsx").write_bytes(b"dummy")
        convert_excel_to_pdf(tmpdir, in_file, out_file)
        assert len(calls) == 2
        assert calls[0][2] == "ods"
        assert calls[1][2].startswith("pdf")


class TestProcessConsignment:
    """Consignment processing integration tests"""

    @mock_aws
    def test_process_consignment_conversion_flow(
        self, monkeypatch, sqlite_conn
    ):
        s3_client = boto3.client("s3", region_name="eu-west-2")
        s3_client.create_bucket(
            Bucket="source-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        s3_client.create_bucket(
            Bucket="dest-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        s3_client.put_object(
            Bucket="source-bucket",
            Key="cons1/file123",
            Body=b"original content",
        )

        conn, metadata, ffid, file_table = sqlite_conn
        conn.execute(insert(ffid).values(FileId="file123", PUID="fmt/40"))
        conn.commit()

        monkeypatch.setattr(main_module, "s3", s3_client)

        def fake_convert(input_path, output_path, convert_to="pdf"):
            with open(output_path, "wb") as fh:
                fh.write(b"%PDF-1.4")

        monkeypatch.setattr(
            main_module, "convert_with_libreoffice", fake_convert
        )

        failed = process_consignment(
            "cons1",
            "source-bucket",
            "dest-bucket",
            conn,
        )

        # Verify the file was uploaded and no failures
        assert failed == []
        response = s3_client.list_objects_v2(
            Bucket="dest-bucket", Prefix="cons1/"
        )
        assert "Contents" in response
        assert len(response["Contents"]) == 1
        assert response["Contents"][0]["Key"] == "cons1/file123"

    @mock_aws
    def test_process_consignment_skips_nonconvertible(
        self, monkeypatch, sqlite_conn
    ):
        s3_client = boto3.client("s3", region_name="eu-west-2")
        s3_client.create_bucket(
            Bucket="src",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        s3_client.create_bucket(
            Bucket="dst",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
        s3_client.put_object(
            Bucket="src", Key="cons1/file123", Body=b"text content"
        )

        conn, metadata, ffid, file_table = sqlite_conn
        conn.execute(insert(ffid).values(FileId="file123", PUID="fmt/100000"))
        conn.commit()

        monkeypatch.setattr(main_module, "s3", s3_client)

        failed = process_consignment("cons1", "src", "dst", conn)

        assert failed == []
        # Verify no files were uploaded to destination
        response = s3_client.list_objects_v2(Bucket="dst", Prefix="cons1/")
        assert "Contents" not in response

    @mock_aws
    def test_multiple_consignments_reuse_connection(
        self, monkeypatch, sqlite_conn
    ):
        s3_client = boto3.client("s3", region_name="eu-west-2")
        for bucket in ["source-bucket", "dest-bucket"]:
            s3_client.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
            )
        s3_client.put_object(
            Bucket="source-bucket", Key="cons1/fileA", Body=b"A"
        )
        s3_client.put_object(
            Bucket="source-bucket", Key="cons2/fileB", Body=b"B"
        )

        monkeypatch.setattr(main_module, "s3", s3_client)

        conn, metadata, ffid, file_table = sqlite_conn
        conn.execute(insert(ffid).values(FileId="fileA", PUID="fmt/40"))
        conn.execute(insert(ffid).values(FileId="fileB", PUID="fmt/40"))
        conn.commit()

        def fake_convert(input_path, output_path, convert_to="pdf"):
            from pathlib import Path

            Path(output_path).write_bytes(b"%PDF-1.4")

        monkeypatch.setattr(
            main_module, "convert_with_libreoffice", fake_convert
        )

        failed1 = process_consignment(
            "cons1", "source-bucket", "dest-bucket", conn
        )
        failed2 = process_consignment(
            "cons2", "source-bucket", "dest-bucket", conn
        )

        assert failed1 == []
        assert failed2 == []

        resp = s3_client.list_objects_v2(Bucket="dest-bucket")
        uploaded_keys = [obj["Key"] for obj in resp.get("Contents", [])]
        assert "cons1/fileA" in uploaded_keys
        assert "cons2/fileB" in uploaded_keys

    @mock_aws
    def test_process_consignment_continues_on_conversion_failure(
        self, monkeypatch, sqlite_conn
    ):
        s3_client = boto3.client("s3", region_name="eu-west-2")
        for bucket in ["source-bucket", "dest-bucket"]:
            s3_client.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
            )

        for fname in ["file1", "file2", "file3"]:
            s3_client.put_object(
                Bucket="source-bucket", Key=f"cons1/{fname}", Body=b"data"
            )

        conn, metadata, ffid, file_table = sqlite_conn
        for fname in ["file1", "file2", "file3"]:
            conn.execute(insert(ffid).values(FileId=fname, PUID="fmt/40"))
        conn.commit()

        monkeypatch.setattr(main_module, "s3", s3_client)

        original_process_file = main_module.process_file

        def patched_process_file(file_id, *args, **kwargs):
            if file_id == "file2":
                raise RuntimeError("conversion fail")
            return original_process_file(file_id, *args, **kwargs)

        monkeypatch.setattr(main_module, "process_file", patched_process_file)

        failed = main_module.process_consignment(
            "cons1", "source-bucket", "dest-bucket", conn
        )

        assert "cons1/file2" in failed
        assert "cons1/file1" not in failed
        assert "cons1/file3" not in failed

        response = s3_client.list_objects_v2(
            Bucket="dest-bucket", Prefix="cons1/"
        )
        uploaded_keys = [obj["Key"] for obj in response.get("Contents", [])]
        assert "cons1/file1" in uploaded_keys
        assert "cons1/file3" in uploaded_keys
        assert "cons1/file2" not in uploaded_keys


class TestMain:
    """Main entrypoint tests"""

    def test_main_missing_app_secret_id(self, monkeypatch):
        monkeypatch.delenv("APP_SECRET_ID", raising=False)

        with pytest.raises(Exception) as exc:
            main_module.main()

        assert "APP_SECRET_ID environment variable not found" in str(exc.value)

    def test_main_all_conversion(self, monkeypatch):
        monkeypatch.setenv("APP_SECRET_ID", "app-secret")
        monkeypatch.setenv("CONVERSION_TYPE", "ALL")

        monkeypatch.setattr(
            main_module,
            "get_secret_string",
            lambda secret_id: {
                "RECORD_BUCKET_NAME": "source-bucket",
                "ACCESS_COPY_BUCKET": "dest-bucket",
            },
        )

        fake_conn = mock.Mock()
        fake_engine = mock.Mock()
        fake_engine.connect.return_value = fake_conn

        monkeypatch.setattr(main_module, "get_engine", lambda: fake_engine)

        all_mock = mock.Mock()
        monkeypatch.setattr(
            main_module,
            "create_access_copies_for_all_consignments",
            all_mock,
        )

        main_module.main()

        all_mock.assert_called_once_with(
            "source-bucket",
            "dest-bucket",
            fake_conn,
        )

    def test_main_single_conversion(self, monkeypatch):
        monkeypatch.setenv("APP_SECRET_ID", "app-secret")
        monkeypatch.setenv("CONVERSION_TYPE", "SINGLE")

        monkeypatch.setattr(
            main_module,
            "get_secret_string",
            lambda secret_id: {
                "RECORD_BUCKET_NAME": "source-bucket",
                "ACCESS_COPY_BUCKET": "dest-bucket",
            },
        )

        fake_conn = mock.Mock()
        fake_engine = mock.Mock()
        fake_engine.connect.return_value = fake_conn

        monkeypatch.setattr(main_module, "get_engine", lambda: fake_engine)

        single_mock = mock.Mock()
        monkeypatch.setattr(
            main_module,
            "create_access_copy_from_sns",
            single_mock,
        )

        main_module.main()

        single_mock.assert_called_once_with(
            "source-bucket",
            "dest-bucket",
            fake_conn,
        )

    def test_main_empty_conversion_type(self, monkeypatch):
        monkeypatch.setenv("APP_SECRET_ID", "app-secret")
        monkeypatch.setenv("CONVERSION_TYPE", "")

        monkeypatch.setattr(
            main_module,
            "get_secret_string",
            lambda secret_id: {
                "RECORD_BUCKET_NAME": "source-bucket",
                "ACCESS_COPY_BUCKET": "dest-bucket",
            },
        )

        with pytest.raises(Exception) as exc:
            main_module.main()

        assert "CONVERSION_TYPE environment variable not found" in str(
            exc.value
        )

    def test_main_invalid_conversion_type(self, monkeypatch):
        monkeypatch.setenv("APP_SECRET_ID", "app-secret")
        monkeypatch.setenv("CONVERSION_TYPE", "INVALID")

        monkeypatch.setattr(
            main_module,
            "get_secret_string",
            lambda secret_id: {
                "RECORD_BUCKET_NAME": "source-bucket",
                "ACCESS_COPY_BUCKET": "dest-bucket",
            },
        )

        fake_engine = mock.Mock()
        fake_engine.connect.return_value = mock.Mock()
        monkeypatch.setattr(main_module, "get_engine", lambda: fake_engine)

        with pytest.raises(ValueError) as exc:
            main_module.main()

        assert "Invalid CONVERSION_TYPE" in str(exc.value)


class TestTopLevelConversionFlows:
    """Top-level conversion flow tests"""

    def test_create_access_copies_for_all_consignments_success(
        self, monkeypatch
    ):
        class FakePaginator:
            def paginate(self, Bucket):
                return [
                    {
                        "Contents": [
                            {"Key": "cons1/file1"},
                            {"Key": "cons2/file2"},
                        ]
                    }
                ]

        fake_s3 = mock.Mock()
        fake_s3.get_paginator.return_value = FakePaginator()
        monkeypatch.setattr(main_module, "s3", fake_s3)

        processed = []

        def fake_process_consignment(
            consignment_ref, source_bucket, dest_bucket, conn
        ):
            processed.append(consignment_ref)
            return []

        monkeypatch.setattr(
            main_module, "process_consignment", fake_process_consignment
        )

        main_module.create_access_copies_for_all_consignments(
            "source-bucket", "dest-bucket", mock.Mock()
        )

        assert set(processed) == {"cons1", "cons2"}

    def test_create_access_copies_for_all_consignments_raises_on_failures(
        self, monkeypatch
    ):
        class FakePaginator:
            def paginate(self, Bucket):
                return [{"Contents": [{"Key": "cons1/file1"}]}]

        fake_s3 = mock.Mock()
        fake_s3.get_paginator.return_value = FakePaginator()
        monkeypatch.setattr(main_module, "s3", fake_s3)

        monkeypatch.setattr(
            main_module,
            "process_consignment",
            lambda consignment_ref, source_bucket, dest_bucket, conn: [
                "cons1/file1"
            ],
        )

        with pytest.raises(RuntimeError) as exc:
            main_module.create_access_copies_for_all_consignments(
                "source-bucket", "dest-bucket", mock.Mock()
            )

        assert "Conversion failed for 1 file(s)" in str(exc.value)
        assert "cons1/file1" in str(exc.value)

    def test_create_access_copies_for_all_consignments_empty(self, monkeypatch):
        class FakePaginator:
            def paginate(self, Bucket):
                return []

        fake_s3 = mock.Mock()
        fake_s3.get_paginator.return_value = FakePaginator()
        monkeypatch.setattr(main_module, "s3", fake_s3)

        process_mock = mock.Mock()
        monkeypatch.setattr(main_module, "process_consignment", process_mock)

        main_module.create_access_copies_for_all_consignments(
            "source-bucket", "dest-bucket", mock.Mock()
        )

        process_mock.assert_not_called()

    def test_create_access_copy_from_sns_missing_message(self, monkeypatch):
        monkeypatch.delenv("SNS_MESSAGE", raising=False)

        with pytest.raises(Exception) as exc:
            main_module.create_access_copy_from_sns(
                "source-bucket", "dest-bucket", mock.Mock()
            )

        assert "SNS_MESSAGE environment variable not found" in str(exc.value)

    def test_create_access_copy_from_sns_invalid_json(
        self, monkeypatch, caplog
    ):
        monkeypatch.setenv("SNS_MESSAGE", "not json")

        with pytest.raises(Exception):
            main_module.create_access_copy_from_sns(
                "source-bucket", "dest-bucket", mock.Mock()
            )

        assert "Error parsing SNS_MESSAGE" in caplog.text

    def test_create_access_copy_from_sns_missing_reference(self, monkeypatch):
        monkeypatch.setenv("SNS_MESSAGE", json.dumps({"parameters": {}}))

        with pytest.raises(Exception) as exc:
            main_module.create_access_copy_from_sns(
                "source-bucket", "dest-bucket", mock.Mock()
            )

        assert "Missing consignment_reference in SNS Message" in str(exc.value)

    def test_create_access_copy_from_sns_success(self, monkeypatch):
        monkeypatch.setenv(
            "SNS_MESSAGE",
            json.dumps({"parameters": {"reference": "cons1"}}),
        )

        called = {}

        def fake_process_consignment(
            consignment_ref, source_bucket, dest_bucket, conn
        ):
            called["consignment_ref"] = consignment_ref
            called["source_bucket"] = source_bucket
            called["dest_bucket"] = dest_bucket
            called["conn"] = conn
            return []

        monkeypatch.setattr(
            main_module, "process_consignment", fake_process_consignment
        )

        conn = mock.Mock()
        main_module.create_access_copy_from_sns(
            "source-bucket", "dest-bucket", conn
        )

        assert called["consignment_ref"] == "cons1"
        assert called["source_bucket"] == "source-bucket"
        assert called["dest_bucket"] == "dest-bucket"
        assert called["conn"] == conn

    def test_create_access_copy_from_sns_raises_on_failures(self, monkeypatch):
        monkeypatch.setenv(
            "SNS_MESSAGE",
            json.dumps({"parameters": {"reference": "cons1"}}),
        )

        monkeypatch.setattr(
            main_module,
            "process_consignment",
            lambda consignment_ref, source_bucket, dest_bucket, conn: [
                "cons1/file1"
            ],
        )

        with pytest.raises(RuntimeError) as exc:
            main_module.create_access_copy_from_sns(
                "source-bucket", "dest-bucket", mock.Mock()
            )

        assert "Conversion failed for 1 file(s)" in str(exc.value)
        assert "cons1/file1" in str(exc.value)


class TestLibreOfficeRealConversion:
    @pytest.mark.parametrize(
        "input_file, expected_pdf, converter",
        [
            (
                "doc_integration_test.doc",
                "doc_integration_test.pdf",
                convert_with_libreoffice,
            ),
            (
                "docx_integration_test.docx",
                "docx_integration_test.pdf",
                convert_with_libreoffice,
            ),
            (
                "xls_integration_test.xls",
                "xls_integration_test.pdf",
                convert_excel_to_pdf,
            ),
            (
                "xlsx_integration_test.xlsx",
                "xlsx_integration_test.pdf",
                convert_excel_to_pdf,
            ),
        ],
    )
    def test_real_conversion(
        self,
        tmp_path: Path,
        input_file: str,
        expected_pdf: str,
        converter,
    ):
        repo_root = Path(__file__).resolve().parents[3]
        input_path = (
            repo_root / "data_management/integration_test_files" / input_file
        )
        output_path = tmp_path / expected_pdf

        if converter is convert_excel_to_pdf:
            converter(str(tmp_path), str(input_path), str(output_path))
        else:
            converter(str(input_path), str(output_path))

        assert output_path.exists()
        data = output_path.read_bytes()
        assert data.startswith(b"%PDF-")
