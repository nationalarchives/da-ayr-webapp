import io
import os
from typing import Any

import boto3
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


def get_download_filename(file):
    """Generate download filename for a file."""
    if file.CiteableReference:
        if len(file.FileName.rsplit(".", 1)) > 1:
            return (
                file.CiteableReference + "." + file.FileName.rsplit(".", 1)[1]
            )
    return None


def create_presigned_url(file: File) -> str:
    """Create a presigned URL for accessing a file."""
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
        aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
        verify=False,
    )
    bucket = current_app.config["RECORD_BUCKET_NAME"]
    key = f"{file.consignment.ConsignmentReference}/{file.FileId}"

    try:
        presigned_url = s3.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=10
        )
        return presigned_url
    except Exception as e:
        current_app.logger.error(f"Failed to generate presigned URL: {str(e)}")
        raise


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


def generate_audio_manifest(
    file_name: str, file_url: str, manifest_url: str, s3_file_object: Any
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
                                    "type": "Sound",
                                    "format": "audio/mp3",
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


def generate_video_manifest(
    file_name: str, file_url: str, manifest_url: str, s3_file_object: Any
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
                "id": manifest_url + "/canvas",
                "type": "Canvas",
                "width": 1920,  
                "height": 1080,  
                "duration": 60.0,
                "label": {"en": ["Video content"]},
                "items": [
                    {
                        "id": manifest_url + "/canvas/page",
                        "type": "AnnotationPage",
                        "items": [
                            {
                                "id": manifest_url + "/canvas/page/annotation",
                                "type": "Annotation",
                                "motivation": "painting",
                                "body": {
                                    "id": file_url,
                                    "type": "Video",
                                    "format": "video/mp4",
                                },
                                "target": manifest_url + "/canvas",
                            }
                        ],
                    }
                ],
            }
        ],
    }

    return jsonify(manifest)


def generate_ebook_manifest(
    file_name: str, file_url: str, manifest_url: str
) -> Response:
    manifest = {
        "@context": ["https://iiif.io/api/presentation/3/context.json"],
        "id": manifest_url,
        "type": "Manifest",
        "label": {"en": [file_name]},
        "requiredStatement": {
            "label": {"en": ["File name"]},
            "value": {"en": [file_name]},
        },
        "items": [
            {
                "id": f"{manifest_url}/canvas/1",
                "type": "Canvas",
                "label": {"en": ["eBook"]},
                "items": [
                    {
                        "id": f"{manifest_url}/canvas/1/annotationpage/1",
                        "type": "AnnotationPage",
                        "items": [
                            {
                                "id": f"{manifest_url}/canvas/1/annotation/1",
                                "type": "Annotation",
                                "motivation": "painting",
                                "body": {
                                    "id": file_url,
                                    "type": "Text",
                                    "format": "application/epub+zip",
                                },
                                "target": f"{manifest_url}/canvas/1",
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
