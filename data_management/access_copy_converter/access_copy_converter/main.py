import json
import logging
import os
import subprocess  # nosec
import tempfile

import boto3
from sqlalchemy import MetaData, Table, create_engine, select
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger()


s3 = boto3.client("s3")
sm = boto3.client("secretsmanager")


def get_secret_string(secret_id):
    secret_value = sm.get_secret_value(SecretId=secret_id)
    secret = json.loads(
        secret_value["SecretString"]  # pragma: allowlist secret
    )
    return secret


def get_engine():
    db_secret_id = os.getenv("DB_SECRET_ID")
    creds = get_secret_string(db_secret_id)
    url = (
        f"postgresql+psycopg2://{creds['username']}:{creds['password']}"
        f"@{creds['proxy']}:{creds['port']}/{creds['dbname']}"
    )
    return create_engine(url)


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

    try:
        stmt = (
            select(file_table.c.FileName)
            .where(file_table.c.FileId == file_id)
            .limit(1)
        )
        result = conn.execute(stmt).first()
        if result and result[0]:
            filename = result[0]
            if "." in filename:
                return filename.rsplit(".", 1)[1].lower()
    except SQLAlchemyError as e:
        logger.error(f"Error querying File table: {e}")
        conn.rollback()

    return None


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
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"LibreOffice conversion failed: {e}")


def process_consignment(consignment_ref: str):
    logger.info(f"Processing consignment: {consignment_ref}")
    prefix = f"{consignment_ref}/"

    engine = get_engine()
    metadata = MetaData()
    secret_id = os.getenv("APP_SECRET_ID")
    app_secret = get_secret_string(secret_id)
    source_bucket = app_secret["RECORD_BUCKET_NAME"]
    dest_bucket = app_secret["ACCESS_COPY_BUCKET"]
    convertible_extensions = set(
        json.loads(app_secret["CONVERTIBLE_EXTENSIONS"])
    )
    with engine.connect() as conn:
        response = s3.list_objects_v2(Bucket=source_bucket, Prefix=prefix)
        if "Contents" not in response:
            logger.warning(f"No files found in consignment {consignment_ref}")
            return

        for obj in response["Contents"]:
            key = obj["Key"]
            file_id = key.split("/")[-1]
            logger.info(f"Checking file_id: {file_id}")

            extension = get_extension(file_id, conn, metadata)
            logger.info(f"File extension: {extension}")

            if extension in convertible_extensions:
                logger.info(f"File {file_id} requires conversion to PDF")

                with tempfile.TemporaryDirectory() as tmpdir:
                    input_path = os.path.join(tmpdir, f"input.{extension}")
                    output_path = os.path.join(tmpdir, "input.pdf")

                    s3.download_file(source_bucket, key, input_path)
                    logger.info(f"Downloaded {key} to {input_path}")

                    try:
                        convert_office_to_pdf(input_path, output_path)
                        logger.info(
                            f"Converted {input_path} to PDF {output_path}"
                        )
                    except Exception as e:
                        logger.error(f"Conversion failed for {file_id}: {e}")
                        continue

                    dest_key = f"{consignment_ref}/{file_id}"
                    s3.upload_file(output_path, dest_bucket, dest_key)
                    logger.info(
                        f"Uploaded converted PDF to s3://{dest_bucket}/{dest_key}"
                    )
            else:
                logger.info(f"File {file_id} does not require conversion")


def main():
    raw_sns_message = os.getenv("SNS_MESSAGE")
    logger.info(f"Message Received: {raw_sns_message}")
    if not raw_sns_message:
        raise Exception("SNS_MESSAGE environment variable not found")

    try:
        sns_message = json.loads(raw_sns_message)
    except Exception as e:
        logger.error(f"Error parsing SNS_MESSAGE: {e}")
        raise

    consignment_reference = sns_message.get("parameters", {}).get("reference")

    if not consignment_reference:
        raise Exception(
            "Missing reference in SNS Message required for indexing"
        )

    process_consignment(consignment_reference)


if __name__ == "__main__":
    main()
