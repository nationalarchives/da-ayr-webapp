import base64
import io
from typing import Any, List

import boto3
import pymupdf
from flask import Response, current_app, jsonify
from PIL import Image


def extract_pdf_pages_as_images(pdf_bytes: bytes) -> List[dict]:
    """Extract PDF pages as images and return page info with base64 thumbnails."""
    DPI = 150  # Output DPI for rendering

    print(f"PDF bytes length: {pdf_bytes}")
    try:
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
                thumbnail_data_url = (
                    f"data:image/jpeg;base64,{thumbnail_base64}"
                )

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
                        "thumbnail_base64_size": len(thumbnail_base64),
                        "page_base64_size": len(page_base64),
                    }
                )

                # Clean up resources
                page_image.close()
                thumbnail.close()
                pix = None

            return page_data
    except pymupdf.FileDataError as e:
        current_app.logger.error(f"Invalid PDF file: {e}")
        return []
    except Exception as e:
        current_app.logger.error(
            f"Error extracting PDF pages: {e}", exc_info=True
        )
        return []

def generate_pdf_manifest(
    file_name: str, file_url: str, manifest_url: str, file_obj: Any = None
) -> Response:
    """
    Generate an IIIF manifest for a PDF file, including page thumbnails and images if possible.

    Args:
        file_name (str): The display name of the file.
        file_url (str): The URL to the file.
        manifest_url (str): The manifest's own URL.
        file_obj (Any, optional): The File object for S3 access.

    Returns:
        Response: Flask JSON response containing the IIIF manifest.
    """
    FALLBACK_WIDTH = 800
    FALLBACK_HEIGHT = 1000
    page_data = []
    current_app.logger.info(
        f"Generating PDF manifest for {file_name}, file_obj: {file_obj is not None}"
    )

    try:
        s3 = boto3.client("s3")
        bucket = current_app.config["RECORD_BUCKET_NAME"]
        key = f"{file_obj.consignment.ConsignmentReference}/{file_obj.FileId}"

        current_app.logger.info(
            f"Fetching PDF from S3: bucket={bucket}, key={key}"
        )
        response = s3.get_object(Bucket=bucket, Key=key)
        pdf_bytes = response["Body"].read()
        current_app.logger.info(f"PDF bytes length: {len(pdf_bytes)}")

        page_data = extract_pdf_pages_as_images(pdf_bytes)
        current_app.logger.info(f"Extracted {len(page_data)} pages from PDF")
    except Exception as e:
        current_app.logger.error(
            f"Error processing PDF for thumbnails: {e}", exc_info=True
        )
        return jsonify({"error": "Failed to process PDF"}), 500

    # Manifest-level thumbnail (use first page if available)
    manifest_thumbnail = []
    if page_data:
        first_page = page_data[0]
        manifest_thumbnail = [
            {
                "id": first_page["thumbnail_url"],
                "type": "Image",
                "format": "image/jpeg",
                "height": 200,
                "width": 150,
            }
        ]

    items = []
    if page_data:
        for page_info in page_data:
            canvas_id = f"{manifest_url}/canvas/p{page_info['page_number']}"
            annotation_page_id = (
                f"{manifest_url}/page/p{page_info['page_number']}/1"
            )
            annotation_id = f"{manifest_url}/annotation/p{str(page_info['page_number']).zfill(4)}-image"
            items.append(
                {
                    "id": canvas_id,
                    "type": "Canvas",
                    "label": {"en": [f"Page {page_info['page_number']}"]},
                    "width": page_info["width"],
                    "height": page_info["height"],
                    "items": [
                        {
                            "id": annotation_page_id,
                            "type": "AnnotationPage",
                            "items": [
                                {
                                    "id": annotation_id,
                                    "type": "Annotation",
                                    "motivation": "painting",
                                    "body": {
                                        "id": page_info["page_image_url"],
                                        "type": "Image",
                                        "format": "image/jpeg",
                                        "height": page_info["height"],
                                        "width": page_info["width"],
                                    },
                                    "target": canvas_id,
                                }
                            ],
                        }
                    ],
                }
            )
    else:
        # Fallback to single canvas (original behavior)
        canvas_id = f"{manifest_url}/canvas/p0"
        annotation_page_id = f"{manifest_url}/page/p0/1"
        annotation_id = f"{manifest_url}/annotation/p0000-image"
        items.append(
            {
                "id": canvas_id,
                "type": "Canvas",
                "label": {"en": ["PDF Document"]},
                "width": FALLBACK_WIDTH,
                "height": FALLBACK_HEIGHT,
                "items": [
                    {
                        "id": annotation_page_id,
                        "type": "AnnotationPage",
                        "items": [
                            {
                                "id": annotation_id,
                                "type": "Annotation",
                                "motivation": "painting",
                                "body": {
                                    "id": file_url,
                                    "type": "Text",
                                    "format": "application/pdf",
                                },
                                "target": canvas_id,
                            }
                        ],
                    }
                ],
            }
        )

    manifest = {
        "@context": "http://iiif.io/api/presentation/3/context.json",
        "id": manifest_url,
        "type": "Manifest",
        "label": {"en": [file_name]},
        "summary": {"en": [f"Manifest for {file_name}"]},
        "thumbnail": manifest_thumbnail,
        "items": items,
    }

    current_app.logger.info(
        f"Generated PDF manifest with {len(items)} canvases for {file_name}"
    )
    return jsonify(manifest)