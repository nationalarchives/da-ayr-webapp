import os

import boto3
import requests
from botocore.config import Config
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

from app import create_app, db
from app.main.db.models import Body, Consignment, File, FileMetadata, Series
from configs.env_config import EnvConfig

load_dotenv()


def clean_opensearch():
    host = os.getenv("OPEN_SEARCH_HOST")
    username = os.getenv("OPEN_SEARCH_USERNAME")
    password = os.getenv("OPEN_SEARCH_PASSWORD")
    index_name = "documents"

    try:
        response = requests.delete(
            f"{host}/{index_name}",
            auth=HTTPBasicAuth(username, password),
            verify=False,  # nosec
            timeout=20,
        )
        if response.status_code == 200:
            print(f"Deleted OpenSearch index: {index_name}")
        elif response.status_code == 404:
            print(f"OpenSearch index '{index_name}' not found.")
        else:
            print(
                f"Failed to delete OpenSearch index: {response.status_code} - {response.text}"
            )
    except Exception as e:
        print(f"Error deleting OpenSearch index: {e}")


def clean_database():
    """Clean up all test data from the database."""
    app = create_app(EnvConfig)
    with app.app_context():
        try:
            models = [FileMetadata, File, Consignment, Series, Body]

            for model in models:
                print(f"Cleaning data from {model}")
                model.query.delete()
                print(f"Deleted all records from {model}")

            db.session.commit()
            print("Database cleanup completed successfully")
            return True
        except Exception as e:
            print(f"Error during database cleanup: {e}")
            db.session.rollback()
            return False


def clean_example_files():
    """Clean up test files from the example_files directory."""
    try:
        example_folder = os.path.join(
            os.getcwd(), "local_services/mds_data_generator/example_files"
        )
        if not os.path.exists(example_folder):
            print("Example folder not found, skipping file cleanup")
            return True

        # Keep the original files
        original_file = os.path.join(example_folder, "file.pdf")
        deleted_count = 0

        for filename in os.listdir(example_folder):
            file_path = os.path.join(example_folder, filename)
            if file_path != original_file and filename.startswith("test_file_"):
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting file {filename}: {e}")

        print(
            f"Example files cleanup completed - deleted {deleted_count} files"
        )
        return True
    except Exception as e:
        print(f"Error during file cleanup: {e}")
        return False


def clean_minio():
    """Clean up test objects from MinIO storage."""
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
            aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
            aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

        # List all objects in the bucket
        bucket = os.getenv("RECORD_BUCKET_NAME")
        response = s3.list_objects_v2(Bucket=bucket)
        deleted_count = 0

        if "Contents" in response:
            for obj in response["Contents"]:
                # Delete objects that are in TEST-* folders
                if obj["Key"].startswith("TEST-"):
                    s3.delete_object(Bucket=bucket, Key=obj["Key"])
                    deleted_count += 1

        print(f"MinIO cleanup completed - deleted {deleted_count} objects")
        return True
    except Exception as e:
        print(f"Error cleaning up MinIO: {e}")
        return False


if __name__ == "__main__":
    clean_database()
    clean_example_files()
    clean_minio()
    clean_opensearch()
