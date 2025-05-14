import argparse
import json
import os
import shutil
import uuid
from datetime import datetime

import boto3
from botocore.client import Config
from dotenv import load_dotenv

from app import create_app, db
from app.main.db.models import Body, Series
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
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
        region_name="us-east-1",
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


def create_test_files(file_type_counts):
    """Create test files by copying example files of specified types."""
    example_folder = os.path.join(
        os.getcwd(), "local_services/mds_data_generator/example_files"
    )
    os.makedirs(example_folder, exist_ok=True)

    created_files = []

    for ext, count in file_type_counts.items():
        source_file = os.path.join(example_folder, f"file.{ext}")
        if not os.path.exists(source_file):
            raise FileNotFoundError(f"Source file not found: {source_file}")

        for i in range(count):
            filename = f"test_file_{i + 1}.{ext}"
            file_path = os.path.join(example_folder, filename)
            shutil.copy2(source_file, file_path)
            created_files.append((file_path, ext))

    return created_files


def process_files(file_paths):
    """Process files by uploading to S3 and adding metadata to database."""
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

            for i, (file_path, file_ext) in enumerate(file_paths):
                filename = os.path.basename(file_path)
                file_id = str(uuid.uuid4())

                upload_file_to_s3(file_path, f"{consignment_ref}/{file_id}")

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
                    "file_size": str(os.path.getsize(file_path)),
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


def remove_created_files():
    """Delete the test files that were created."""
    print("Deleting created files")

    example_folder = os.path.join(
        os.getcwd(), "local_services/mds_data_generator/example_files"
    )
    print(f"Looking in: {example_folder}")
    print("Files:", os.listdir(example_folder))

    for filename in os.listdir(example_folder):
        print(f"Checking: {filename}")
        if filename.startswith("test_"):
            file_path = os.path.join(example_folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted: {file_path}")


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
    parser.add_argument(
        "--num-pdf", type=int, default=0, help="Number of PDF files to create"
    )
    parser.add_argument(
        "--num-png", type=int, default=0, help="Number of PNG files to create"
    )
    parser.add_argument(
        "--num-jpg", type=int, default=0, help="Number of JPG files to create"
    )
    parser.add_argument(
        "--num-tiff", type=int, default=0, help="Number of TIF files to create"
    )

    args = parser.parse_args()

    file_type_counts = {
        "pdf": args.num_pdf,
        "png": args.num_png,
        "jpg": args.num_jpg,
        "tiff": args.num_tiff,
    }

    file_type_counts = {k: v for k, v in file_type_counts.items() if v > 0}

    if not file_type_counts:
        file_type_counts = {
            "pdf": 1,
            "png": 1,
            "jpg": 1,
            "tiff": 1,
        }

    file_paths = create_test_files(file_type_counts)
    process_files(file_paths)
    print(f"\nSuccessfully processed {len(file_paths)} files")
    remove_created_files()


if __name__ == "__main__":
    main()
