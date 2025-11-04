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
logger = logging.getLogger()

s3 = boto3.client("s3")
sm = boto3.client("secretsmanager")


def get_secret_string(secret_id):
    secret_value = sm.get_secret_value(SecretId=secret_id)
    return json.loads(secret_value["SecretString"])  # pragma: allowlist secret


def get_engine():
    db_secret_id = os.getenv("DB_SECRET_ID")
    if not db_secret_id:
        raise Exception("DB_SECRET_ID environment variable not found")
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
        logger.warning(
            f"Error checking if {key} already converted:{e} Proceeding with conversion"
        )
        return False


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
        conn.rollback()
        raise Exception(f"Error querying FFIDMetadata table: {e}")

    logger.info(
        f"No extension found in FFIDMetadata for {file_id}. Trying to extract from file_name instead"
    )
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
            logger.warning("No extension in FileName")
    except SQLAlchemyError as e:
        conn.rollback()
        raise Exception(f"Error querying File table: {e}")


def convert_with_libreoffice(input_path, output_path, convert_to="pdf"):
    try:
        result = subprocess.run(  # nosec
            [
                "soffice",
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                "--convert-to",
                convert_to,
                "--outdir",
                os.path.dirname(output_path),
                input_path,
            ],
            check=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            timeout=300,
        )
        logger.info(f"Converted {input_path} to {output_path}")

        if result.stderr:
            raise RuntimeError(f"LibreOffice stderr: {result.stderr.decode()}")

    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"LibreOffice timed out after 300s converting {input_path}"
        )

    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"LibreOffice conversion failed ({input_path}): {e.stderr.decode()}"
        )

    except Exception as e:
        raise RuntimeError(
            f"Unexpected error running LibreOffice for {input_path}: {e}"
        )


def convert_xls_xlsx_to_pdf(tmpdir, input_path, output_path):
    temp_ods = os.path.join(tmpdir, "input.ods")
    convert_with_libreoffice(input_path, temp_ods, convert_to="ods")
    convert_with_libreoffice(
        temp_ods,
        output_path,
        convert_to='pdf:calc_pdf_Export:{"SinglePageSheets":{"type":"boolean","value":"true"}}',
    )


def _get_extension(file_id, conn, metadata):
    try:
        return get_extension(file_id, conn, metadata)
    except Exception as e:
        logger.error(f"Failed to get file_extension for {file_id}: {e}")
        raise Exception(f"Failed to get file_extension for {file_id}: {e}")


def _download_input(source_bucket, key, input_path):
    try:
        s3.download_file(source_bucket, key, input_path)
        logger.info(f"Downloaded {key} to {input_path}")
    except Exception as e:
        logger.error(f"Failed to download {key}: {e}")
        raise Exception(f"Failed to download {key}: {e}")


def _convert_file(extension, tmpdir, input_path, output_path, file_id):
    try:
        if extension in ("xls", "xlsx"):
            convert_xls_xlsx_to_pdf(tmpdir, input_path, output_path)
        else:
            convert_with_libreoffice(input_path, output_path)
        logger.info(f"Converted {file_id} to PDF")
    except Exception as e:
        logger.error(f"Conversion failed for {file_id}: {e}")
        raise Exception(f"Conversion failed for {file_id}: {e}")


def _verify_output_exists(output_path, file_id):
    if not os.path.exists(output_path):
        logger.error(f"Converted file missing for {file_id}, skipping upload")
        raise Exception(f"Converted file missing for {file_id}")


def _upload_output(output_path, dest_bucket, key, file_id):
    try:
        s3.upload_file(output_path, dest_bucket, key)
        logger.info(f"Uploaded converted file {file_id} to Access Copy Bucket")
    except Exception as e:
        logger.error(f"Failed to upload {key} to Access Copy bucket: {e}")
        raise Exception(f"Failed to upload {key} to Access Copy bucket: {e}")


def process_file(
    file_id,
    consignment_ref,
    source_bucket,
    dest_bucket,
    convertible_extensions,
    conn,
):
    metadata = MetaData()
    key = f"{consignment_ref}/{file_id}"

    extension = _get_extension(file_id, conn, metadata)
    logger.info(f"File extension: {extension}")

    if extension not in convertible_extensions:
        logger.info(f"File {file_id} does not require conversion")
        return

    if already_converted(dest_bucket, key):
        logger.info(f"Skipping {file_id}, already converted")
        return

    logger.info(f"File {file_id} requires conversion to PDF")
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, f"input.{extension}")
        output_path = os.path.join(tmpdir, "input.pdf")

        _download_input(source_bucket, key, input_path)
        _convert_file(extension, tmpdir, input_path, output_path, file_id)
        _verify_output_exists(output_path, file_id)

        logger.info(
            f"Files in {tmpdir} after converting {file_id}: {os.listdir(tmpdir)}"
        )
        _upload_output(output_path, dest_bucket, key, file_id)


def process_consignment(
    consignment_ref, source_bucket, dest_bucket, convertible_extensions, conn
):
    prefix = f"{consignment_ref}/"
    failed_files = []
    paginator = s3.get_paginator("list_objects_v2")
    response = paginator.paginate(Bucket=source_bucket, Prefix=prefix)
    files = set()
    for page in response:
        for obj in page.get("Contents", []):
            files.add(obj["Key"].split("/")[-1])

    if len(files) == 0:
        logger.warning(f"No files found in consignment {consignment_ref}")
        return []

    logger.info(f"{len(files)} files in consignment {consignment_ref}")

    for file_id in files:
        logger.info(f"Checking file_id: {file_id}")
        try:
            process_file(
                file_id,
                consignment_ref,
                source_bucket,
                dest_bucket,
                convertible_extensions,
                conn,
            )
        except Exception as e:
            logger.error(f"Failed to process {file_id}: {e}")
            failed_files.append(f"{consignment_ref}/{file_id}")

    return failed_files


def create_access_copies_for_all_consignments(
    source_bucket, dest_bucket, convertible_extensions, conn
):
    paginator = s3.get_paginator("list_objects_v2")
    response = paginator.paginate(Bucket=source_bucket)
    consignments = set()
    for page in response:
        for obj in page["Contents"]:
            consignments.add(obj["Key"].split("/")[0])

    logger.info(f"Found {len(consignments)} consignments")

    all_failures = []

    for consignment_ref in consignments:
        logger.info(f"Processing consignment: {consignment_ref}")
        failures = process_consignment(
            consignment_ref,
            source_bucket,
            dest_bucket,
            convertible_extensions,
            conn,
        )
        all_failures.extend(failures)

    if all_failures:
        raise RuntimeError(
            f"Conversion failed for {len(all_failures)} file(s):\n"
            + "\n".join(all_failures)
        )
    logger.info("All files requiring conversion converted successfully")


def create_access_copy_from_sns(
    source_bucket, dest_bucket, convertible_extensions, conn
):
    raw_sns_message = os.getenv("SNS_MESSAGE")
    if not raw_sns_message:
        raise Exception("SNS_MESSAGE environment variable not found")
    logger.info(f"Message Received: {raw_sns_message}")

    try:
        sns_message = json.loads(raw_sns_message)
    except Exception as e:
        logger.error(f"Error parsing SNS_MESSAGE: {e}")
        raise

    consignment_ref = sns_message.get("parameters", {}).get("reference")

    if not consignment_ref:
        raise Exception("Missing consignment_reference in SNS Message")
    logger.info(f"Processing consignment: {consignment_ref}")
    failures = process_consignment(
        consignment_ref,
        source_bucket,
        dest_bucket,
        convertible_extensions,
        conn,
    )

    if failures:
        raise RuntimeError(
            f"Conversion failed for {len(failures)} file(s):\n"
            + "\n".join(failures)
        )
    logger.info(
        f"All files requiring conversion in {consignment_ref} converted successfully"
    )


def main():
    app_secret_id = os.getenv("APP_SECRET_ID")
    if not app_secret_id:
        raise Exception("APP_SECRET_ID environment variable not found")
    app_secret = get_secret_string(app_secret_id)
    source_bucket = app_secret["RECORD_BUCKET_NAME"]
    dest_bucket = app_secret["ACCESS_COPY_BUCKET"]
    convertible_extensions = set(
        json.loads(app_secret["CONVERTIBLE_EXTENSIONS"])
    )

    conversion_type = os.getenv("CONVERSION_TYPE")
    if not conversion_type:
        raise Exception("CONVERSION_TYPE environment variable not found")
    engine = get_engine()
    conn = engine.connect()
    if conversion_type == "ALL":
        create_access_copies_for_all_consignments(
            source_bucket, dest_bucket, convertible_extensions, conn
        )

    elif conversion_type == "SINGLE":
        create_access_copy_from_sns(
            source_bucket, dest_bucket, convertible_extensions, conn
        )

    else:
        raise ValueError("Invalid CONVERSION_TYPE. Expected 'ALL' or 'SINGLE'")


if __name__ == "__main__":
    main()
