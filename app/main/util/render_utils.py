import os
import shutil

import boto3
from flask import current_app

from app.main.db.queries import get_file_metadata


def get_file_mimetype(file_type):
    if file_type == "pdf":
        return "application/pdf"
    elif file_type in ["png", "jpg", "jpeg"]:
        return f"image/{file_type}"


def get_file_details(file):
    """Retrieve file metadata and determine file type and extension."""
    file_metadata = get_file_metadata(file.FileId)
    file_extension = file.FileName.split(".")[-1].lower()

    if file_extension in ["pdf", "png", "jpg", "jpeg"]:
        file_type = "iiif"
    else:
        file_type = None

    return file_metadata, file_type, file_extension


def generate_breadcrumb_values(file):
    """Generate breadcrumb values for the record template."""
    consignment = file.consignment
    body = consignment.series.body
    series = consignment.series
    return {
        0: {"transferring_body_id": body.BodyId},
        1: {"transferring_body": body.Name},
        2: {"series_id": series.SeriesId},
        3: {"series": series.Name},
        4: {"consignment_id": consignment.ConsignmentId},
        5: {"consignment_reference": consignment.ConsignmentReference},
        6: {"file_name": file.FileName},
    }


def get_download_filename(file):
    """Generate download filename for a file."""
    if file.CiteableReference:
        if len(file.FileName.rsplit(".", 1)) > 1:
            return (
                file.CiteableReference + "." + file.FileName.rsplit(".", 1)[1]
            )
    return None


def manage_static_file(file, record_id, file_extension):
    """Manage the file in the static directory."""
    s3 = boto3.client("s3")
    bucket = current_app.config["RECORD_BUCKET_NAME"]
    key = f"{file.consignment.ConsignmentReference}/{file.FileId}"
    files_directory = os.path.join(current_app.static_folder, "files")

    if file_extension == "pdf":
        static_file_path = os.path.join(files_directory, f"{record_id}.pdf")
    elif file_extension in ["png", "jpg", "jpeg"]:
        static_file_path = os.path.join(
            files_directory, f"{record_id}.{file_extension}"
        )

    if os.path.exists(files_directory):
        shutil.rmtree(files_directory)

    os.makedirs(files_directory)

    s3_file_object = s3.get_object(Bucket=bucket, Key=key)
    file_content = s3_file_object["Body"].read()

    with open(static_file_path, "wb") as static_file:
        static_file.write(file_content)

    return static_file_path
