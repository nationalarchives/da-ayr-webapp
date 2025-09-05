import json
import logging
import os
import subprocess  # nosec
import tempfile

import boto3
from botocore.exceptions import ClientError
from sqlalchemy import MetaData, Table, create_engine, select
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

s3 = boto3.client("s3")
sm = boto3.client("secretsmanager")


def get_secret_string(secret_id):
    secret_value = sm.get_secret_value(SecretId=secret_id)
    return json.loads(secret_value["SecretString"])  # pragma: allowlist secret


def get_engine():
    db_secret_id = os.getenv("DB_SECRET_ID")
    creds = get_secret_string(db_secret_id)
    url = (
        f"postgresql+psycopg2://{creds['username']}:{creds['password']}"
        f"@{creds['proxy']}:{creds['port']}/{creds['dbname']}"
    )
    return create_engine(url)


def already_converted(bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise


def get_extension(file_id, conn, metadata):
    ffidmetadata = Table("FFIDMetadata", metadata, autoload_with=conn)
    file_table = Table("File", metadata, autoload_with=conn)

    try:
        stmt = (
            select(ffidmetadata.c.Extension)
            .where(ffidmetadata.c.FileId == file_id)
            .limit(1)
        )
        result = conn.execute(stmt).first()
        if result and result[0]:
            return result[0].lower()
    except SQLAlchemyError as e:
        logger.error(f"Error querying FFIDMetadata table: {e}")
        conn.rollback()
        return "ERROR"

    try:
        logger.info(
            f"No extension found in FFIDMetadata for {file_id}. Trying to extract from file_name instead"
        )
        stmt = (
            select(file_table.c.FileName)
            .where(file_table.c.FileId == file_id)
            .limit(1)
        )
        result = conn.execute(stmt).first()
        if result and result[0]:
            filename = result[0]
            logger.info(f"FileName: {filename}")
            if "." in filename:
                return filename.rsplit(".", 1)[1].lower()
            logger.warning("No extension in FileName")
    except SQLAlchemyError as e:
        logger.error(f"Error querying File table: {e}")
        conn.rollback()
        return "ERROR"


def convert_office_to_pdf(input_path, output_path):
    try:
        subprocess.run(  # nosec
            [
                "soffice",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                os.path.dirname(output_path),
                input_path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"LibreOffice conversion failed: {e.stderr.decode()}"
        )


def process_consignment(
    consignment_ref: str,
    source_bucket,
    dest_bucket,
    convertible_extensions,
    engine,
    metadata,
):
    prefix = f"{consignment_ref}/"

    response = s3.list_objects_v2(Bucket=source_bucket, Prefix=prefix)
    if "Contents" not in response:
        logger.warning(f"No files found in consignment {consignment_ref}")
        return
    logger.info(
        f"{len(response['Contents'])} files in consignment {consignment_ref}"
    )

    with engine.connect() as conn:
        for obj in response["Contents"]:
            key = obj["Key"]
            file_id = key.split("/")[-1]
            logger.info(f"Checking file_id: {file_id}")

            extension = get_extension(file_id, conn, metadata)
            if extension == "ERROR":
                logger.error(f"failed to get file_extension for {file_id}")
                continue
            logger.info(f"File extension: {extension}")

            if extension not in convertible_extensions:
                logger.info(f"File {file_id} does not require conversion")
                continue

            dest_key = f"{consignment_ref}/{file_id}"
            if already_converted(dest_bucket, dest_key):
                logger.info(f"Skipping {file_id}, already converted")
                continue

            logger.info(f"File {file_id} requires conversion to PDF")
            with tempfile.TemporaryDirectory() as tmpdir:
                input_path = os.path.join(tmpdir, f"input.{extension}")
                output_path = os.path.join(tmpdir, "input.pdf")

                s3.download_file(source_bucket, key, input_path)
                logger.info(f"Downloaded {key} to {input_path}")

                try:
                    convert_office_to_pdf(input_path, output_path)
                    logger.info(f"Converted {input_path} to PDF {output_path}")
                except Exception as e:
                    logger.error(f"Conversion failed for {file_id}: {e}")
                    continue

                s3.upload_file(output_path, dest_bucket, dest_key)
                logger.info("Uploaded converted PDF to Access Copy Bucket")


def main():
    app_secret_id = os.getenv("APP_SECRET_ID")
    app_secret = get_secret_string(app_secret_id)
    source_bucket = app_secret["RECORD_BUCKET_NAME"]
    dest_bucket = app_secret["ACCESS_COPY_BUCKET"]
    convertible_extensions = set(
        json.loads(app_secret["CONVERTIBLE_EXTENSIONS"])
    )

    engine = get_engine()
    metadata = MetaData()
    paginator = s3.get_paginator("list_objects_v2")
    response = paginator.paginate(Bucket=source_bucket)
    consignments = set()
    for page in response:
        for obj in page["Contents"]:
            consignments.add(obj["Key"].split("/")[0])

    logger.info(f"Found {len(consignments)} consignments")

    for consignment_ref in consignments:
        logger.info(f"Processing consignment: {consignment_ref}")
        process_consignment(
            consignment_ref,
            source_bucket,
            dest_bucket,
            convertible_extensions,
            engine,
            metadata,
        )


if __name__ == "__main__":
    main()
