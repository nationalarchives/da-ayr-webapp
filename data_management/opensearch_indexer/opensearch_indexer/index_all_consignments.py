"""
Script to index all consignments from the database into OpenSearch.

This script is intended for local development to populate OpenSearch with all
test data from the postgres database and minio bucket.

Usage:
    python -m data_management.opensearch_indexer.opensearch_indexer.index_all_consignments

Required environment variables:
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_SSL_ROOT_CERTIFICATE
    AWS_ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, RECORD_BUCKET_NAME
    OPEN_SEARCH_HOST, OPEN_SEARCH_USERNAME, OPEN_SEARCH_PASSWORD
    OPEN_SEARCH_CA_CERTS, OPEN_SEARCH_TIMEOUT (optional, defaults to 60)
"""

import logging
import os
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from .index_consignment.bulk_index_consignment import bulk_index_consignment

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_all_consignment_references(database_url: str) -> list[str]:
    """
    Fetch all consignment references from the database.

    Args:
        database_url (str): The database connection URL.

    Returns:
        list[str]: A list of consignment references.
    """
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    query = """
    SELECT DISTINCT "ConsignmentReference"
    FROM "Consignment"
    ORDER BY "ConsignmentReference";
    """

    try:
        result = session.execute(text(query)).fetchall()
        consignment_references = [row[0] for row in result]
        logger.info(
            f"Found {len(consignment_references)} consignments in database"
        )
        return consignment_references
    finally:
        session.close()


def build_database_url() -> str:
    """Build database URL from environment variables."""
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_ssl_cert = os.getenv("DB_SSL_ROOT_CERTIFICATE")

    if not all([db_host, db_port, db_name, db_user, db_password]):
        raise ValueError(
            "Missing required database environment variables: "
            "DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD"
        )

    database_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # Only use SSL if cert file exists
    if db_ssl_cert and os.path.exists(db_ssl_cert):
        database_url += f"?sslmode=verify-full&sslrootcert={db_ssl_cert}"

    return database_url


def main():
    """Index all consignments from the database into OpenSearch."""
    logger.info("Starting indexing of all consignments")

    # Build database URL
    database_url = build_database_url()

    # Get OpenSearch configuration from environment
    bucket_name = os.getenv("RECORD_BUCKET_NAME")
    open_search_host_url = os.getenv("OPEN_SEARCH_HOST")
    open_search_username = os.getenv("OPEN_SEARCH_USERNAME", "")
    open_search_password = os.getenv("OPEN_SEARCH_PASSWORD", "")
    open_search_ca_certs = os.getenv("OPEN_SEARCH_CA_CERTS")
    open_search_timeout = int(os.getenv("OPEN_SEARCH_TIMEOUT", "60"))
    open_search_use_ssl = (
        os.getenv("OPEN_SEARCH_USE_SSL", "true").lower() == "true"
    )
    open_search_verify_certs = (
        os.getenv("OPEN_SEARCH_VERIFY_CERTS", "true").lower() == "true"
    )

    if not all([bucket_name, open_search_host_url]):
        raise ValueError(
            "Missing required OpenSearch environment variables: "
            "RECORD_BUCKET_NAME, OPEN_SEARCH_HOST"
        )

    # Use auth only if both username and password are provided
    open_search_http_auth = (
        (open_search_username, open_search_password)
        if open_search_username and open_search_password
        else None
    )

    # Get all consignment references
    consignment_references = get_all_consignment_references(database_url)

    if not consignment_references:
        logger.warning("No consignments found in database")
        return

    # Index each consignment
    failed_consignments = []
    for i, consignment_reference in enumerate(consignment_references, 1):
        logger.info(
            f"Indexing consignment {i}/{len(consignment_references)}: {consignment_reference}"
        )
        try:
            bulk_index_consignment(
                consignment_reference,
                bucket_name,
                database_url,
                open_search_host_url,
                open_search_http_auth,
                open_search_timeout,
                open_search_ca_certs,
                open_search_use_ssl,
                open_search_verify_certs,
            )
            logger.info(f"Successfully indexed {consignment_reference}")
        except Exception as e:
            logger.error(
                f"Failed to index {consignment_reference}: {e}", exc_info=True
            )
            failed_consignments.append(consignment_reference)

    # Summary
    logger.info(
        f"\n{'='*60}\nIndexing complete\n"
        f"Total consignments: {len(consignment_references)}\n"
        f"Successfully indexed: {len(consignment_references) - len(failed_consignments)}\n"
        f"Failed: {len(failed_consignments)}\n{'='*60}"
    )

    if failed_consignments:
        logger.error(f"Failed consignments: {', '.join(failed_consignments)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
