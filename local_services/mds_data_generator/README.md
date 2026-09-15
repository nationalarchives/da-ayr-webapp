# MDS Test Data Generator

This tool generates test data for AYR development and performance testing by:

1. Creating various document types (PDF, TIF, GIF, PNG, JPEG)
2. Adding metadata to a PostgreSQL database
3. Uploading files to S3-compatible storage (RustFS in local development)

## Prerequisites

Before running the tool, ensure the following environment variables are set (usually via `.env`):

- `RUSTFS_ROOT_USER` – your RustFS access key
- `RUSTFS_ROOT_PASSWORD` – your RustFS secret key
- `AWS_ENDPOINT_URL` – the S3-compatible endpoint (e.g., http://localhost:9000)
- `RECORD_BUCKET_NAME` – the name of the bucket used for test files

Example `.env`:

```env
RUSTFS_ROOT_USER=
RUSTFS_ROOT_PASSWORD=
AWS_ENDPOINT_URL=http://localhost:9000
RECORD_BUCKET_NAME=test-record-download


## To Run

python local_services/mds_data_generator/mds_test_file_importer.py --num-tif 5 --num-pdf 5

## To remove all files

python local_services/mds_data_generator/cleanup_test_data.py
