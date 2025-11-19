import logging
import tempfile
from typing import Any, Dict, Union

import textract
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def index_file_content_and_metadata_in_opensearch(
    file_id: str,
    file_stream: bytes,
    database_url: str,
    open_search_host_url: str,
    open_search_http_auth: AWS4Auth,
) -> None:
    """
    Extracts file metadata from the database, adds the file content, and indexes it in OpenSearch.
    """
    file_data = _fetch_file_data(file_id, database_url)
    file_data_with_text_content = _add_text_content(file_data, file_stream)
    _index_in_opensearch(
        file_id,
        file_data_with_text_content,
        open_search_host_url,
        open_search_http_auth,
    )


def _add_text_content(
    file_data: Dict[str, Any], file_stream: bytes
) -> Dict[str, Any]:
    file_type = file_data["file_name"].split(".")[-1].lower()
    new_file_data = file_data
    if file_type in ["txt", "docx", "pdf", "pptx", "xlsx"]:
        new_file_data["content"] = extract_text(file_stream)
    return new_file_data


def _fetch_file_data(
    file_id: str, database_url: str
) -> Dict[str, Union[str, Dict[str, str]]]:
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
        f."FileId" = :file_id;
    """
    result = session.execute(text(query), {"file_id": file_id}).fetchall()

    session.close()

    file_data = {
        "file_id": result[0].file_id,
        "file_name": result[0].file_name,
        "file_reference": result[0].file_reference,
        "file_path": result[0].file_path,
        "citeable_reference": result[0].citeable_reference,
        "series_id": result[0].series_id,
        "series_name": result[0].series_name,
        "transferring_body": result[0].transferring_body,
        "transferring_body_id": result[0].transferring_body_id,
        "transferring_body_description": result[
            0
        ].transferring_body_description,
        "consignment_id": result[0].consignment_id,
        "consignment_reference": result[0].consignment_reference,
        "metadata": {
            row.PropertyName: row.Value
            for row in result
            if row.PropertyName is not None
        },
    }

    return file_data


def extract_text(file_stream: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=True) as temp:
        temp.write(file_stream)
        temp.flush()
        context = textract.process(temp.name)
    return context.decode("utf-8")


def _index_in_opensearch(
    file_id: str,
    document: Dict[str, Any],
    open_search_host_url: str,
    open_search_http_auth: AWS4Auth,
) -> None:
    open_search = OpenSearch(
        open_search_host_url,
        http_auth=open_search_http_auth,
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection,
    )
    open_search.index(index="documents", id=file_id, body=document)
