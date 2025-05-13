# MDS Test Data Generator

This tool generates test data for AYR development and performance testing by:

1. Creating various document types (PDF, TIF, GIF, PNG, JPEG)
2. Adding metadata to a PostgreSQL database
3. Uploading files to S3/MinIO storage

## Prerequisites

Before running the tool, ensure the following environment variables are set (usually via `.env`):

- `MINIO_ROOT_USER` – your MinIO access key
- `MINIO_ROOT_PASSWORD` – your MinIO secret key
- `AWS_ENDPOINT_URL` – the S3/MinIO endpoint (e.g., http://localhost:9000)
- `RECORD_BUCKET_NAME` – the name of the bucket used for test files

Example `.env`:

```env
MINIO_ROOT_USER=
MINIO_ROOT_PASSWORD=
AWS_ENDPOINT_URL=http://localhost:9000
RECORD_BUCKET_NAME=test-record-download


The PostgreSQL database is expected to be running locally in Docker, and the connection is configured with a password as:

```python
def get_db_connection():
    """Get a secure connection to the webapp database using environment variables."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="verify-full",
        sslrootcert=os.getenv("DB_SSL_ROOTCERT"),
    )

```

## To Run

python local_services/mds_data_generator/mds_test_file_importer.py --num-tif 5 --num-pdf 5

## To remove all files

python local_services/mds_data_generator/cleanup_test_data.py
