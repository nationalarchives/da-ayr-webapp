import base64
import contextlib
import io
from typing import List

import boto3
import pymupdf
from botocore.exceptions import ClientError
from flask import Response, current_app, jsonify, url_for
from PIL import Image

from app.main.db.models import File


@contextlib.contextmanager
def _open_pdf(pdf_bytes: bytes):
    """Open a PDF with MuPDF stderr suppressed; log any collected messages at DEBUG."""
    pymupdf.TOOLS.mupdf_display_errors(False)
    pymupdf.TOOLS.mupdf_display_warnings(False)
    try:
        with pymupdf.open("pdf", io.BytesIO(pdf_bytes)) as doc:
            yield doc
    except Exception as e:
        raise ValueError(f"Failed to open PDF: {e}") from e
    finally:
        messages = pymupdf.TOOLS.mupdf_warnings(reset=True)
        pymupdf.TOOLS.mupdf_display_errors(True)
        pymupdf.TOOLS.mupdf_display_warnings(True)
        if messages:
            current_app.logger.debug("MuPDF: %s", messages)


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

    with _open_pdf(pdf_bytes) as pdf_document:
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

    with _open_pdf(pdf_bytes) as pdf_document:
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
    current_app.logger.info(f"PDF bytes length: {len(pdf_bytes)}")

    canvas_items = []

    with _open_pdf(pdf_bytes) as pdf_document:
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

    pdf_url = url_for(
        "main.get_record_pdf", record_id=record_id, _external=True
    )

    search_url = url_for(
        "main.search_within_record", record_id=record_id, _external=True
    )

    manifest = {
        "@context": "https://iiif.io/api/presentation/3/context.json",
        "@type": "sc:Manifest",
        "@id": manifest_url,
        "label": {"en": [file_name]},
        "description": f"Manifest for {file_name}",
        "viewingDirection": "left-to-right",
        "service": {
            "@context": "http://iiif.io/api/search/1/context.json",
            "@id": search_url,
            "profile": "http://iiif.io/api/search/1/search",
            "label": "Search within this record",
        },
        "rendering": [
            {
                "@id": pdf_url,
                "@type": "dctypes:Text",
                "format": "application/pdf",
            }
        ],
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
    search_url: str,
    manifest_url: str,
    bucket: str,
    key: str,
) -> Response:
    """
    Search for text within a PDF and return a IIIF Content Search API v1 response.

    Args:
        query: The search term.
        search_url: The search service base URL (used in the response @id).
        manifest_url: The manifest URL (used to construct canvas @id values).
        bucket: S3 bucket name.
        key: S3 object key.

    Returns:
        Flask JSON response containing a IIIF sc:AnnotationList.
    """
    DPI = 150
    SCALE = DPI / 72

    pdf_bytes = get_pdf_from_s3(bucket, key)

    resources = []
    hits = []
    annotation_count = 0

    with _open_pdf(pdf_bytes) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            rects = page.search_for(query)
            canvas_id = f"{manifest_url}/canvas/{page_num + 1}"

            for rect in rects:
                annotation_count += 1
                annotation_id = f"{search_url}/annotation/{annotation_count}"

                x = int(rect.x0 * SCALE)
                y = int(rect.y0 * SCALE)
                w = int((rect.x1 - rect.x0) * SCALE)
                h = int((rect.y1 - rect.y0) * SCALE)

                matched_text = page.get_textbox(rect).strip() or query

                resources.append(
                    {
                        "@id": annotation_id,
                        "@type": "oa:Annotation",
                        "motivation": "sc:painting",
                        "resource": {
                            "@type": "cnt:ContentAsText",
                            "chars": matched_text,
                        },
                        "on": f"{canvas_id}#xywh={x},{y},{w},{h}",
                    }
                )
                hits.append(
                    {
                        "@type": "search:Hit",
                        "annotations": [annotation_id],
                        "match": matched_text,
                    }
                )

    result = {
        "@context": [
            "http://iiif.io/api/presentation/2/context.json",
            "http://iiif.io/api/search/1/context.json",
        ],
        "@id": f"{search_url}?q={query}",
        "@type": "sc:AnnotationList",
        "within": {
            "@type": "sc:Layer",
            "total": annotation_count,
        },
        "resources": resources,
        "hits": hits,
    }

    return jsonify(result)


def get_pdf_from_s3(bucket: str, key: str) -> bytes:
    """fetch PDF file from S3 and return its bytes."""
    s3 = boto3.client("s3")
    s3_object = s3.get_object(Bucket=bucket, Key=key)
    pdf_bytes = s3_object["Body"].read()

    return pdf_bytes
