import argparse
import json
import os
import secrets
import string
import uuid
from datetime import UTC, datetime
from pathlib import Path

import boto3
from botocore.client import Config
from dotenv import load_dotenv
from index_file_content_and_metadata_in_opensearch import (
    index_file_content_and_metadata_in_opensearch,
)
from requests_aws4auth import AWS4Auth

from app import create_app, db
from app.main.db.models import Body, File, Series
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FFIDMetadataFactory,
    FileFactory,
    FileMetadataFactory,
    SeriesFactory,
)
from configs.env_config import EnvConfig

load_dotenv()


def get_s3_client():
    """Get a S3 client for MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
        aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
        config=Config(signature_version="s3v4"),
        region_name="eu-west-2",
    )


def ensure_bucket_exists(bucket_name):
    """Ensure the S3 bucket exists, create it if it doesn't."""
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=bucket_name)
    except Exception:
        s3.create_bucket(Bucket=bucket_name)
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicRead",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
                }
            ],
        }
        s3.put_bucket_policy(
            Bucket=bucket_name, Policy=json.dumps(bucket_policy)
        )


def upload_file_to_s3(file_path, s3_key):
    """Upload a file to MinIO."""
    s3 = get_s3_client()
    bucket = os.getenv("RECORD_BUCKET_NAME")

    ensure_bucket_exists(bucket)

    with open(file_path, "rb") as file_data:
        s3.put_object(
            Bucket=bucket, Key=s3_key, Body=file_data.read(), ACL="public-read"
        )


def create_test_filepaths(file_type_counts):
    """
    Instead of copying files, generate random file IDs and pair them with
    example files by file type.

    Returns:
        List of tuples: (file_id: str, file_ext: str, source_path: Path)
    """
    example_files = Path("local_services/mds_data_generator/example_files")

    example_file_paths = {
        f.suffix.lstrip("."): example_files / f.name
        for f in example_files.iterdir()
        if f.is_file() and f.suffix.lstrip(".")
    }

    created_files = []

    for ext, count in file_type_counts.items():
        source_path = example_file_paths.get(ext)

        for _ in range(count):
            file_id = str(uuid.uuid4())
            created_files.append((file_id, ext, source_path))

    return created_files


def process_files(files):
    """
    files: List of tuples (file_id: str, file_ext: str, source_path: Path)

    For each file:
    - Upload example file from source_path to S3 using file_id as key
    - Create DB entries with FileFactory and metadata
    """
    app = create_app(EnvConfig)
    with app.app_context():
        try:
            body = (
                db.session.query(Body)
                .filter_by(Name="Test Transferring Body")
                .first()
            )
            if not body:
                body = BodyFactory.create(
                    Name="Test Transferring Body",
                    Description="Test Transferring Body Description",
                )

            series = (
                db.session.query(Series)
                .filter_by(Name="SCOT 13", body=body)
                .first()
            )
            if not series:
                series = SeriesFactory.create(
                    body=body,
                    Name="SCOT 13",
                    Description="Test Series Description",
                )

            timestamp = datetime.now(UTC).strftime("%Y")
            random_string = "".join(
                secrets.choice(string.ascii_uppercase + string.digits)
                for _ in range(4)
            )
            consignment_ref = f"AYR-{timestamp}-{random_string}"

            consignment = ConsignmentFactory.create(
                series=series,
                BodyId=body.BodyId,
                ConsignmentReference=consignment_ref,
                ConsignmentType="Test",
                IncludeTopLevelFolder=True,
                ContactName="Test User",
                ContactEmail="test@example.com",
                TransferStartDatetime=datetime.now(UTC),
                CreatedDatetime=datetime.now(UTC),
            )

            mime_types = {
                # Assigning PUIDs to correct extensions as sets
                "pdf": {"application/pdf", "fmt/276"},
                "doc": {"application/msword", "fmt/40"},
                "docx": {
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "fmt/412",
                },
                "ppt": {"application/vnd.ms-powerpoint", "fmt/214"},
                "pptx": {
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    "fmt/126",
                },
                "wk1": {"application/vnd.lotus-1-2-3", "x-fmt/44"},
                "wk4": {"application/vnd.lotus-1-2-3", "x-fmt/45"},
                "wpd": {"application/wordperfect", "fmt/355"},
                "rtf": {"application/rtf", "fmt/61"},
                "xls": {"application/vnd.ms-excel", "fmt/59"},
                "xlsx": {
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "fmt/215",
                },
                "xml": {"application/xml", "fmt/50"},
                "odt": {"application/vnd.oasis.opendocument.text", "fmt/39"},
                "html": {"text/html", "x-fmt/394"},
                "png": {"image/png", "x-fmt/116"},
                "jpg": {"image/jpeg", "x-fmt/111"},
                "txt": {"text/plain"},
            }

            format_names = {
                "pdf": "PDF",
                "doc": "Microsoft Word Document",
                "docx": "Microsoft Word Open XML Document",
                "ppt": "Microsoft PowerPoint Presentation",
                "pptx": "Microsoft PowerPoint Open XML Presentation",
                "wk1": "Lotus 1-2-3 Spreadsheet",
                "wk4": "Lotus 1-2-3 Spreadsheet",
                "wpd": "WordPerfect Document",
                "rtf": "Rich Text Format",
                "xls": "Microsoft Excel Spreadsheet",
                "xlsx": "Microsoft Excel Open XML Spreadsheet",
                "xml": "Extensible Markup Language",
                "odt": "OpenDocument Text",
                "html": "HyperText Markup Language",
                "png": "Portable Network Graphics",
                "jpg": "JPEG Image",
                "txt": "Plain Text",
            }

            for i, (file_id, file_ext, source_path) in enumerate(files):
                filename = source_path.name
                try:
                    upload_file_to_s3(
                        source_path, f"{consignment_ref}/{file_id}"
                    )
                except Exception as e:
                    print(f"Failed to upload {filename}: {e}")
                    continue  # Skip DB entry if upload fails

                ffid_metadata = FFIDMetadataFactory.create(
                    FileId=file_id,
                    Extension=file_ext,
                    PUID=next(
                        (
                            m
                            for m in mime_types.get(file_ext, set())
                            if m.startswith("fmt/") or m.startswith("x-fmt/")
                        ),
                        None,
                    ),
                    FormatName=format_names.get(file_ext, "Unknown"),
                )

                file = FileFactory.create(
                    FileId=file_id,
                    consignment=consignment,
                    FileName=filename,
                    FileType="File",
                    FilePath=f"data/content/{filename}",
                    FileReference="".join(
                        secrets.choice(string.ascii_uppercase + string.digits)
                        for _ in range(4)
                    ),
                    CreatedDatetime=datetime.now(UTC),
                    CiteableReference=f"CITE-{i + 1:04d}",
                    ffid_metadata=ffid_metadata,
                )

                metadata_dict = {
                    "source": "test_file",
                    "file_name": filename,
                    "file_type": "File",
                    "file_size": str(os.path.getsize(source_path)),
                    "rights_copyright": "Crown Copyright",
                    "legal_status": "Public Record(s)",
                    "held_by": "The National Archives",
                    "date_last_modified": datetime.now(UTC).isoformat(),
                    "description": "Test file for AYR development",
                    "closure_type": "Open",
                    "title_closed": "false",
                    "description_closed": "false",
                    "language": "English",
                    "created_at": datetime.now(UTC).isoformat(),
                    "last_transfer_date": datetime.now(UTC).isoformat(),
                    "file_format": file_ext.upper(),
                    "file_extension": file_ext,
                    "closure_status": "Open",
                    "closure_period": "0",
                    "foi_exemption_code": "None",
                    "foi_exemption_code_description": "None",
                    "title": f"Test File {i + 1}",
                }

                for key, value in metadata_dict.items():
                    FileMetadataFactory.create(
                        FileId=file_id,
                        file=file,
                        PropertyName=key,
                        Value=value,
                        CreatedDatetime=datetime.now(UTC),
                    )

                print(f"Processed file: {filename} (ID: {file_id})")
            print(f"Creating consignment with reference: {consignment_ref}")
            db.session.commit()

        except Exception as e:
            print(f"Error processing files: {e}")
            db.session.rollback()
            raise


def index_in_opensearch(files):
    """Index each processed file in OpenSearch."""
    app = create_app(EnvConfig)
    with app.app_context():
        try:

            s3 = get_s3_client()
            bucket = os.getenv("RECORD_BUCKET_NAME")

            aws_service = "es"
            aws_region = os.getenv("AWS_REGION")
            aws_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")

            open_search_host_url = os.getenv("OPEN_SEARCH_HOST_URL")
            open_search_http_auth = AWS4Auth(
                aws_key, aws_secret, aws_region, aws_service
            )
            database_url = app.config["SQLALCHEMY_DATABASE_URI"]

            for file_id, file_ext, file_path in files:
                file = db.session.query(File).filter_by(FileId=file_id).first()
                if file is None:
                    print(f"File with ID {file_id} not found in DB, skipping.")
                    continue

                filename = os.path.basename(file_path)
                file_id = file.FileId
                consignment_ref = file.consignment.ConsignmentReference

                try:
                    s3_key = f"{consignment_ref}/{file_id}"
                    response = s3.get_object(Bucket=bucket, Key=s3_key)
                    file_stream = response["Body"].read()

                    index_file_content_and_metadata_in_opensearch(
                        file_id,
                        file_stream,
                        database_url,
                        open_search_host_url,
                        open_search_http_auth,
                    )

                    print(
                        f"Successfully indexed file: {filename} (ID: {file_id})"
                    )

                except Exception as e:
                    print(
                        f"Error indexing file {filename} (ID: {file_id}): {e}"
                    )

        except Exception as e:
            print(f"Error during OpenSearch indexing: {e}")


def main():
    """
    Generate and process test files for AYR testing using Factory Boy.

    Example usage:
        python mds_test_file_importer.py --num-pdf 2 --num-png 1
        if no args are passed, the default will be 1 of each file
    """
    parser = argparse.ArgumentParser(
        description="Generate and process test files for AYR testing"
    )
    example_files = Path("local_services/mds_data_generator/example_files")
    file_types = sorted(
        {
            f.suffix.lstrip(".")
            for f in example_files.iterdir()
            if f.is_file() and f.suffix.lstrip(".")
        }
    )
    for ext in file_types:
        parser.add_argument(
            f"--num-{ext}",
            type=int,
            default=1,
            help=f"Number of {ext.upper()} files to create",
        )

    args = parser.parse_args()

    file_type_counts = {ext: getattr(args, f"num_{ext}") for ext in file_types}

    file_paths = create_test_filepaths(file_type_counts)
    process_files(file_paths)
    index_in_opensearch(file_paths)
    print("Successfully processed files")


if __name__ == "__main__":
    main()
