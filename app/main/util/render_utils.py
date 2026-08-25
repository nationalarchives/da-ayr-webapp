import contextlib
import io
import logging

import boto3
import pymupdf
from botocore.exceptions import ClientError
from flask import Response, current_app, jsonify, url_for
from PIL import Image

from app.main.db.models import File

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def _open_pdf(pdf_bytes: bytes):
    """Open a PDF with MuPDF stderr suppressed; log any collected messages at DEBUG."""
    pymupdf.TOOLS.mupdf_display_errors(False)
    pymupdf.TOOLS.mupdf_display_warnings(False)
    try:
        with pymupdf.open("pdf", io.BytesIO(pdf_bytes)) as doc:
            yield doc
    finally:
        messages = pymupdf.TOOLS.mupdf_warnings(reset=True)
        pymupdf.TOOLS.mupdf_display_errors(True)
        pymupdf.TOOLS.mupdf_display_warnings(True)
        if messages:
            logger.debug("MuPDF: %s", messages)


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


def get_file_puid(file):
    """Extract file PUID from FFIDMetadata"""
    puid = file.ffid_metadata.PUID.lower()
    return puid


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
            raise Exception("No converted file in Access Copy bucket")

    presigned_url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=10
    )
    return presigned_url


def generate_pdf_manifest(
    file_name: str,
    manifest_url: str,
    record_id: str,
) -> Response:
    """
    Generate an IIIF Presentation 3 manifest for a PDF file.

    The single canvas is painted with the PDF itself (format
    "application/pdf"), which makes Universal Viewer select its PDF
    extension and render the document client-side with PDF.js (preserving
    the text layer for search), instead of the OpenSeadragon image
    extension which fetches server-rasterised JPEGs page by page.

    Args:
        file_name (str): The display name of the file.
        manifest_url (str): The manifest's own URL.
        record_id (str): The record UUID for generating the PDF URL.

    Returns:
        Response: Flask JSON response containing the IIIF manifest.
    """
    current_app.logger.info(
        f"Generating PDF manifest for {file_name}, record_id: {record_id}"
    )

    pdf_url = url_for(
        "main.get_record_pdf", record_id=record_id, _external=True
    )

    canvas_id = f"{manifest_url}/canvas/1"

    manifest = {
        "@context": "https://iiif.io/api/presentation/3/context.json",
        "id": manifest_url,
        "type": "Manifest",
        "label": {"en": [file_name]},
        "summary": {"en": [f"Manifest for {file_name}"]},
        "rendering": [
            {
                "id": pdf_url,
                "type": "Text",
                "label": {"en": [file_name]},
                "format": "application/pdf",
            }
        ],
        "items": [
            {
                "id": canvas_id,
                "type": "Canvas",
                "label": {"en": [file_name]},
                "items": [
                    {
                        "id": f"{canvas_id}/annotationpage/1",
                        "type": "AnnotationPage",
                        "items": [
                            {
                                "id": f"{canvas_id}/annotation/1",
                                "type": "Annotation",
                                "motivation": "painting",
                                "body": {
                                    "id": pdf_url,
                                    "type": "Text",
                                    "format": "application/pdf",
                                },
                                "target": canvas_id,
                            }
                        ],
                    }
                ],
            }
        ],
    }

    response = jsonify(manifest)

    return response


def generate_image_manifest(
    file_name: str,
    file_url: str,
    manifest_url: str,
    bucket: str = None,
    key: str = None,
) -> Response:
    pdf_bytes = get_pdf_from_s3(bucket, key)
    image = Image.open(io.BytesIO(pdf_bytes))
    image_width, image_height = image.size

    # Detect image format
    image_format = image.format.lower() if image.format else "png"
    if image_format == "jpeg":
        mime_type = "image/jpeg"
    elif image_format == "png":
        mime_type = "image/png"
    elif image_format in ["tiff", "tif"]:
        mime_type = "image/tiff"
    elif image_format == "gif":
        mime_type = "image/gif"
    elif image_format == "webp":
        mime_type = "image/webp"
    else:
        mime_type = f"image/{image_format}"

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
                                    "@type": "dctypes:Image",
                                    "format": mime_type,
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

    response = jsonify(manifest)

    return response


def search_within_pdf(
    query: str,
    bucket: str,
    key: str,
) -> Response:
    """
    Search for text within a PDF.

    The manifest paints one canvas with the whole PDF (see
    generate_pdf_manifest), so there's no per-page canvas to target and no
    generic IIIF client using this, it's called directly by our own
    search overlay in init.uv.js. Rects are normalised so the frontend can
    position highlights from whatever size it's currently rendering the
    page at, without knowing PDF.js's live zoom scale.

    Args:
        query: The search term.
        bucket: S3 bucket name.
        key: S3 object key.

    Returns:
        Flask JSON response: {"total": int, "hits": [{"page", "rect"}]}.
    """
    pdf_bytes = get_pdf_from_s3(bucket, key)

    hits = []

    with _open_pdf(pdf_bytes) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            page_width = page.rect.width
            page_height = page.rect.height

            for rect in page.search_for(query):
                hits.append(
                    {
                        "page": page_num + 1,
                        "rect": {
                            "x": rect.x0 / page_width,
                            "y": rect.y0 / page_height,
                            "w": (rect.x1 - rect.x0) / page_width,
                            "h": (rect.y1 - rect.y0) / page_height,
                        },
                    }
                )

    return jsonify({"total": len(hits), "hits": hits})


def get_pdf_from_s3(bucket: str, key: str) -> bytes:
    """fetch PDF file from S3 and return its bytes."""
    s3 = boto3.client("s3")
    s3_object = s3.get_object(Bucket=bucket, Key=key)
    pdf_bytes = s3_object["Body"].read()

    return pdf_bytes
