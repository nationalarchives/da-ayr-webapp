import json
import logging
from typing import Dict, List, Optional, Tuple, Union

import pg8000
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from ..aws_helpers import (
    _build_db_url,
    _get_opensearch_auth,
    get_s3_file,
    get_secret_data,
)
from ..text_extraction import add_text_content

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def bulk_index_consignment_from_aws(
    consignment_reference: str, secret_id: str
) -> None:
    """
    Retrieve credentials and host information from AWS Secrets Manager, fetch consignment data,
    and index it in OpenSearch.

    Args:
        consignment_reference (str): The reference identifier for the consignment.
        secret_id (str): The ID of the AWS secret storing s3 record bucket name,
            and database and OpenSearch credentials.

    Returns:
        None
    """
    secret_string = get_secret_data(secret_id)
    bucket_name = secret_string["RECORD_BUCKET_NAME"]
    database_url = _build_db_url(secret_string)
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
    open_search_http_auth: Union[AWS4Auth, Tuple[str, str]],
    open_search_bulk_index_timeout: int = 60,
    open_search_ca_certs: Optional[str] = None,
) -> None:
    """
    Fetch files associated with a consignment and index them in OpenSearch.

    Args:
        consignment_reference (str): The consignment reference identifier.
        bucket_name (str): The S3 bucket name containing files.
        database_url (str): The connection string for the PostgreSQL database.
        open_search_host_url (str): The host URL of the OpenSearch cluster.
        open_search_http_auth (Union[AWS4Auth, Tuple[str, str]]): The authentication credentials for OpenSearch.
        open_search_ca_certs (Optional[str]): Path to CA certificates for SSL verification.

    Returns:
        None
    """
    files = _fetch_files_in_consignment(consignment_reference, database_url)
    documents_to_index = _construct_documents(files, bucket_name)
    bulk_index_files_in_opensearch(
        documents_to_index,
        open_search_host_url,
        open_search_http_auth,
        open_search_bulk_index_timeout,
        open_search_ca_certs,
    )


def _construct_documents(files: List[Dict], bucket_name: str) -> List[Dict]:
    """
    Construct a list of documents to be indexed in OpenSearch from file metadata.

    Args:
        files (List[Dict]): The list of file metadata dictionaries.
        bucket_name (str): The S3 bucket name where the files are stored.

    Returns:
        List[Dict]: A list of documents ready for indexing.
    """
    documents_to_index = []
    for file in files:
        object_key = file["consignment_reference"] + "/" + str(file["file_id"])

        logger.info(f"Processing file: {object_key}")

        file_stream = None
        document = file

        try:
            file_stream = get_s3_file(bucket_name, object_key)
        except Exception as e:
            logger.error(f"Failed to obtain file {object_key}: {e}")
            raise e

        document = add_text_content(file, file_stream)

        documents_to_index.append(
            {"file_id": file["file_id"], "document": document}
        )
    return documents_to_index


def _fetch_files_in_consignment(
    consignment_reference: str, database_url: str
) -> List[Dict]:
    """
    Fetch file metadata associated with the given consignment reference.

    Args:
        consignment_reference (str): The consignment reference identifier.
        database_url (str): The connection string for the PostgreSQL database.

    Returns:
        List[Dict]: A list of file metadata dictionaries.
    """
    engine = create_engine(database_url)
    Base = declarative_base()
    Base.metadata.reflect(bind=engine)
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
        fm."Value"
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
    WHERE
        c."ConsignmentReference" = :consignment_reference
        AND f."FileType" = 'File';
    """
    try:
        result = session.execute(
            text(query), {"consignment_reference": consignment_reference}
        ).fetchall()
    except pg8000.Error as e:
        logger.error(
            f"Failed to retrieve file metadata from database for consignment reference: {consignment_reference}"
        )
        session.close()
        raise e

    session.close()

    # Process query results
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
            }

        if row.PropertyName:
            files_data[file_id][row.PropertyName] = str(row.Value)

    return list(files_data.values())


def bulk_index_files_in_opensearch(
    documents: List[Dict[str, Union[str, Dict]]],
    open_search_host_url: str,
    open_search_http_auth: Union[AWS4Auth, Tuple[str, str]],
    open_search_bulk_index_timeout: int = 60,
    open_search_ca_certs: Optional[str] = None,
) -> None:
    """
    Perform bulk indexing of documents in OpenSearch.

    Args:
        documents (List[Dict[str, Union[str, Dict]]]): The documents to index.
        open_search_host_url (str): The OpenSearch cluster URL.
        open_search_http_auth (Union[AWS4Auth, Tuple[str, str]]): The authentication credentials.
        open_search_ca_certs (Optional[str]): Path to CA certificates for SSL verification.

    Returns:
        None
    """
    opensearch_index = "documents"

    bulk_data = []
    for doc in documents:
        bulk_data.append(
            json.dumps(
                {"index": {"_index": opensearch_index, "_id": doc["file_id"]}}
            )
        )
        bulk_data.append(json.dumps(doc["document"]))

    bulk_payload = "\n".join(bulk_data) + "\n"

    open_search = OpenSearch(
        open_search_host_url,
        http_auth=open_search_http_auth,
        use_ssl=True,
        verify_certs=True,
        ca_certs=open_search_ca_certs,
        connection_class=RequestsHttpConnection,
    )

    try:
        response = open_search.bulk(
            index=opensearch_index,
            body=bulk_payload,
            timeout=open_search_bulk_index_timeout,
        )
    except Exception as e:
        logger.error(f"Opensearch bulk indexing call failed: {e}")
        raise e

    logger.info("Opensearch bulk indexing call completed with response")
    logger.info(response)

    if response["errors"]:
        logger.info("Opensearch bulk indexing completed with errors")
        error_message = "Opensearch bulk indexing errors:"
        for item in response["items"]:
            if "error" in item.get("index", {}):
                error_message += f"\nError for document ID {item['index']['_id']}: {item['index']['error']}"
        raise Exception(error_message)
    else:
        logger.info("Opensearch bulk indexing completed successfully")
