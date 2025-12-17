import base64
import io
import time
from typing import List

import boto3
import pymupdf
from botocore.exceptions import ClientError
from flask import Response, current_app, jsonify
from PIL import Image

from app.main.db.models import File

pdf_cache = {}


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


def extract_pdf_pages_as_images(pdf_bytes: bytes) -> List[dict]:
    """Extract PDF pages as images and return page info with base64 thumbnails."""
    DPI = 150  # Output DPI for rendering

    with pymupdf.open("pdf", io.BytesIO(pdf_bytes)) as pdf_document:
        page_data = []

        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            mat = pymupdf.Matrix(DPI / 72, DPI / 72)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")

            # Convert to PIL Image for thumbnail processing
            page_image = Image.open(io.BytesIO(img_bytes))

            # Create thumbnail (150x200 pixels)
            thumbnail = page_image.copy()
            thumbnail.thumbnail((150, 200), Image.Resampling.LANCZOS)

            # Convert thumbnail to base64 data URL
            thumbnail_buffer = io.BytesIO()
            thumbnail.save(thumbnail_buffer, format="JPEG", quality=70)
            thumbnail_base64 = base64.b64encode(
                thumbnail_buffer.getvalue()
            ).decode()
            thumbnail_data_url = f"data:image/jpeg;base64,{thumbnail_base64}"

            # Convert full page to base64 data URL
            page_buffer = io.BytesIO()
            page_image.save(page_buffer, format="JPEG", quality=75)
            page_base64 = base64.b64encode(page_buffer.getvalue()).decode()
            page_data_url = f"data:image/jpeg;base64,{page_base64}"

            current_app.logger.debug(
                f"Page {page_num + 1}: thumbnail={len(thumbnail_base64)} chars, full={len(page_base64)} chars"
            )

            page_data.append(
                {
                    "page_number": page_num + 1,
                    "width": page_image.width,
                    "height": page_image.height,
                    "thumbnail_url": thumbnail_data_url,
                    "page_image_url": page_data_url,
                }
            )

            # Clean up resources
            page_image.close()
            thumbnail.close()
            pix = None

        return page_data


def extract_single_page_as_image(
    pdf_bytes: bytes, page_number: int, thumbnail: bool = False
) -> bytes:
    """
    Extract a single page from PDF as JPEG bytes.

    Args:
        pdf_bytes: The PDF file bytes
        page_number: 1-indexed page number
        thumbnail: If True, return thumbnail size (150x200)

    Returns:
        JPEG image bytes

    Raises:
        ValueError: If page_number is invalid
    """
    DPI = 150

    with pymupdf.open("pdf", io.BytesIO(pdf_bytes)) as pdf_document:
        if page_number < 1 or page_number > pdf_document.page_count:
            raise ValueError(
                f"Invalid page number: {page_number}. PDF has {pdf_document.page_count} pages."
            )

        # Load page (convert 1-indexed to 0-indexed)
        page = pdf_document.load_page(page_number - 1)
        mat = pymupdf.Matrix(DPI / 72, DPI / 72)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")

        # Convert to PIL Image
        page_image = Image.open(io.BytesIO(img_bytes))

        if thumbnail:
            page_image.thumbnail((150, 200), Image.Resampling.LANCZOS)
            quality = 70
        else:
            quality = 75

        # Convert to JPEG
        output_buffer = io.BytesIO()
        page_image.save(output_buffer, format="JPEG", quality=quality)

        # Clean up
        page_image.close()
        pix = None

        return output_buffer.getvalue()


def extract_single_page_as_thumbnail(
    pdf_bytes: bytes, page_number: int
) -> bytes:
    """
    Extract a single page from PDF as a thumbnail JPEG.

    Args:
        pdf_bytes: The PDF file bytes
        page_number: 1-indexed page number

    Returns:
        JPEG thumbnail bytes (150x200 max)
    """
    return extract_single_page_as_image(pdf_bytes, page_number, thumbnail=True)


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
    # file_obj: Any = None,
    bucket: str = None,
    key: str = None,
    record_id: str = None,
) -> Response:
    """
    Generate an IIIF manifest for a PDF file with URLs to page images.

    Args:
        file_name (str): The display name of the file.
        manifest_url (str): The manifest's own URL.
        file_obj (Any, optional): The File object for S3 access.
        record_id (str, optional): The record UUID for generating image URLs.

    Returns:
        Response: Flask JSON response containing the IIIF manifest.
    """
    current_app.logger.info(
        f"Generating PDF manifest for {file_name}, record_id: {record_id}"
    )

    # Read PDF to get page count and dimensions
    pdf_bytes = get_pdf_from_s3(bucket, key)
    # pdf_bytes = file_obj["Body"].read()
    current_app.logger.info(f"PDF bytes length: {len(pdf_bytes)}")

    canvas_items = []

    with pymupdf.open("pdf", io.BytesIO(pdf_bytes)) as pdf_document:
        page_count = pdf_document.page_count
        current_app.logger.info(f"PDF has {page_count} pages")

        for page_num in range(page_count):
            page = pdf_document.load_page(page_num)
            rect = page.rect

            # Calculate dimensions at 150 DPI
            DPI = 150
            width = int(rect.width * DPI / 72)
            height = int(rect.height * DPI / 72)

            page_number = page_num + 1

            # Generate URLs for this page
            from flask import url_for

            page_image_url = url_for(
                "main.get_page_image",
                record_id=record_id,
                page_number=page_number,
                _external=True,
            )

            thumbnail_url = url_for(
                "main.get_page_thumbnail",
                record_id=record_id,
                page_number=page_number,
                _external=True,
            )

            canvas_id = f"{manifest_url}/canvas/{page_number}"
            canvas_items.append(
                {
                    "@type": "sc:Canvas",
                    "@id": canvas_id,
                    "label": f"Page {page_number}",
                    "width": width,
                    "height": height,
                    "thumbnail": {
                        "@id": thumbnail_url,
                        "@type": "dctypes:Image",
                        "format": "image/jpeg",
                        "width": 150,
                        "height": 200,
                    },
                    "images": [
                        {
                            "@type": "oa:Annotation",
                            "motivation": "sc:painting",
                            "resource": {
                                "@id": page_image_url,
                                "@type": "dctypes:Image",
                                "format": "image/jpeg",
                                "width": width,
                                "height": height,
                            },
                            "on": canvas_id,
                        }
                    ],
                }
            )

    manifest = {
        "@context": "https://iiif.io/api/presentation/3/context.json",
        "@type": "sc:Manifest",
        "@id": manifest_url,
        "label": {"en": [file_name]},
        "description": f"Manifest for {file_name}",
        "viewingDirection": "left-to-right",
        "sequences": [
            {
                "@type": "sc:Sequence",
                "@id": f"{manifest_url}/sequence/1",
                "label": "Sequence 1",
                "canvases": canvas_items,
            }
        ],
    }

    current_app.logger.info(
        f"Generated PDF manifest with {len(canvas_items)} canvases for {file_name}"
    )

    response = jsonify(manifest)
    # Set cache headers using configured duration
    max_age = current_app.config["UV_MANIFEST_CACHE_MAX_AGE"]
    response.headers["Cache-Control"] = f"private, max-age={max_age}"
    response.headers["ETag"] = f'"{record_id}-manifest"'

    return response


def generate_image_manifest(
    file_name: str,
    file_url: str,
    manifest_url: str,
    # s3_file_object: Any,
    bucket: str = None,
    key: str = None,
) -> Response:
    pdf_bytes = get_pdf_from_s3(bucket, key)
    image = Image.open(pdf_bytes)
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
    # Set cache headers using configured duration
    max_age = current_app.config["UV_MANIFEST_CACHE_MAX_AGE"]
    response.headers["Cache-Control"] = f"private, max-age={max_age}"

    return response


def get_pdf_from_s3(bucket: str, key: str) -> bytes:
    """Check if PDF has been cached
    else fetch PDF file from S3 and return its bytes."""
    cache_key = f"{bucket}:{key}"
    cache_ttl = current_app.config["PDF_S3_CACHE_TTL"]

    if cache_key in pdf_cache:
        cached_pdf, timestamp = pdf_cache[cache_key]
        if time.time() - timestamp < cache_ttl:
            return cached_pdf
        else:
            del pdf_cache[cache_key]  # Remove stale cache entry

    s3 = boto3.client("s3")
    s3_object = s3.get_object(Bucket=bucket, Key=key)
    pdf_bytes = s3_object["Body"].read()

    # save to cache
    pdf_cache[cache_key] = (pdf_bytes, time.time())
    return pdf_bytes
