import re
from unittest import mock

import pytest
from opensearch_indexer.index_consignment.bulk_index_consignment import (
    bulk_index_files_in_opensearch,
)
from opensearchpy import RequestsHttpConnection


@mock.patch(
    "opensearch_indexer.index_consignment.bulk_index_consignment.OpenSearch"
)
def test_index_file_content_and_metadata_in_opensearch(
    mock_open_search, caplog
):
    """
    Test the `bulk_index_files_in_opensearch` function for successful indexing.

    Given:
    - A list of document dictionaries containing file IDs and content.
    - Mocked OpenSearch connection details.

    When:
    - `bulk_index_files_in_opensearch` is invoked.

    Then:
    - Documents are indexed in OpenSearch successfully.
    - OpenSearch client is initialized with the correct parameters.
    - Logs confirm the completion of the bulk indexing operation without errors.
    """
    open_search_host_url = "test_open_search_host_url"
    open_search_http_auth = mock.Mock()

    documents = [
        {
            "file_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
            "document": {
                "a": "foo1",
                "b": "bar1",
            },
        },
        {
            "file_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f",
            "document": {
                "c": "foo2",
                "d": "bar2",
            },
        },
        {
            "file_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270",
            "document": {
                "e": "foo3",
                "f": "bar3",
            },
        },
    ]

    mock_opensearch_response = {
        "took": 203,
        "errors": False,
        "items": [
            {
                "index": {
                    "_index": "documents",
                    "_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
                    "_version": 26,
                    "result": "updated",
                    "_shards": {"total": 2, "successful": 1, "failed": 0},
                    "_seq_no": 420,
                    "status": 200,
                }
            },
            {
                "index": {
                    "_index": "documents",
                    "_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f",
                    "_version": 26,
                    "result": "updated",
                    "_shards": {"total": 2, "successful": 1, "failed": 0},
                    "_seq_no": 421,
                    "_primary_term": 8,
                    "status": 200,
                }
            },
            {
                "index": {
                    "_index": "documents",
                    "_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270",
                    "_version": 26,
                    "result": "updated",
                    "_shards": {"total": 2, "successful": 1, "failed": 0},
                    "_seq_no": 422,
                    "_primary_term": 8,
                    "status": 200,
                }
            },
        ],
    }
    mock_open_search.return_value.bulk.return_value = mock_opensearch_response

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
        body=(
            '{"index": {"_index": "documents", "_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f"}}\n'
            '{"a": "foo1", "b": "bar1"}\n'
            '{"index": {"_index": "documents", "_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f"}}\n'
            '{"c": "foo2", "d": "bar2"}\n'
            '{"index": {"_index": "documents", "_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270"}}\n'
            '{"e": "foo3", "f": "bar3"}\n'
        ),
        timeout=60,
    )

    assert [rec.message for rec in caplog.records] == [
        "Opensearch bulk indexing call completed with response",
        str(mock_opensearch_response),
        "Opensearch bulk indexing completed successfully",
    ]


@mock.patch(
    "opensearch_indexer.index_consignment.bulk_index_consignment.OpenSearch"
)
def test_index_file_content_and_metadata_in_opensearch_with_document_indexing_errors(
    mock_open_search, caplog
):
    """
    Test the `bulk_index_files_in_opensearch` function for error handling during indexing.

    Given:
    - A list of document dictionaries containing file IDs and content.
    - Mocked OpenSearch connection details.

    When:
    - `bulk_index_files_in_opensearch` is invoked, and OpenSearch returns errors for some documents.

    Then:
    - An exception is raised for the failed documents.
    - OpenSearch client is initialized with the correct parameters.
    - Logs indicate the presence of errors in the indexing operation.
    """
    open_search_host_url = "test_open_search_host_url"
    open_search_http_auth = mock.Mock()

    documents = [
        {
            "file_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
            "document": {
                "a": "foo1",
                "b": "bar1",
            },
        },
        {
            "file_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f",
            "document": {
                "c": "foo2",
                "d": "bar2",
            },
        },
        {
            "file_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270",
            "document": {
                "e": "foo3",
                "f": "bar3",
            },
        },
    ]

    mock_opensearch_response = {
        "took": 203,
        "errors": True,
        "items": [
            {
                "index": {
                    "_index": "documents",
                    "_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
                    "_version": 26,
                    "result": "updated",
                    "_shards": {"total": 2, "successful": 1, "failed": 1},
                    "_seq_no": 420,
                    "status": 200,
                }
            },
            {
                "index": {
                    "_index": "documents",
                    "_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f",
                    "_version": 26,
                    "result": "updated",
                    "_shards": {"total": 2, "successful": 1, "failed": 0},
                    "_seq_no": 421,
                    "_primary_term": 8,
                    "status": 200,
                }
            },
            {
                "index": {
                    "_index": "documents",
                    "_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270",
                    "error": {
                        "type": "document_missing_exception",
                        "reason": "[_doc][tt0816711]: document missing",
                        "index": "documents",
                        "shard": "0",
                        "index_uuid": "yhizhusbSWmP0G7OJnmcLg",
                    },
                    "status": 404,
                }
            },
        ],
    }

    mock_open_search.return_value.bulk.return_value = mock_opensearch_response

    with pytest.raises(
        Exception,
        match=re.escape(
            (
                "Opensearch bulk indexing errors:\n"
                "Error for document ID 47526ba9-88e5-4cc8-8bc1-d682a10fa270: "
                "{'type': 'document_missing_exception', 'reason': '[_doc][tt0816711]: document missing', "
                "'index': 'documents', 'shard': '0', 'index_uuid': 'yhizhusbSWmP0G7OJnmcLg'}"
            )
        ),
    ):
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
        body=(
            '{"index": {"_index": "documents", "_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f"}}\n'
            '{"a": "foo1", "b": "bar1"}\n'
            '{"index": {"_index": "documents", "_id": "a948a34f-6ba0-4ff2-bef6-a290aec31d3f"}}\n'
            '{"c": "foo2", "d": "bar2"}\n'
            '{"index": {"_index": "documents", "_id": "47526ba9-88e5-4cc8-8bc1-d682a10fa270"}}\n'
            '{"e": "foo3", "f": "bar3"}\n'
        ),
        timeout=60,
    )

    assert [rec.message for rec in caplog.records] == [
        "Opensearch bulk indexing call completed with response",
        str(mock_opensearch_response),
        "Opensearch bulk indexing completed with errors",
    ]


@mock.patch(
    "opensearch_indexer.index_consignment.bulk_index_consignment.OpenSearch"
)
def test_index_file_content_and_metadata_in_opensearch_with_bulk_api_exception(
    mock_open_search, caplog
):
    """
    Test the `bulk_index_files_in_opensearch` function for handling exceptions raised by the OpenSearch bulk API.

    Given:
    - A list of document dictionaries containing file IDs and content.
    - Mocked OpenSearch connection details.

    When:
    - `bulk_index_files_in_opensearch` is invoked, and the OpenSearch bulk API raises an exception.

    Then:
    - The exception is propagated as expected.
    - Logs capture the error details.
    """
    open_search_host_url = "test_open_search_host_url"
    open_search_http_auth = mock.Mock()

    documents = [
        {
            "file_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f",
            "document": {"a": "foo1", "b": "bar1"},
        }
    ]

    mock_open_search.return_value.bulk.side_effect = Exception(
        "Simulated OpenSearch bulk API failure"
    )

    with pytest.raises(
        Exception, match="Simulated OpenSearch bulk API failure"
    ):
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
        body=(
            '{"index": {"_index": "documents", "_id": "8ffacc5a-443a-4568-a5c9-c9741955b40f"}}\n'
            '{"a": "foo1", "b": "bar1"}\n'
        ),
        timeout=60,
    )

    assert [rec.message for rec in caplog.records] == [
        "Opensearch bulk indexing call failed: Simulated OpenSearch bulk API failure"
    ]
