from unittest import mock

from opensearch_indexer.index_consignment.bulk_index_consignment import (
    bulk_index_files_in_opensearch,
)
from opensearchpy import RequestsHttpConnection


@mock.patch(
    "opensearch_indexer.index_consignment.bulk_index_consignment.OpenSearch"
)
def test_index_file_content_and_metadata_in_opensearch(mock_open_search):
    """
    Given:
    - A file stream representing a text file.
    - An SQLite database mimicking the file data.
    - OpenSearch connection details.

    When:
    - The index_file_content_and_metadata_in_opensearch function is invoked.

    Then:
    - The relevant file data is fetched from the database.
    - The file's text content is extracted using real extract_text.
    - The file is indexed in OpenSearch with the extracted text.
    """
    open_search_host_url = "test_open_search_host_url"
    open_search_http_auth = mock.Mock()

    documents = [
        {
            "file_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
            "document": {
                "file_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
                "file_name": "path0",
                "file_reference": "ZD8MCK",
                "file_path": "data/E2E_tests/original/path0",
                "citeable_reference": "MOCK1 123/ZD8MCK",
                "series_id": "8bd7ad22-90d1-4c7f-ae00-645dfd1987cc",
                "series_name": "MOCK1 123",
                "transferring_body": "Mock 1 Department",
                "transferring_body_id": "8ccc8cd1-c0ee-431d-afad-70cf404ba337",
                "transferring_body_description": "Mock 1 Department",
                "consignment_id": "2fd4e03e-5913-4c04-b4f2-5a823fafd430",
                "consignment_reference": "TDR-2024-KKX4",
                "file_type": "File",
                "file_size": "1024",
                "rights_copyright": "Crown Copyright",
                "legal_status": "Public Record(s)",
                "held_by": "The National Archives, Kew",
                "date_last_modified": "2024-03-05T15:05:31",
                "closure_type": "Open",
                "title_closed": "false",
                "description_closed": "false",
                "language": "English",
                "content": "",
                "text_extraction_status": "n/a",
            },
        },
        {
            "file_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f",
            "document": {
                "file_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f",
                "file_name": "path2",
                "file_reference": "ZD8MCN",
                "file_path": "data/E2E_tests/original/path2",
                "citeable_reference": "MOCK1 123/ZD8MCN",
                "series_id": "8bd7ad22-90d1-4c7f-ae00-645dfd1987cc",
                "series_name": "MOCK1 123",
                "transferring_body": "Mock 1 Department",
                "transferring_body_id": "8ccc8cd1-c0ee-431d-afad-70cf404ba337",
                "transferring_body_description": "Mock 1 Department",
                "consignment_id": "2fd4e03e-5913-4c04-b4f2-5a823fafd430",
                "consignment_reference": "TDR-2024-KKX4",
                "file_type": "File",
                "file_size": "1024",
                "rights_copyright": "Crown Copyright",
                "legal_status": "Public Record(s)",
                "held_by": "The National Archives, Kew",
                "date_last_modified": "2024-03-05T15:05:31",
                "closure_type": "Open",
                "title_closed": "false",
                "description_closed": "false",
                "language": "English",
                "content": "",
                "text_extraction_status": "n/a",
            },
        },
        {
            "file_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270",
            "document": {
                "file_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270",
                "file_name": "path1",
                "file_reference": "ZD8MCL",
                "file_path": "data/E2E_tests/original/path1",
                "citeable_reference": "MOCK1 123/ZD8MCL",
                "series_id": "8bd7ad22-90d1-4c7f-ae00-645dfd1987cc",
                "series_name": "MOCK1 123",
                "transferring_body": "Mock 1 Department",
                "transferring_body_id": "8ccc8cd1-c0ee-431d-afad-70cf404ba337",
                "transferring_body_description": "Mock 1 Department",
                "consignment_id": "2fd4e03e-5913-4c04-b4f2-5a823fafd430",
                "consignment_reference": "TDR-2024-KKX4",
                "file_type": "File",
                "file_size": "1024",
                "rights_copyright": "Crown Copyright",
                "legal_status": "Public Record(s)",
                "held_by": "The National Archives, Kew",
                "date_last_modified": "2024-03-05T15:05:31",
                "closure_type": "Open",
                "title_closed": "false",
                "description_closed": "false",
                "language": "English",
                "content": "",
                "text_extraction_status": "n/a",
            },
        },
    ]

    bulk_index_files_in_opensearch(
        documents,
        open_search_host_url,
        open_search_http_auth,
    )

    mock_open_search.assert_called_once_with(
        open_search_host_url,
        http_auth=open_search_http_auth,
        use_ssl=True,
        verify_certs=True,
        ca_certs=None,
        connection_class=RequestsHttpConnection,
    )
    mock_open_search.return_value.bulk.assert_called_once_with(
        index="documents",
        body='{"index": {"_index": "documents", "_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f"}}\n{"file_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f", "file_name": "path0", "file_reference": "ZD8MCK", "file_path": "data/E2E_tests/original/path0", "citeable_reference": "MOCK1 123/ZD8MCK", "series_id": "8bd7ad22-90d1-4c7f-ae00-645dfd1987cc", "series_name": "MOCK1 123", "transferring_body": "Mock 1 Department", "transferring_body_id": "8ccc8cd1-c0ee-431d-afad-70cf404ba337", "transferring_body_description": "Mock 1 Department", "consignment_id": "2fd4e03e-5913-4c04-b4f2-5a823fafd430", "consignment_reference": "TDR-2024-KKX4", "file_type": "File", "file_size": "1024", "rights_copyright": "Crown Copyright", "legal_status": "Public Record(s)", "held_by": "The National Archives, Kew", "date_last_modified": "2024-03-05T15:05:31", "closure_type": "Open", "title_closed": "false", "description_closed": "false", "language": "English", "content": "", "text_extraction_status": "n/a"}\n{"index": {"_index": "documents", "_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f"}}\n{"file_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f", "file_name": "path2", "file_reference": "ZD8MCN", "file_path": "data/E2E_tests/original/path2", "citeable_reference": "MOCK1 123/ZD8MCN", "series_id": "8bd7ad22-90d1-4c7f-ae00-645dfd1987cc", "series_name": "MOCK1 123", "transferring_body": "Mock 1 Department", "transferring_body_id": "8ccc8cd1-c0ee-431d-afad-70cf404ba337", "transferring_body_description": "Mock 1 Department", "consignment_id": "2fd4e03e-5913-4c04-b4f2-5a823fafd430", "consignment_reference": "TDR-2024-KKX4", "file_type": "File", "file_size": "1024", "rights_copyright": "Crown Copyright", "legal_status": "Public Record(s)", "held_by": "The National Archives, Kew", "date_last_modified": "2024-03-05T15:05:31", "closure_type": "Open", "title_closed": "false", "description_closed": "false", "language": "English", "content": "", "text_extraction_status": "n/a"}\n{"index": {"_index": "documents", "_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270"}}\n{"file_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270", "file_name": "path1", "file_reference": "ZD8MCL", "file_path": "data/E2E_tests/original/path1", "citeable_reference": "MOCK1 123/ZD8MCL", "series_id": "8bd7ad22-90d1-4c7f-ae00-645dfd1987cc", "series_name": "MOCK1 123", "transferring_body": "Mock 1 Department", "transferring_body_id": "8ccc8cd1-c0ee-431d-afad-70cf404ba337", "transferring_body_description": "Mock 1 Department", "consignment_id": "2fd4e03e-5913-4c04-b4f2-5a823fafd430", "consignment_reference": "TDR-2024-KKX4", "file_type": "File", "file_size": "1024", "rights_copyright": "Crown Copyright", "legal_status": "Public Record(s)", "held_by": "The National Archives, Kew", "date_last_modified": "2024-03-05T15:05:31", "closure_type": "Open", "title_closed": "false", "description_closed": "false", "language": "English", "content": "", "text_extraction_status": "n/a"}\n',  # noqa: E501
        timeout=60,
    )
