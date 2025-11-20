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
