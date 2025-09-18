import subprocess
from unittest import mock

import access_copy_converter.main as converter
import pytest
from botocore.exceptions import ClientError
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


@pytest.fixture(autouse=True)
def patch_boto_clients(monkeypatch):
    s3 = mock.Mock()
    sm = mock.Mock()
    monkeypatch.setattr(converter, "s3", s3)
    monkeypatch.setattr(converter, "sm", sm)
    return {"s3": s3, "sm": sm}


@pytest.fixture
def sqlite_conn():
    engine = create_engine("sqlite:///:memory:")
    metadata = MetaData()
    ffid = Table(
        "FFIDMetadata",
        metadata,
        Column("Id", Integer, primary_key=True),
        Column("FileId", String, index=True),
        Column("Extension", String),
    )
    file_table = Table(
        "File",
        metadata,
        Column("Id", Integer, primary_key=True),
        Column("FileId", String, index=True),
        Column("FileName", String),
    )
    metadata.create_all(engine)
    conn = engine.connect()
    try:
        yield conn, metadata, ffid, file_table
    finally:
        conn.close()
        engine.dispose()


def test_already_converted_exists(patch_boto_clients):
    s3 = patch_boto_clients["s3"]
    s3.head_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}
    assert converter.already_converted("bucket", "key") is True
    s3.head_object.assert_called_once_with(Bucket="bucket", Key="key")


def test_already_converted_not_found(patch_boto_clients):
    s3 = patch_boto_clients["s3"]
    err = ClientError({"Error": {"Code": "404"}}, "HeadObject")
    s3.head_object.side_effect = err
    assert converter.already_converted("bucket", "key") is False


def test_already_converted_other_error_raises(patch_boto_clients):
    s3 = patch_boto_clients["s3"]
    err = ClientError({"Error": {"Code": "500"}}, "HeadObject")
    s3.head_object.side_effect = err
    with pytest.raises(ClientError):
        converter.already_converted("bucket", "key")


def test_get_extension_from_ffid(sqlite_conn):
    conn, metadata, ffid, file_table = sqlite_conn
    conn.execute(insert(ffid).values(FileId="file123", Extension="DOCX"))
    conn.commit()
    ext = converter.get_extension("file123", conn, metadata)
    assert ext == "docx"


def test_get_extension_from_filename(sqlite_conn):
    conn, metadata, ffid, file_table = sqlite_conn
    conn.execute(
        insert(file_table).values(FileId="file123", FileName="report.PDF")
    )
    conn.commit()
    ext = converter.get_extension("file123", conn, metadata)
    assert ext == "pdf"


def test_get_extension_no_extension_and_warning(sqlite_conn, caplog):
    conn, metadata, ffid, file_table = sqlite_conn
    conn.execute(
        insert(file_table).values(FileId="file123", FileName="noextfile")
    )
    conn.commit()
    caplog.set_level("WARNING")
    ext = converter.get_extension("file123", conn, metadata)
    assert ext is None
    assert "No extension in FileName" in caplog.text


def test_get_extension_ffid_query_failure(monkeypatch, sqlite_conn):
    conn, metadata, ffid, file_table = sqlite_conn
    orig_execute = conn.execute

    def execute_raise(stmt, *args, **kwargs):
        s = str(stmt).lower()
        if "ffidmetadata" in s:
            raise SQLAlchemyError("ffid error")
        return orig_execute(stmt, *args, **kwargs)

    monkeypatch.setattr(conn, "execute", execute_raise)
    with pytest.raises(Exception) as exc:
        converter.get_extension("file123", conn, metadata)
    assert "Error querying FFIDMetadata table" in str(exc.value)


def test_get_extension_file_query_failure(monkeypatch, sqlite_conn):
    conn, metadata, ffid, file_table = sqlite_conn

    def execute_raise(stmt, *args, **kwargs):
        s = str(stmt).lower()

        if "ffidmetadata" in s:
            return type("R", (), {"first": lambda self=None: None})()

        raise SQLAlchemyError("file error")

    monkeypatch.setattr(conn, "execute", execute_raise)
    with pytest.raises(Exception) as exc:
        converter.get_extension("file123", conn, metadata)
    assert "Error querying File table" in str(exc.value)


def test_convert_with_libreoffice_success(monkeypatch, tmp_path):
    def fake_run(args, check, stderr):
        return mock.Mock()

    monkeypatch.setattr(subprocess, "run", fake_run)
    in_path = str(tmp_path / "in.docx")
    out_path = str(tmp_path / "out.pdf")
    (tmp_path / "in.docx").write_text("dummy")
    converter.convert_with_libreoffice(in_path, out_path)


def test_convert_with_libreoffice_failure(monkeypatch, tmp_path):
    def fake_run(args, check, stderr):
        raise subprocess.CalledProcessError(1, args, stderr=b"conversion error")

    monkeypatch.setattr(subprocess, "run", fake_run)
    in_path = str(tmp_path / "in.docx")
    out_path = str(tmp_path / "out.pdf")
    (tmp_path / "in.docx").write_text("dummy")
    with pytest.raises(RuntimeError):
        converter.convert_with_libreoffice(in_path, out_path)


def test_convert_xls_xlsx_to_pdf(monkeypatch, tmp_path):
    calls = []

    def fake_convert(input_path, output_path, convert_to="pdf"):
        calls.append((input_path, output_path, convert_to))

        from pathlib import Path

        Path(output_path).write_bytes(b"%PDF-1.4")

    monkeypatch.setattr(converter, "convert_with_libreoffice", fake_convert)
    tmpdir = str(tmp_path)
    in_file = str(tmp_path / "input.xlsx")
    out_file = str(tmp_path / "output.pdf")
    (tmp_path / "input.xlsx").write_bytes(b"dummy")
    converter.convert_xls_xlsx_to_pdf(tmpdir, in_file, out_file)
    assert len(calls) == 2
    assert calls[0][2] == "ods"
    assert calls[1][2].startswith("pdf")


def test_process_consignment_conversion_flow(
    monkeypatch, patch_boto_clients, sqlite_conn
):
    s3 = patch_boto_clients["s3"]
    s3.list_objects_v2.return_value = {"Contents": [{"Key": "cons1/file123"}]}
    s3.head_object.side_effect = ClientError(
        {"Error": {"Code": "404"}}, "HeadObject"
    )

    def fake_download(bucket, key, filename):
        with open(filename, "wb") as fh:
            fh.write(b"original content")

    s3.download_file.side_effect = fake_download
    s3.upload_file = mock.Mock()

    conn, metadata, ffid, file_table = sqlite_conn
    conn.execute(insert(ffid).values(FileId="file123", Extension="docx"))
    conn.commit()

    class DummyEngine:
        def connect(self):
            return mock.MagicMock(
                __enter__=lambda self: conn, __exit__=lambda *a: None
            )

    monkeypatch.setattr(converter, "get_engine", lambda: DummyEngine())

    def fake_convert(input_path, output_path, convert_to="pdf"):
        with open(output_path, "wb") as fh:
            fh.write(b"%PDF-1.4")

    monkeypatch.setattr(converter, "convert_with_libreoffice", fake_convert)

    converter.process_consignment(
        "cons1", "source-bucket", "dest-bucket", {"docx", "xls", "xlsx"}
    )

    assert (
        s3.upload_file.called
    ), "Expected s3.upload_file to be called but it was not"
    called_args = s3.upload_file.call_args[0]
    assert called_args[1] == "dest-bucket"
    assert called_args[2] == "cons1/file123"


def test_process_consignment_skips_nonconvertible(
    monkeypatch, patch_boto_clients, sqlite_conn
):
    s3 = patch_boto_clients["s3"]
    s3.list_objects_v2.return_value = {"Contents": [{"Key": "cons1/file123"}]}
    s3.head_object.side_effect = ClientError(
        {"Error": {"Code": "404"}}, "HeadObject"
    )

    conn, metadata, ffid, file_table = sqlite_conn
    conn.execute(insert(ffid).values(FileId="file123", Extension="txt"))
    conn.commit()

    class DummyEngine:
        def connect(self):
            return mock.MagicMock(
                __enter__=lambda self: conn, __exit__=lambda *a: None
            )

    monkeypatch.setattr(converter, "get_engine", lambda: DummyEngine())

    s3.upload_file = mock.Mock()
    converter.process_consignment(
        "cons1", "src", "dst", convertible_extensions={"docx", "xls", "xlsx"}
    )
    s3.upload_file.assert_not_called()
