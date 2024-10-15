from typing import Optional

from requests_aws4auth import AWS4Auth
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from .index_file_content_and_metadata_in_opensearch import (
    index_file_content_and_metadata_in_opensearch,
)
from .index_file_content_and_metadata_in_opensearch_from_aws import get_s3_file


def get_file_ids_with_consignment_references(database_url):
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    query = """
    SELECT
        f."FileId" AS file_id,
        c."ConsignmentReference" AS consignment_reference
    FROM
        "File" f
    JOIN
        "Consignment" c ON f."ConsignmentId" = c."ConsignmentId"
    WHERE
        f."FileType"='File';
    """
    results = session.execute(text(query)).fetchall()

    session.close()

    return [
        (result.file_id, result.consignment_reference) for result in results
    ]


def index_file_content_and_metadata_in_opensearch_for_all_files_in_db(
    bucket_name: str,
    database_url: str,
    open_search_host_url: str,
    open_search_http_auth: AWS4Auth,
    open_search_ca_certs: Optional[str] = None,
):
    """
    Assumes db and s3 bucket have corresponding files.
    """
    files_ids_with_congisngment_refs = get_file_ids_with_consignment_references(
        database_url
    )
    for file_id, consignment_reference in files_ids_with_congisngment_refs:
        try:
            object_key = f"{consignment_reference}/{file_id}"
            file_stream = get_s3_file(bucket_name, object_key)
            index_file_content_and_metadata_in_opensearch(
                file_id,
                file_stream,
                database_url,
                open_search_host_url,
                open_search_http_auth,
                open_search_ca_certs,
            )
        except Exception as e:
            print(
                f"Error extracting text content from file_id: {file_id} "
                f"(in consignment_reference: {consignment_reference})"
            )
            print(e)
