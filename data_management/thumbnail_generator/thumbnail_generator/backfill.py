"""
Thumbnail Generator Backfill — AYR-1594 POC

Queries the database for all renderable files (native PDFs and converted access
copies) and runs the thumbnail generator for each one, skipping any that have
already been generated.

DB auth modes
-------------
Direct (local / basic auth):
    Set DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD.

RDS IAM (AWS):
    Set DB_SECRET_ID (Secrets Manager secret containing host/port/username/
    dbname/proxy).  An IAM auth token is generated automatically.
    Requires rds-db:connect permission on the IAM role.

Usage
-----
Local (MinIO + local Postgres):

    AWS_ENDPOINT_URL=http://127.0.0.1:9000 \
    AWS_ACCESS_KEY_ID=ROOTNAME \
    AWS_SECRET_ACCESS_KEY=CHANGEME123 \
    AWS_REGION=eu-west-2 \
    DB_HOST=localhost \
    DB_PORT=5434 \
    DB_NAME=local_db \
    DB_USER=local_db_user \
    DB_PASSWORD=local_db_user_password \
    RECORD_BUCKET=test-record-download \
    ACCESS_COPY_BUCKET=test-record-download \
    RENDERED_BUCKET=test-thumbnail-bucket \
    poetry run python data_management/thumbnail_generator/thumbnail_generator/backfill.py

AWS / staging (RDS IAM auth):

    AWS_REGION=eu-west-2 \
    DB_SECRET_ID=<secretsmanager-secret-id> \
    RECORD_BUCKET=<record-bucket> \
    ACCESS_COPY_BUCKET=<access-copy-bucket> \
    RENDERED_BUCKET=<rendered-pages-bucket> \
    poetry run python data_management/thumbnail_generator/thumbnail_generator/backfill.py

Required environment variables
-------------------------------
    RECORD_BUCKET       bucket containing native PDFs
    ACCESS_COPY_BUCKET  bucket containing converted PDFs
    RENDERED_BUCKET     bucket to write rendered images to

    One of:
      DB_SECRET_ID                        (AWS / RDS IAM auth)
      DB_HOST, DB_PORT, DB_NAME,          (direct auth)
      DB_USER, DB_PASSWORD

Optional
--------
    DB_SSL_ROOT_CERTIFICATE   path to RDS CA bundle (direct auth only)
    FORCE_REGENERATE          set to "true" to re-render already-generated files
    DRY_RUN                   set to "true" to list files without rendering
"""

import json
import logging
import os
import sys
from urllib.parse import quote_plus

import boto3
from main import process
from sqlalchemy import MetaData, Table, create_engine, select

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# PUIDs that are served directly from the record bucket as-is
NATIVE_PDF_PUIDS = {
    "fmt/16",
    "fmt/17",
    "fmt/18",
    "fmt/19",
    "fmt/20",
    "fmt/276",
}

# PUIDs whose converted PDF lives in the access copy bucket
CONVERTIBLE_PUIDS = {
    "fmt/39",
    "fmt/40",
    "x-fmt/44",
    "x-fmt/45",
    "fmt/50",
    "fmt/59",
    "fmt/61",
    "x-fmt/111",
    "x-fmt/116",
    "fmt/126",
    "fmt/214",
    "fmt/215",
    "fmt/355",
    "x-fmt/394",
    "fmt/412",
    "x-fmt/115",
    "fmt/116",
    "x-fmt/258",
    "fmt/443",
    "fmt/1510",
    "x-fmt/255",
    "x-fmt/332",
    "x-fmt/18",
}

ALL_RENDERABLE_PUIDS = NATIVE_PDF_PUIDS | CONVERTIBLE_PUIDS


def _get_engine_direct():
    """Build engine using explicit DB_HOST/DB_USER/DB_PASSWORD env vars."""

    rds = boto3.client("rds")
    host = os.environ["DB_HOST"]
    port = os.environ["DB_PORT"]
    name = os.environ["DB_NAME"]
    user = os.environ["DB_USER"]
    password = quote_plus(os.environ["DB_PASSWORD"])
    ssl_cert = os.getenv("DB_SSL_ROOT_CERTIFICATE")

    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
    connect_args = {}
    if ssl_cert:
        connect_args["sslrootcert"] = ssl_cert
        connect_args["sslmode"] = "verify-full"

    token = rds.generate_db_auth_token(
        DBHostname=host, Port=port, DBUsername=user
    )
    print("Generated IAM auth token for RDS")
    url = (
        f"postgresql+psycopg2://{user}:{quote_plus(token)}"
        f"@{host}:{port}/{name}"
    )
    return create_engine(
        url,
        connect_args={"sslmode": "require"},
    )


def get_engine():
    logger.info("Using direct DB auth (DB_HOST/DB_USER/DB_PASSWORD)")
    return _get_engine_direct()


def get_renderable_files(conn):
    """
    Return a list of dicts describing every renderable file::

        {
            "file_id": str,
            "consignment_ref": str,
            "puid": str,
            "bucket": str,           # which S3 bucket the source PDF is in
        }
    """
    meta = MetaData()
    file_table = Table("File", meta, autoload_with=conn)
    consignment_table = Table("Consignment", meta, autoload_with=conn)
    ffid_table = Table("FFIDMetadata", meta, autoload_with=conn)

    stmt = (
        select(
            file_table.c.FileId,
            consignment_table.c.ConsignmentReference,
            ffid_table.c.PUID,
        )
        .join(
            consignment_table,
            file_table.c.ConsignmentId == consignment_table.c.ConsignmentId,
        )
        .join(ffid_table, file_table.c.FileId == ffid_table.c.FileId)
        .where(file_table.c.FileType == "File")
    )

    record_bucket = os.environ["RECORD_BUCKET"]
    access_copy_bucket = os.environ["ACCESS_COPY_BUCKET"]

    results = []
    for row in conn.execute(stmt):
        file_id, consignment_ref, puid = row
        if puid is None:
            continue
        puid = puid.lower()
        if puid in NATIVE_PDF_PUIDS:
            bucket = record_bucket
        elif puid in CONVERTIBLE_PUIDS:
            bucket = access_copy_bucket
        else:
            continue
        results.append(
            {
                "file_id": str(file_id),
                "consignment_ref": consignment_ref,
                "puid": puid,
                "bucket": bucket,
            }
        )

    return results


def run_backfill():
    rendered_bucket = os.environ["RENDERED_BUCKET"]
    force_regenerate = os.getenv("FORCE_REGENERATE", "").lower() == "true"
    dry_run = os.getenv("DRY_RUN", "").lower() == "true"

    engine = get_engine()
    with engine.connect() as conn:
        files = get_renderable_files(conn)

    logger.info(f"Found {len(files)} renderable file(s)")
    if dry_run:
        for f in files:
            logger.info(
                f"  [DRY RUN] {f['consignment_ref']}/{f['file_id']} ({f['puid']}) from {f['bucket']}"
            )
        return

    succeeded = 0
    skipped = 0
    failed = 0

    for i, f in enumerate(files, 1):
        file_id = f["file_id"]
        consignment_ref = f["consignment_ref"]
        s3_key = f"{consignment_ref}/{file_id}"
        logger.info(
            f"[{i}/{len(files)}] {consignment_ref}/{file_id} ({f['puid']})"
        )
        try:
            result = process(
                source_bucket=f["bucket"],
                s3_key=s3_key,
                rendered_bucket=rendered_bucket,
                consignment_ref=consignment_ref,
                file_id=file_id,
                force_regenerate=force_regenerate,
            )
            if result.get("skipped"):
                skipped += 1
            else:
                succeeded += 1
        except Exception as e:
            logger.error(f"  FAILED: {e}")
            failed += 1

    logger.info(
        f"\nBackfill complete — "
        f"succeeded: {succeeded}, skipped: {skipped}, failed: {failed}"
    )
    if failed:
        sys.exit(1)


def lambda_handler(event: dict, context) -> dict:
    """
    Lambda entry point — two modes depending on ``event["mode"]``:

    "run" (default) — full backfill in a single invocation
    --------------------------------------------------------
    Queries the DB, renders every unprocessed file, returns a summary.
    Suitable for small amount of records.  Will hit the 15-minute Lambda timeout for
    large datasets — use "fanout" mode instead.

    Event schema::

        {
            "mode": "run",           // optional, default
            "force_regenerate": false
        }

    "fanout" — coordinator for large amount of records
    -----------------------------------------
    Queries the DB and sends one SQS message per file.  Each message is
    consumed by the per-file ``lambda_handler`` in ``main.py``, which can
    run in parallel across many Lambda instances with no timeout risk.

    Requires SQS_QUEUE_URL env var pointing at the processing queue.

    Event schema::

        {
            "mode": "fanout",
            "force_regenerate": false
        }

    Environment variables (both modes)
    -----------------------------------
        DB_SECRET_ID or DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD
        RECORD_BUCKET, ACCESS_COPY_BUCKET, RENDERED_BUCKET
        SQS_QUEUE_URL   (fanout mode only)
    """
    mode = event.get("mode", "run")

    if mode == "fanout":
        return _lambda_fanout(event)
    return _lambda_run(event)


def _lambda_run(event: dict) -> dict:
    """Run the full backfill inside a single Lambda invocation."""
    force_regenerate = event.get("force_regenerate", False)
    rendered_bucket = os.environ["RENDERED_BUCKET"]

    engine = get_engine()
    with engine.connect() as conn:
        files = get_renderable_files(conn)

    logger.info(f"Found {len(files)} renderable file(s)")

    succeeded = skipped = failed = 0
    for i, f in enumerate(files, 1):
        file_id = f["file_id"]
        consignment_ref = f["consignment_ref"]
        logger.info(f"[{i}/{len(files)}] {consignment_ref}/{file_id}")
        try:
            result = process(
                source_bucket=f["bucket"],
                s3_key=f"{consignment_ref}/{file_id}",
                rendered_bucket=rendered_bucket,
                consignment_ref=consignment_ref,
                file_id=file_id,
                force_regenerate=force_regenerate,
            )
            if result.get("skipped"):
                skipped += 1
            else:
                succeeded += 1
        except Exception as e:
            logger.error(f"  FAILED {file_id}: {e}")
            failed += 1

    return {"succeeded": succeeded, "skipped": skipped, "failed": failed}


def _lambda_fanout(event: dict) -> dict:
    """
    Query the DB and enqueue one SQS message per file.
    Each message is consumed by the per-file lambda_handler in main.py.
    """
    sqs = boto3.client("sqs")
    queue_url = os.environ["SQS_QUEUE_URL"]
    rendered_bucket = os.environ["RENDERED_BUCKET"]
    force_regenerate = event.get("force_regenerate", False)

    engine = get_engine()
    with engine.connect() as conn:
        files = get_renderable_files(conn)

    logger.info(f"Enqueuing {len(files)} file(s) → {queue_url}")

    enqueued = 0
    for f in files:
        message = {
            "source_bucket": f["bucket"],
            "rendered_bucket": rendered_bucket,
            "s3_key": f"{f['consignment_ref']}/{f['file_id']}",
            "file_id": f["file_id"],
            "consignment_ref": f["consignment_ref"],
            "force_regenerate": force_regenerate,
        }
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
        )
        enqueued += 1

    logger.info(f"Enqueued {enqueued} messages")
    return {"enqueued": enqueued}


if __name__ == "__main__":
    run_backfill()
