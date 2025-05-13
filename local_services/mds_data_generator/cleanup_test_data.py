import os

import boto3
from botocore.config import Config
from db_utils import get_db_connection
from dotenv import load_dotenv

load_dotenv()


def clean_database():
    """Clean up all test data from the database."""
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            print("Cleaning up database test data...")

            # Delete in reverse order of dependencies
            tables_to_clean = [
                {
                    "table": "FileMetadata",
                    "condition": 'WHERE "FileId" IN (SELECT "FileId" FROM "File" WHERE "FileType" = %s)',
                    "params": ("File",),
                },
                {
                    "table": "AVMetadata",
                    "condition": 'WHERE "FileId" IN (SELECT "FileId" FROM "File" WHERE "FileType" = %s)',
                    "params": ("File",),
                },
                {
                    "table": "FFIDMetadata",
                    "condition": 'WHERE "FileId" IN (SELECT "FileId" FROM "File" WHERE "FileType" = %s)',
                    "params": ("File",),
                },
                {
                    "table": "File",
                    "condition": 'WHERE "FileType" = %s',
                    "params": ("File",),
                },
                {
                    "table": "Consignment",
                    "condition": 'WHERE "ConsignmentReference" LIKE %s',
                    "params": ("TEST-%",),
                },
                {
                    "table": "Series",
                    "condition": 'WHERE "Name" LIKE %s',
                    "params": ("Test Series%",),
                },
                {
                    "table": "Body",
                    "condition": 'WHERE "Name" LIKE %s',
                    "params": ("Test Transferring Body%",),
                },
            ]

            for table_info in tables_to_clean:
                query = f'DELETE FROM "{table_info["table"]}" {table_info["condition"]}'  # nosec
                cur.execute(query, table_info["params"])
                print(f"Deleted {table_info['table']} records")

            conn.commit()
            print("Database cleanup completed successfully")
            return True
    except Exception as e:
        print(f"Error during database cleanup: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


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


def cleanup_test_data():
    """Cleanup of all test data from database, example files, and MinIO."""
    results = {
        "database": clean_database(),
        "files": clean_example_files(),
        "minio": clean_minio(),
    }

    return results


if __name__ == "__main__":
    cleanup_test_data()
