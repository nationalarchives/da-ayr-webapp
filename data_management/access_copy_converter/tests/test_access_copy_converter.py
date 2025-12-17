import subprocess
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


class TestMainModuleCoverage:
    def test_main_invalid_conversion_type(self, monkeypatch):
        monkeypatch.setenv("APP_SECRET_ID", "x")
        monkeypatch.setenv("CONVERSION_TYPE", "INVALID")
        monkeypatch.setattr(
            main_module,
            "get_secret_string",
            lambda x: {
                "RECORD_BUCKET_NAME": "src",
                "ACCESS_COPY_BUCKET": "dst",
            },
        )
        monkeypatch.setattr(
            main_module,
            "get_engine",
            lambda: mock.Mock(connect=lambda: mock.Mock()),
        )

        class DummySM:
            def get_secret_value(self, SecretId):
                return {
                    "SecretString": '{"RECORD_BUCKET_NAME": "src", "ACCESS_COPY_BUCKET": "dst"}'
                }

        class DummyS3:
            def download_file(self, *a, **k):
                pass

            def upload_file(self, *a, **k):
                pass

            def get_paginator(self, *a, **k):
                class DummyPaginator:
                    def paginate(self, *a, **k):
                        return []

                return DummyPaginator()

            def head_object(self, *a, **k):
                raise Exception("not found")

        monkeypatch.setattr(main_module, "sm", DummySM())
        monkeypatch.setattr(main_module, "s3", DummyS3())
        with pytest.raises(ValueError) as exc:
            main_module.main()
        assert "Invalid CONVERSION_TYPE" in str(exc.value)

    def test_create_access_copy_from_sns_missing_env(self, monkeypatch):
        monkeypatch.delenv("SNS_MESSAGE", raising=False)
        with pytest.raises(Exception) as exc:
            main_module.create_access_copy_from_sns("src", "dst", mock.Mock())
        assert "SNS_MESSAGE environment variable not found" in str(exc.value)

    def test_create_access_copy_from_sns_missing_reference(self, monkeypatch):
        monkeypatch.setenv("SNS_MESSAGE", "{}")
        with pytest.raises(Exception) as exc:
            main_module.create_access_copy_from_sns("src", "dst", mock.Mock())
        assert "Missing consignment_reference" in str(exc.value)

    def test_create_access_copies_for_all_consignments_failure(
        self, monkeypatch
    ):
        # Simulate a failed file conversion
        class DummyPaginator:
            def paginate(self, *a, **k):
                return [{"Contents": [{"Key": "cons1/file1"}]}]

        class DummyS3:
            def get_paginator(self, *a, **k):
                return DummyPaginator()

        monkeypatch.setattr(main_module, "s3", DummyS3())

        def process_consignment(*a, **k):
            return ["cons1/file1"]

        monkeypatch.setattr(
            main_module, "process_consignment", process_consignment
        )
        with pytest.raises(RuntimeError) as exc:
            main_module.create_access_copies_for_all_consignments(
                "src", "dst", mock.Mock()
            )
        assert "Conversion failed for 1 file(s)" in str(exc.value)

    def test_create_access_copy_from_sns_failure(self, monkeypatch):
        # Simulate a failed file conversion in SNS path
        monkeypatch.setenv(
            "SNS_MESSAGE", '{"parameters": {"reference": "cons1"}}'
        )

        def process_consignment(*a, **k):
            return ["cons1/file1"]

        monkeypatch.setattr(
            main_module, "process_consignment", process_consignment
        )
        with pytest.raises(RuntimeError) as exc:
            main_module.create_access_copy_from_sns("src", "dst", mock.Mock())
        assert "Conversion failed for 1 file(s)" in str(exc.value)

    def test_get_secret_string_success(self, monkeypatch):
        class FakeSM:
            def get_secret_value(self, SecretId):
                return {
                    "SecretString": '{"username": "username", '  # pragma: allowlist secret
                    '"password": "password", '  # pragma: allowlist secret
                    '"proxy": "localhost", '  # pragma: allowlist secret
                    '"port": 5433, "dbname": "db_name", '  # pragma: allowlist secret
                    '"RECORD_BUCKET_NAME": "src", '  # pragma: allowlist secret
                    '"ACCESS_COPY_BUCKET": "dst"}'  # pragma: allowlist secret
                }

        monkeypatch.setattr(main_module, "sm", FakeSM())
        secret = main_module.get_secret_string("fakeid")
        assert secret["username"] == "username"

    def test_get_secret_string_failure(self, monkeypatch):
        class FakeSM:
            def get_secret_value(self, SecretId):
                raise Exception("fail")

        monkeypatch.setattr(main_module, "sm", FakeSM())
        with pytest.raises(Exception):
            main_module.get_secret_string("fakeid")

    def test_get_engine_env_missing(self, monkeypatch):
        monkeypatch.delenv("DB_SECRET_ID", raising=False)
        with pytest.raises(Exception) as exc:
            main_module.get_engine()
        assert "DB_SECRET_ID environment variable not found" in str(exc.value)

    def test_download_input_error(self, monkeypatch):
        def fail_download(*a, **k):
            raise Exception("fail download")

        monkeypatch.setattr(
            main_module, "s3", mock.Mock(download_file=fail_download)
        )
        with pytest.raises(Exception) as exc:
            main_module._download_input("b", "k", "p")
        assert "Failed to download" in str(exc.value)

    def test_upload_output_error(self, monkeypatch, tmp_path):
        def fail_upload(*a, **k):
            raise Exception("fail upload")

        monkeypatch.setattr(
            main_module, "s3", mock.Mock(upload_file=fail_upload)
        )
        f = tmp_path / "f.pdf"
        f.write_bytes(b"x")
        with pytest.raises(Exception) as exc:
            main_module._upload_output(str(f), "b", "k", "id")
        assert "Failed to upload" in str(exc.value)

    def test_cleanup_soffice_processes(self, monkeypatch):
        class FakeProc:
            def __init__(self, name, fail_kill=False):
                self.info = {"name": name}
                self.pid = 1
                self._fail = fail_kill

            def kill(self):
                if self._fail:
                    raise Exception("fail kill")

        monkeypatch.setattr(
            main_module.psutil,
            "process_iter",
            lambda attrs: [
                FakeProc("soffice"),
                FakeProc("soffice.bin", True),
                FakeProc("other"),
            ],
        )
        # Should not raise
        main_module._cleanup_soffice_processes()

    def test_main_env_errors(self, monkeypatch):
        # Test missing APP_SECRET_ID
        monkeypatch.delenv("APP_SECRET_ID", raising=False)
        monkeypatch.setenv("CONVERSION_TYPE", "ALL")  # Prevent AWS call
        with pytest.raises(Exception) as exc:
            main_module.main()
        assert "APP_SECRET_ID environment variable not found" in str(exc.value)

        # Test missing CONVERSION_TYPE should NOT raise (defaults to 'ALL')
        monkeypatch.setenv("APP_SECRET_ID", "x")
        monkeypatch.setattr(
            main_module,
            "get_secret_string",
            lambda x: {
                "RECORD_BUCKET_NAME": "src",
                "ACCESS_COPY_BUCKET": "dst",
            },
        )

        class DummySM:
            def get_secret_value(self, SecretId):
                return {
                    "SecretString": '{"RECORD_BUCKET_NAME": "src", "ACCESS_COPY_BUCKET": "dst"}'
                }

        class DummyS3:
            def download_file(self, *a, **k):
                pass

            def upload_file(self, *a, **k):
                pass

            def get_paginator(self, *a, **k):
                class DummyPaginator:
                    def paginate(self, *a, **k):
                        return []

                return DummyPaginator()

            def head_object(self, *a, **k):
                raise Exception("not found")

        monkeypatch.setattr(main_module, "sm", DummySM())
        monkeypatch.setattr(main_module, "s3", DummyS3())
        monkeypatch.delenv("CONVERSION_TYPE", raising=False)
        monkeypatch.setattr(
            main_module,
            "get_engine",
            lambda: mock.Mock(connect=lambda: mock.Mock()),
        )
        # Should NOT raise
        main_module.main()


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
