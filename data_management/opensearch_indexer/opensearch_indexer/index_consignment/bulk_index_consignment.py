import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple, Union

import sqlalchemy
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from ..aws_helpers import (
    _build_db_url,
    _get_opensearch_auth,
    get_s3_file,
)
from ..text_extraction import TextExtractionStatus, add_text_content

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ConsignmentBulkIndexError(Exception):
    """
    Custom exception raised when bulk indexing a consignment fails due to errors
    in text extraction or OpenSearch bulk indexing.
    """

    pass


def bulk_index_consignment_from_aws(
    consignment_reference: str,
    secret_string: Dict[str, Any],
    db_secret_string: Dict[str, Any],
) -> None:
    """
    Retrieve credentials and host information from AWS Secrets Manager, fetch consignment data,
    and index it in OpenSearch.

    Args:
        consignment_reference (str): The reference identifier for the consignment.
        secret_string (str):  AWS secret storing s3 record bucket name,
            and database and OpenSearch credentials.
        db_secret_string (str): AWS secret storing database credentials.

    Returns:
        None
    """
    bucket_name = secret_string["RECORD_BUCKET_NAME"]
    database_url = _build_db_url(db_secret_string)
    open_search_host_url = secret_string["OPEN_SEARCH_HOST"]
    open_search_http_auth = _get_opensearch_auth(secret_string)
    open_search_bulk_index_timeout = int(
        secret_string["OPEN_SEARCH_BULK_INDEX_TIMEOUT"]
    )

    bulk_index_consignment(
        consignment_reference,
        bucket_name,
        database_url,
        open_search_host_url,
        open_search_http_auth,
        open_search_bulk_index_timeout,
    )


def bulk_index_consignment(
    consignment_reference: str,
    bucket_name: str,
    database_url: str,
    open_search_host_url: str,
    open_search_http_auth: Union[Tuple[str, str], AWS4Auth],
    open_search_bulk_index_timeout: int,
    open_search_ca_certs: Optional[str] = None,
    open_search_use_ssl: bool = True,
    open_search_verify_certs: bool = True,
) -> None:
    """
    Fetch files associated with a consignment and index them in OpenSearch.

    Args:
        consignment_reference (str): The unique reference identifying the consignment to be indexed.
        bucket_name (str): Name of the S3 bucket.
        database_url (str): Database connection URL.
        open_search_host_url (str): OpenSearch endpoint URL.
        open_search_http_auth (AWS4Auth or tuple): Authentication details for OpenSearch.
        open_search_bulk_index_timeout (int): Timeout for OpenSearch bulk indexing.
        open_search_ca_certs (str, optional): Path to a file containing OpenSearch CA certificates for verification.

    Raises:
        ConsignmentBulkIndexError: If errors occur during text extraction or bulk indexing.
    """
    files = fetch_files_in_consignment(consignment_reference, database_url)
    documents_to_index = construct_documents(files, bucket_name)

    text_extraction_error = validate_text_extraction(documents_to_index)

    bulk_index_error = None
    try:
        bulk_index_files_in_opensearch(
            documents_to_index,
            open_search_host_url,
            open_search_http_auth,
            open_search_bulk_index_timeout,
            open_search_ca_certs,
            open_search_use_ssl,
            open_search_verify_certs,
        )
    except Exception as bulk_indexing_exception:
        bulk_index_error = str(bulk_indexing_exception)

    if text_extraction_error or bulk_index_error:
        raise ConsignmentBulkIndexError(
            format_bulk_indexing_error_message(
                consignment_reference, text_extraction_error, bulk_index_error
            )
        )


def validate_text_extraction(documents: List[Dict]) -> Optional[str]:
    """
    Validate document text extraction statuses and return an error message if any documents failed.

    Args:
        documents (list): A list of dictionaries, each containing metadata and content of a document.

    Returns:
        Optional[str]: An error message if any documents failed text extraction, otherwise None.
    """
    errors = [
        f"\n{doc['file_id']}"
        for doc in documents
        if doc["document"]["text_extraction_status"]
        not in [
            TextExtractionStatus.SKIPPED.value,
            TextExtractionStatus.SUCCEEDED.value,
        ]
    ]
    if errors:
        return "Text extraction failed on the following documents:" + "".join(
            errors
        )
    return None


def construct_documents(files: List[Dict], bucket_name: str) -> List[Dict]:
    """
    Construct a list of documents to be indexed in OpenSearch from file metadata.

    Args:
        files (list): A list of file metadata dictionaries retrieved from the database.
        bucket_name (str): The name of the S3 bucket containing the files.

    Returns:
        list: A list of dictionaries, each representing a document to be indexed in OpenSearch.

    Raises:
        Exception: If a file cannot be retrieved from S3.
    """
    documents_to_index = []

    def process_file(file):
        thread_name = threading.current_thread().name
        object_key = f"{file['consignment_reference']}/{str(file['file_id'])}"
        logger.info(f"[{thread_name}] Processing file: {object_key}")

        try:
            file_stream = get_s3_file(bucket_name, object_key)
            document = add_text_content(file, file_stream)
            return {"file_id": file["file_id"], "document": document}
        except Exception as e:
            logger.error(f"Failed to obtain file {object_key}: {e}")
            raise

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_file, file) for file in files]

        for future in as_completed(futures):
            result = future.result()
            if result:
                documents_to_index.append(result)
    return documents_to_index


def fetch_files_in_consignment(
    consignment_reference: str, database_url: str
) -> List[Dict]:
    """
    Fetch file metadata associated with the given consignment reference, including FFID file extension.

    Args:
        consignment_reference (str): The unique reference identifying the consignment.
        database_url (str): The database connection URL.

    Returns:
        list: A list of dictionaries, each containing metadata for a file in the consignment.

    Raises:
        sqlalchemy.exc.ProgrammingError: If the database query fails.
    """
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    query = """
    SELECT
        f."FileId" AS file_id,
        f."FileName" AS file_name,
        f."FileReference" AS file_reference,
        f."FilePath" AS file_path,
        f."CiteableReference" AS citeable_reference,
        s."SeriesId" AS series_id,
        s."Name" AS series_name,
        b."Name" AS transferring_body,
        b."BodyId" AS transferring_body_id,
        b."Description" AS transferring_body_description,
        c."ConsignmentId" AS consignment_id,
        c."ConsignmentReference" AS consignment_reference,
        fm."PropertyName",
        fm."Value",
        ffid."Extension" AS file_extension
    FROM
        "File" f
    JOIN
        "Consignment" c ON f."ConsignmentId" = c."ConsignmentId"
    JOIN
        "Series" s ON c."SeriesId" = s."SeriesId"
    JOIN
        "Body" b ON s."BodyId" = b."BodyId"
    LEFT JOIN
        "FileMetadata" fm ON f."FileId" = fm."FileId"
    LEFT JOIN
        "FFIDMetadata" ffid ON f."FileId" = ffid."FileId"
    WHERE
        c."ConsignmentReference" = :consignment_reference
        AND f."FileType" = 'File';
    """
    try:
        result = session.execute(
            text(query), {"consignment_reference": consignment_reference}
        ).fetchall()
    except sqlalchemy.exc.ProgrammingError as e:
        logger.error(
            f"Failed to retrieve file metadata for consignment reference: {consignment_reference}"
        )
        session.close()
        raise e

    session.close()

    files_data = {}

    for row in result:
        file_id = str(row.file_id)
        if file_id not in files_data:
            files_data[file_id] = {
                "file_id": str(row.file_id),
                "file_name": str(row.file_name),
                "file_reference": str(row.file_reference),
                "file_path": str(row.file_path),
                "citeable_reference": str(row.citeable_reference),
                "series_id": str(row.series_id),
                "series_name": str(row.series_name),
                "transferring_body": str(row.transferring_body),
                "transferring_body_id": str(row.transferring_body_id),
                "transferring_body_description": str(
                    row.transferring_body_description
                ),
                "consignment_id": str(row.consignment_id),
                "consignment_reference": str(row.consignment_reference),
                "file_extension": str(row.file_extension),
            }

        if row.PropertyName:
            files_data[file_id][row.PropertyName] = str(row.Value)

    return list(files_data.values())


def bulk_index_files_in_opensearch(
    documents_to_index: List[Dict],
    host_url: str,
    http_auth: Union[Tuple[str, str], AWS4Auth],
    timeout: int = 60,
    ca_certs: Optional[str] = None,
    use_ssl: bool = True,
    verify_certs: bool = True,
) -> None:
    """
    Perform bulk indexing of documents into OpenSearch using the OpenSearch library.

    Args:
        documents_to_index (List[Dict[str, Union[str, Dict]]]): The documents to index.
        host_url (str): (str): The OpenSearch cluster URL.
        http_auth (Union[AWS4Auth, Tuple[str, str]]): The authentication credentials.
        timeout (int): Timeout in seconds for bulk indexing operations.
        ca_certs (Optional[str]): Path to CA certificates for SSL verification.
        use_ssl (bool): Whether to use SSL. Defaults to True.
        verify_certs (bool): Whether to verify SSL certificates. Defaults to True.

    Raises:
        Exception: If the bulk indexing operation fails.
    """
    index = "documents"

    client = OpenSearch(
        host_url,
        http_auth=http_auth,
        use_ssl=use_ssl,
        verify_certs=verify_certs,
        ca_certs=ca_certs,
        connection_class=RequestsHttpConnection,
    )

    actions = prepare_bulk_index_payload(documents_to_index, index)

    try:
        bulk_response = client.bulk(index=index, body=actions, timeout=timeout)
    except Exception as e:
        logger.error(f"Opensearch bulk indexing call failed: {e}")
        raise e

    logger.info("Opensearch bulk indexing call completed with response")
    logger.info(bulk_response)

    if bulk_response["errors"]:
        logger.info("Opensearch bulk indexing completed with errors")
        error_message = "Opensearch bulk indexing errors:"
        for item in bulk_response["items"]:
            if "error" in item.get("index", {}):
                error_message += f"\nError for document ID {item['index']['_id']}: {item['index']['error']}"
        raise Exception(error_message)
    else:
        logger.info("Opensearch bulk indexing completed successfully")


def format_bulk_indexing_error_message(
    consignment_reference: str,
    text_extraction_error: Optional[str],
    bulk_index_error: Optional[str],
) -> str:
    """
    Construct a detailed error message for bulk indexing failures.

    Args:
        consignment_reference (str): The unique reference identifying the consignment.
        text_extraction_error (str, optional): Error message related to text extraction.
        bulk_index_error (str, optional): Error message related to bulk indexing.

    Returns:
        str: A formatted error message detailing the issues.
    """
    error_message = (
        f"Bulk indexing failed for consignment {consignment_reference}:"
    )
    if text_extraction_error:
        error_message += f"\nText Extraction Errors:\n{text_extraction_error}"
    if bulk_index_error:
        error_message += f"\nBulk Index Errors:\n{bulk_index_error}"
    return error_message


def prepare_bulk_index_payload(
    documents: List[Dict[str, Union[str, Dict]]], opensearch_index: str
) -> str:
    bulk_data = []
    for doc in documents:
        bulk_data.append(
            json.dumps(
                {"index": {"_index": opensearch_index, "_id": doc["file_id"]}}
            )
        )
        bulk_data.append(json.dumps(doc["document"]))

    bulk_payload = "\n".join(bulk_data) + "\n"
    return bulk_payload
