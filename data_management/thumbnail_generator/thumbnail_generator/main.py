"""
Thumbnail Generator — AYR-1594 POC

Pre-generates full-size page images and thumbnails for a PDF document and
stores them in S3.  The manifest endpoint can then serve presigned URLs to
these pre-rendered objects instead of rasterising the PDF on every request.

S3 key scheme
-------------
  {consignment_ref}/{file_id}/pages/{page_number}.jpg   ← full-size (150 DPI)
  {consignment_ref}/{file_id}/thumbs/{page_number}.jpg  ← thumbnail (≤150×200)
  {consignment_ref}/{file_id}/metadata.json             ← page count + dimensions

The metadata file lets the manifest be generated without downloading the PDF at
all

Entry points
------------
  ECS task  : python main.py   (reads config from environment variables)
  Lambda    : handler exported as ``lambda_handler`` (reads from event or env)

Required environment variables (ECS) / event keys (Lambda)
-----------------------------------------------------------
  SOURCE_BUCKET     S3 bucket containing the source PDF
  RENDERED_BUCKET   S3 bucket to write rendered images to (can be same bucket)
  S3_KEY            Full S3 key of the source PDF, e.g. TDR-2024-ABC/<uuid>
  FILE_ID           The file UUID (used to build output key prefix)
  CONSIGNMENT_REF   The consignment reference (used to build output key prefix)

Optional
--------
  DPI               Render DPI (default 150, matches current render_utils.py)
  FORCE_REGENERATE  Set to "true" to re-render even when images already exist
"""

import io
import json
import logging
import os

import boto3
import pymupdf
from botocore.exceptions import ClientError
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

s3 = boto3.client("s3")

DPI = int(os.environ.get("DPI", "150"))
THUMBNAIL_SIZE = (150, 200)
JPEG_QUALITY_FULL = 75
JPEG_QUALITY_THUMB = 70


# ---------------------------------------------------------------------------
# S3 helpers
# ---------------------------------------------------------------------------


def get_pdf_from_s3(bucket: str, key: str) -> bytes:
    logger.info(f"Downloading s3://{bucket}/{key}")
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response["Body"].read()
    logger.info(f"Downloaded {len(data) / 1_048_576:.2f} MB")
    return data


def put_object(bucket: str, key: str, body: bytes, content_type: str) -> None:
    s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType=content_type)
    logger.debug(f"  Uploaded s3://{bucket}/{key} ({len(body):,} bytes)")


def pregenerated_images_exist(
    rendered_bucket: str, consignment_ref: str, file_id: str
) -> bool:
    """Return True if page 1 already exists == already generated."""
    key = f"{consignment_ref}/{file_id}/pages/1.jpg"
    try:
        s3.head_object(Bucket=rendered_bucket, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchKey"):
            return False
        raise


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def render_pdf(
    pdf_bytes: bytes,
    rendered_bucket: str,
    consignment_ref: str,
    file_id: str,
) -> dict:
    """
    Rasterise every page of *pdf_bytes* and upload images + thumbnails to S3.

    Returns a summary dict::

        {
            "page_count": int,
            "pages": [{"page": int, "width": int, "height": int}, ...],
            "total_bytes_uploaded": int,
        }
    """
    prefix = f"{consignment_ref}/{file_id}"
    total_bytes = 0
    pages_meta = []

    with pymupdf.open("pdf", io.BytesIO(pdf_bytes)) as pdf_doc:
        page_count = pdf_doc.page_count
        logger.info(
            f"Rendering {page_count} pages at {DPI} DPI → s3://{rendered_bucket}/{prefix}/"
        )

        for page_num in range(page_count):
            page_number = page_num + 1
            page = pdf_doc.load_page(page_num)
            mat = pymupdf.Matrix(DPI / 72, DPI / 72)
            pix = page.get_pixmap(matrix=mat)

            # Build a PIL image from the pixmap samples
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

            # --- Full-size JPEG ---
            full_buf = io.BytesIO()
            img.save(
                full_buf,
                format="JPEG",
                quality=JPEG_QUALITY_FULL,
                optimize=True,
            )
            full_bytes = full_buf.getvalue()
            put_object(
                rendered_bucket,
                f"{prefix}/pages/{page_number}.jpg",
                full_bytes,
                "image/jpeg",
            )
            total_bytes += len(full_bytes)

            # --- Thumbnail JPEG ---
            thumb = img.copy()
            thumb.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            thumb_buf = io.BytesIO()
            thumb.save(
                thumb_buf,
                format="JPEG",
                quality=JPEG_QUALITY_THUMB,
                optimize=True,
            )
            thumb_bytes = thumb_buf.getvalue()
            put_object(
                rendered_bucket,
                f"{prefix}/thumbs/{page_number}.jpg",
                thumb_bytes,
                "image/jpeg",
            )
            total_bytes += len(thumb_bytes)

            pages_meta.append(
                {"page": page_number, "width": img.width, "height": img.height}
            )

            logger.info(
                f"  Page {page_number}/{page_count}: "
                f"full={len(full_bytes)/1024:.1f} KB, "
                f"thumb={len(thumb_bytes)/1024:.1f} KB"
            )

            img.close()
            thumb.close()
            pix = None

    # --- Metadata JSON ---
    # Stored alongside the images so the manifest endpoint can read page
    # dimensions without having to download the PDF itself.
    metadata = {
        "file_id": file_id,
        "consignment_ref": consignment_ref,
        "dpi": DPI,
        "page_count": page_count,
        "pages": pages_meta,
    }
    meta_bytes = json.dumps(metadata, indent=2).encode()
    put_object(
        rendered_bucket,
        f"{prefix}/metadata.json",
        meta_bytes,
        "application/json",
    )
    total_bytes += len(meta_bytes)

    return {
        "page_count": page_count,
        "pages": pages_meta,
        "total_bytes_uploaded": total_bytes,
    }


# ---------------------------------------------------------------------------
# Processing logic (shared by Lambda and ECS entry points)
# ---------------------------------------------------------------------------


def process(
    source_bucket: str,
    s3_key: str,
    rendered_bucket: str,
    consignment_ref: str,
    file_id: str,
    force_regenerate: bool = False,
) -> dict:
    if not force_regenerate and pregenerated_images_exist(
        rendered_bucket, consignment_ref, file_id
    ):
        logger.info(
            f"Pre-generated images already exist for {file_id} — skipping. "
            "Set FORCE_REGENERATE=true to override."
        )
        return {"skipped": True, "file_id": file_id}

    pdf_bytes = get_pdf_from_s3(source_bucket, s3_key)
    result = render_pdf(pdf_bytes, rendered_bucket, consignment_ref, file_id)
    result["skipped"] = False
    result["file_id"] = file_id

    logger.info(
        f"Done: {result['page_count']} pages, "
        f"{result['total_bytes_uploaded'] / 1_048_576:.2f} MB uploaded to "
        f"s3://{rendered_bucket}"
    )
    return result


# ---------------------------------------------------------------------------
# Lambda entry point
# ---------------------------------------------------------------------------


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda entry point.

    Event schema (all fields fall back to the corresponding environment
    variable if omitted)::

        {
            "source_bucket":   "ayr-record-bucket",
            "rendered_bucket": "ayr-rendered-pages",
            "s3_key":          "TDR-2024-ABC/<file-uuid>",
            "file_id":         "<file-uuid>",
            "consignment_ref": "TDR-2024-ABC",
            "force_regenerate": false
        }
    """
    source_bucket = event.get("source_bucket") or os.environ["SOURCE_BUCKET"]
    rendered_bucket = (
        event.get("rendered_bucket") or os.environ["RENDERED_BUCKET"]
    )
    s3_key = event.get("s3_key") or os.environ["S3_KEY"]
    file_id = event.get("file_id") or os.environ["FILE_ID"]
    consignment_ref = (
        event.get("consignment_ref") or os.environ["CONSIGNMENT_REF"]
    )
    force_regenerate = event.get("force_regenerate", False) or (
        os.environ.get("FORCE_REGENERATE", "").lower() == "true"
    )

    return process(
        source_bucket,
        s3_key,
        rendered_bucket,
        consignment_ref,
        file_id,
        force_regenerate,
    )


# ---------------------------------------------------------------------------
# ECS / standalone entry point
# ---------------------------------------------------------------------------


def main():
    source_bucket = os.environ["SOURCE_BUCKET"]
    rendered_bucket = os.environ["RENDERED_BUCKET"]
    s3_key = os.environ["S3_KEY"]
    file_id = os.environ["FILE_ID"]
    consignment_ref = os.environ["CONSIGNMENT_REF"]
    force_regenerate = os.environ.get("FORCE_REGENERATE", "").lower() == "true"

    result = process(
        source_bucket,
        s3_key,
        rendered_bucket,
        consignment_ref,
        file_id,
        force_regenerate,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
