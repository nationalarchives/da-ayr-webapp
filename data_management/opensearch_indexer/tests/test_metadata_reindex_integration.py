import os
from datetime import datetime
from uuid import uuid4

import pytest
from opensearch_indexer.index_consignment.bulk_index_consignment import (
    reindex_consignment_metadata,
)
from opensearchpy import OpenSearch
from sqlalchemy.orm import sessionmaker

from data_management.conftest import (
    Base,
    Body,
    Consignment,
    File,
    FileMetadata,
    Series,
)


@pytest.fixture
def metadata_reindex_index():
    endpoint = os.getenv("OPENSEARCH_INTEGRATION_URL")
    if not endpoint:
        pytest.skip("OPENSEARCH_INTEGRATION_URL is not configured")

    client = OpenSearch(
        hosts=[endpoint],
        use_ssl=endpoint.startswith("https://"),
        verify_certs=False,
    )
    if not client.ping():
        pytest.fail(
            f"OpenSearch integration endpoint is unavailable: {endpoint}"
        )

    index = f"metadata-reindex-integration-{uuid4().hex}"
    client.indices.create(index=index)
    try:
        yield client, index, endpoint
    finally:
        if client.indices.exists(index=index):
            client.indices.delete(index=index)


def test_metadata_reindex_updates_existing_document_from_database(
    database, metadata_reindex_index
):
    client, index, endpoint = metadata_reindex_index
    engine = database()
    Base.metadata.create_all(engine)
    body_id = uuid4()
    series_id = uuid4()
    consignment_id = uuid4()
    file_id = uuid4()
    consignment_reference = "metadata-reindex-integration"

    session = sessionmaker(bind=engine)()
    session.add_all(
        [
            Body(BodyId=body_id, Name="Test body", Description="Test body"),
            Series(
                SeriesId=series_id,
                BodyId=body_id,
                Name="Test series",
                Description="Test series",
            ),
            Consignment(
                ConsignmentId=consignment_id,
                SeriesId=series_id,
                ConsignmentType="Digital",
                ConsignmentReference=consignment_reference,
                TransferCompleteDatetime=datetime(2026, 1, 2, 3, 4, 5),
            ),
            File(
                FileId=file_id,
                ConsignmentId=consignment_id,
                FileReference="file-reference",
                FileType="File",
                FileName="record.txt",
                FilePath="/record.txt",
            ),
            FileMetadata(
                MetadataId=uuid4(),
                FileId=file_id,
                PropertyName="custom_metadata",
                Value="from database",
            ),
        ]
    )
    session.commit()
    session.close()

    client.index(
        index=index,
        id=str(file_id),
        body={
            "file_id": str(file_id),
            "file_name": "stale-record.txt",
            "custom_metadata": "stale value",
            "content": "previously extracted content",
        },
    )
    client.indices.refresh(index=index)

    updated_count = reindex_consignment_metadata(
        consignment_reference,
        database.url(),
        endpoint,
        ("", ""),
        60,
        open_search_use_ssl=endpoint.startswith("https://"),
        open_search_verify_certs=False,
        opensearch_index=index,
    )

    updated_document = client.get(index=index, id=str(file_id))["_source"]
    assert updated_count == 1
    assert updated_document["file_name"] == "record.txt"
    assert updated_document["custom_metadata"] == "from database"
    assert (
        updated_document["consignment_transfer_complete_date"]
        == "2026-01-02T03:04:05"
    )
    assert updated_document["content"] == "previously extracted content"
