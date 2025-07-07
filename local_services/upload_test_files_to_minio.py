#!/usr/bin/env python3
"""
Upload test files from local_services/files/ to MinIO for CI testing.
This script mirrors the manual upload process described in the README.
"""

import boto3
import os
import sys
from pathlib import Path
from botocore.client import Config


def main():
    # MinIO client setup
    s3 = boto3.client(
        's3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='ROOTNAME',
        aws_secret_access_key='CHANGEME123', # pragma: allowlist secret
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

    # Create bucket if it doesn't exist
    bucket_name = 'test-record-download'
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists")
    except Exception as e:
        print(f"Creating bucket '{bucket_name}'")
        s3.create_bucket(Bucket=bucket_name)

    # Upload all files from local_services/files/
    script_dir = Path(__file__).parent
    files_dir = script_dir / 'files'
    
    if not files_dir.exists():
        print(f"Error: {files_dir} directory not found")
        sys.exit(1)

    uploaded_count = 0
    for consignment_dir in files_dir.iterdir():
        if consignment_dir.is_dir():
            print(f"Processing consignment: {consignment_dir.name}")
            for file_path in consignment_dir.iterdir():
                if file_path.is_file():
                    key = f'{consignment_dir.name}/{file_path.name}'
                    print(f'  Uploading {key}')
                    try:
                        s3.upload_file(str(file_path), bucket_name, key)
                        uploaded_count += 1
                    except Exception as e:
                        print(f'  Error uploading {key}: {e}')

    print(f'MinIO file upload completed. Uploaded {uploaded_count} files.')


if __name__ == '__main__':
    main()