import argparse
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

import boto3
from botocore.client import Config
from dotenv import load_dotenv
from requests_aws4auth import AWS4Auth

from app import create_app, db
from app.main.db.models import Body, File, Series
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    FileMetadataFactory,
    SeriesFactory,
)
from configs.env_config import EnvConfig
from data_management.opensearch_indexer.opensearch_indexer.index_file_content_and_metadata_in_opensearch import (
    index_file_content_and_metadata_in_opensearch,
)

load_dotenv()


def get_s3_client():
    """Get a S3 client for MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
        aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
        verify=False,
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
            Bucket=bucket, Key=s3_key, Body=file_data, ACL="public-read"
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
        "pdf": example_files / "file.pdf",
        "png": example_files / "file.png",
        "jpg": example_files / "file.jpg",
        "tiff": example_files / "file.tiff",
        "txt": example_files / "file.txt",
        "epub": example_files / "file.epub",
        "gif": example_files / "file.gif",
        "svg": example_files / "file.svg",
        "jp2": example_files / "file.jp2",
        "webp": example_files / "file.webp",
        "mp3": example_files / "file.mp3",
        "wav": example_files / "file.wav",
        "ogg": example_files / "file.ogg",
        "m4a": example_files / "file.m4a",
        "flac": example_files / "file.flac",
        "mp4": example_files / "file.mp4",
        "webm": example_files / "file.webm",
        "mpeg": example_files / "file.mpeg",
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
                .filter_by(Name="Test Series", body=body)
                .first()
            )
            if not series:
                series = SeriesFactory.create(
                    body=body,
                    Name="Test Series",
                    Description="Test Series Description",
                )

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            consignment_ref = f"TEST-{timestamp}"
            consignment = ConsignmentFactory.create(
                series=series,
                ConsignmentReference=consignment_ref,
                ConsignmentType="Test",
                IncludeTopLevelFolder=True,
                ContactName="Test User",
                ContactEmail="test@example.com",
                TransferStartDatetime=datetime.utcnow(),
                CreatedDatetime=datetime.utcnow(),
            )

            for i, (file_id, file_ext, source_path) in enumerate(files):
                filename = source_path.name

                upload_file_to_s3(source_path, f"{consignment_ref}/{file_id}")

                file = FileFactory.create(
                    FileId=file_id,
                    consignment=consignment,
                    FileType="File",
                    FileName=filename,
                    FilePath=f"{consignment.ConsignmentId}/{file_id}/{filename}",
                    FileReference=file_id,
                    CreatedDatetime=datetime.utcnow(),
                )

                metadata_dict = {
                    "source": "test_file",
                    "file_type": file_ext,
                    "created_at": datetime.utcnow().isoformat(),
                    "last_transfer_date": datetime.utcnow().isoformat(),
                    "file_size": str(os.path.getsize(source_path)),
                    "file_format": file_ext.upper(),
                    "file_extension": file_ext,
                    "mime_type": f"application/{file_ext}",
                    "closure_status": "Open",
                    "closure_type": "Open",
                    "closure_period": "0",
                    "foi_exemption_code": "None",
                    "foi_exemption_code_description": "None",
                    "title": f"Test File {i + 1}",
                    "description": "Test file for AYR development",
                    "language": "English",
                    "security_classification": "Open",
                    "copyright_status": "Crown Copyright",
                    "legal_status": "Public Record",
                }

                for key, value in metadata_dict.items():
                    FileMetadataFactory.create(
                        file=file,
                        PropertyName=key,
                        Value=value,
                        CreatedDatetime=datetime.utcnow(),
                    )

                print(f"Processed file: {filename} (ID: {file_id})")

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

            open_search_http_auth = AWS4Auth(
                aws_key, aws_secret, aws_region, aws_service
            )

            open_search_ca_certs = os.getenv("OPEN_SEARCH_CA_CERTS")
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
                        open_search_http_auth,
                        open_search_ca_certs,
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

    file_type_args = [
        "pdf",
        "png",
        "jpg",
        "tiff",
        "txt",
        "epub",
        "jp2",
        "gif",
        "svg",
        "webp",
        "mp3",
        "wav",
        "ogg",
        "m4a",
        "flac",
        "mp4",
        "webm",
        "mpeg",
    ]

    parser = argparse.ArgumentParser(
        description="Generate and process test files for AYR testing"
    )
    for ext in file_type_args:
        parser.add_argument(
            f"--num-{ext}",
            type=int,
            help=f"Number of {ext.upper()} files to create",
        )

    args = parser.parse_args()
    args_dict = vars(args)

    any_args_provided = any(value is not None for value in args_dict.values())

    if any_args_provided:
        file_type_counts = {
            ext: (
                args_dict.get(f"num_{ext}")
                if args_dict.get(f"num_{ext}") is not None
                else 0
            )
            for ext in file_type_args
        }
    else:
        file_type_counts = {ext: 1 for ext in file_type_args}

    file_paths = create_test_filepaths(file_type_counts)
    process_files(file_paths)
    index_in_opensearch(file_paths)
    print("Successfully processed files")


if __name__ == "__main__":
    main()
