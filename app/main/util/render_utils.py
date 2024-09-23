import io

import boto3
from flask import abort, current_app, jsonify, url_for
from PIL import Image

from app.main.db.models import File, db
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


def create_presigned_url(file):
    file_extension = file.FileName.split(".")[-1].lower()
    if file_extension not in current_app.config["SUPPORTED_RENDER_EXTENSIONS"]:
        current_app.logger.info(
            f"Rendering file format '{file_extension}' is not currently supported by AYR."
        )
        return None

    s3 = boto3.client("s3")
    bucket = current_app.config["RECORD_BUCKET_NAME"]
    key = f"{file.consignment.ConsignmentReference}/{file.FileId}"

    try:
        presigned_url = s3.generate_presigned_url(
            "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=10
        )

    except Exception as e:
        current_app.logger.info(f"Failed to create presigned url. {e}")
        abort(404)

    return presigned_url


def generate_pdf_manifest(record_id):
    file = db.session.get(File, record_id)

    if file is None:
        abort(404)

    file_name = file.FileName
    file_url = url_for(
        "main.download_record", record_id=record_id, _external=True
    )

    manifest = {
        "@context": [
            "http://iiif.io/api/presentation/3/context.json",
        ],
        "id": f"{url_for('main.generate_manifest', record_id=record_id, _external=True, render=True)}",
        "type": "Manifest",
        "label": {"none": [file_name]},
        "requiredStatement": {
            "label": {"en": ["File name"]},
            "value": {"en": [file_name]},
        },
        "viewingDirection": "left-to-right",
        "behavior": ["individuals"],
        "description": f"Manifest for {file_name}",
        "items": [
            {
                "id": f"{url_for('main.generate_manifest', record_id=record_id, _external=True, render=True)}",
                "type": "Canvas",
                "label": {"en": ["test"]},
                "items": [
                    {
                        "id": f"""{url_for('main.download_record',
                                           record_id=record_id, _external=True, render=True)}""",
                        "type": "AnnotationPage",
                        "label": {"en": ["test"]},
                        "items": [
                            {
                                "id": f"""{url_for('main.download_record',
                                                   record_id=record_id, _external=True, render=True)}""",
                                "type": "Annotation",
                                "motivation": "painting",
                                "label": {"en": ["test"]},
                                "body": {
                                    "id": file_url,
                                    "type": "Text",
                                    "format": "application/pdf",
                                },
                                "target": f"""{url_for('main.download_record',
                                                       record_id=record_id, _external=True, render=True)}""",
                            }
                        ],
                    }
                ],
            }
        ],
    }

    return jsonify(manifest)


def generate_image_manifest(s3_file_object, record_id):
    file = db.session.get(File, record_id)

    if file is None:
        abort(404)

    filename = file.FileName

    image = Image.open(io.BytesIO(s3_file_object["Body"].read()))
    width, height = image.size

    # Get the file from S3 to read dimensions
    s3 = boto3.client("s3")
    bucket = current_app.config["RECORD_BUCKET_NAME"]
    key = f"{file.consignment.ConsignmentReference}/{file.FileId}"

    s3_response_object = s3.get_object(Bucket=bucket, Key=key)
    file_content = s3_response_object["Body"].read()
    image = Image.open(io.BytesIO(file_content))
    width, height = image.size

    file_url = url_for(
        "main.download_record", record_id=record_id, _external=True, render=True
    )

    manifest = {
        "@context": "http://iiif.io/api/presentation/2/context.json",
        "@id": f"{url_for('main.generate_manifest', record_id=record_id, _external=True)}",
        "@type": "sc:Manifest",
        "label": filename,
        "description": f"Manifest for {filename}",
        "sequences": [
            {
                "@id": f"""{url_for('main.download_record',
                                    record_id=record_id, _external=True, render=True)}""",
                "@type": "sc:Sequence",
                "canvases": [
                    {
                        "@id": f"""{url_for('main.download_record',
                                            record_id=record_id, _external=True, render=True)}""",
                        "@type": "sc:Canvas",
                        "label": "Image 1",
                        "width": width,
                        "height": height,
                        "images": [
                            {
                                "@id": f"""{url_for('main.download_record',
                                                    record_id=record_id, _external=True, render=True)}""",
                                "@type": "oa:Annotation",
                                "motivation": "sc:painting",
                                "resource": {
                                    "@id": file_url,
                                    "type": "dctypes:Image",
                                    "format": "image/png",
                                    "width": width,
                                    "height": height,
                                },
                                "on": f"""{url_for('main.download_record',
                                                   record_id=record_id, _external=True, render=True)}""",
                            }
                        ],
                    }
                ],
            }
        ],
    }

    return jsonify(manifest)
