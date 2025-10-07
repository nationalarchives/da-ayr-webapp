import io
from typing import Any

import boto3
from botocore.exceptions import ClientError
from flask import Response, current_app, jsonify
from PIL import Image

from app.main.db.models import File


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


def get_file_extension(file):
    """Extarct file_extension"""
    if file.ffid_metadata and file.ffid_metadata.Extension is not None:
        file_extension = file.ffid_metadata.Extension.lower()
    else:
        file_extension = file.FileName.split(".")[-1].lower()
    return file_extension


def get_download_filename(file):
    """Generate download filename for a file."""
    if file.CiteableReference:
        if len(file.FileName.rsplit(".", 1)) > 1:
            return (
                file.CiteableReference + "." + file.FileName.rsplit(".", 1)[1]
            )
    return None


def create_presigned_url(file: File) -> str:
    s3 = boto3.client("s3")
    bucket = current_app.config["RECORD_BUCKET_NAME"]
    key = f"{file.consignment.ConsignmentReference}/{file.FileId}"

    presigned_url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=10
    )

    return presigned_url


def create_presigned_url_for_access_copy(file: File) -> str:
    s3 = boto3.client("s3")
    bucket = current_app.config["ACCESS_COPY_BUCKET"]
    key = f"{file.consignment.ConsignmentReference}/{file.FileId}"
    try:
        s3.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            raise Exception("No Converted file in Access Copy Bucket")

    presigned_url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=10
    )
    return presigned_url


def generate_pdf_manifest(
    file_name: str, file_url: str, manifest_url: str
) -> Response:
    manifest = {
        "@context": [
            "https://iiif.io/api/presentation/3/context.json",
        ],
        "id": manifest_url,
        "type": "Manifest",
        "label": {"en": [file_name]},
        "requiredStatement": {
            "label": {"en": ["File name"]},
            "value": {"en": [file_name]},
        },
        "viewingDirection": "left-to-right",
        "behavior": ["individuals"],
        "description": f"Manifest for {file_name}",
        "items": [
            {
                "id": manifest_url,
                "type": "Canvas",
                "label": {"en": ["test"]},
                "items": [
                    {
                        "id": file_url,
                        "type": "AnnotationPage",
                        "label": {"en": ["test"]},
                        "items": [
                            {
                                "id": file_url,
                                "type": "Annotation",
                                "motivation": "painting",
                                "label": {"en": ["test"]},
                                "body": {
                                    "id": file_url,
                                    "type": "Text",
                                    "format": "application/pdf",
                                },
                                "target": file_url,
                            }
                        ],
                    }
                ],
            }
        ],
    }

    return jsonify(manifest)


def generate_image_manifest(
    file_name: str, file_url: str, manifest_url: str, s3_file_object: Any
) -> Response:
    image = Image.open(io.BytesIO(s3_file_object["Body"].read()))
    image_width, image_height = image.size

    manifest = {
        "@context": "https://iiif.io/api/presentation/3/context.json",
        "@id": manifest_url,
        "@type": "sc:Manifest",
        "label": {"en": [file_name]},
        "description": f"Manifest for {file_name}",
        "sequences": [
            {
                "@id": file_url,
                "@type": "sc:Sequence",
                "canvases": [
                    {
                        "@id": file_url,
                        "@type": "sc:Canvas",
                        "label": "Image 1",
                        "width": image_width,
                        "height": image_height,
                        "images": [
                            {
                                "@id": file_url,
                                "@type": "oa:Annotation",
                                "motivation": "sc:painting",
                                "resource": {
                                    "@id": file_url,
                                    "type": "dctypes:Image",
                                    "format": "image/png",
                                    "width": image_width,
                                    "height": image_height,
                                },
                                "on": file_url,
                            }
                        ],
                    }
                ],
            }
        ],
    }

    return jsonify(manifest)
