import os
from uuid import uuid4

import pytest
from flask import Flask
from opensearchpy import OpenSearch
from werkzeug.exceptions import NotFound

from app.main.util.browse_utils import (
    autofill_selected_filters,
    get_autofill_options_rows_from_opensearch,
    get_transferring_body_options_from_opensearch,
)
from app.main.util.search_utils import (
    build_browse_records_search_query,
    execute_search,
)


def _text_with_keyword():
    return {
        "type": "text",
        "fields": {"keyword": {"type": "keyword"}},
    }


@pytest.fixture
def browse_index():
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

    index = f"browse-records-integration-{uuid4().hex}"
    client.indices.create(
        index=index,
        body={
            "settings": {"index": {"max_result_window": 20}},
            "mappings": {
                "properties": {
                    "file_id": _text_with_keyword(),
                    "file_name": _text_with_keyword(),
                    "file_path": {"type": "keyword"},
                    "closure_type": _text_with_keyword(),
                    "opening_date": {"type": "date"},
                    "end_date": {"type": "date"},
                    "date_last_modified": {"type": "date"},
                    "series_id": {"type": "keyword"},
                    "series_name": _text_with_keyword(),
                    "transferring_body_id": _text_with_keyword(),
                    "transferring_body": _text_with_keyword(),
                    "consignment_id": {"type": "keyword"},
                    "consignment_reference": _text_with_keyword(),
                    "consignment_transfer_complete_date": {"type": "date"},
                }
            },
        },
    )

    documents = [
        {
            "file_id": "file-a",
            "file_name": "alpha.txt",
            "transferring_body_id": "body-one",
            "transferring_body": "First Body",
            "series_id": "series-one",
            "series_name": "HO 405",
            "consignment_id": "consignment-one",
            "consignment_reference": "AYR-2026-KSJ2",
            "consignment_transfer_complete_date": "2024-02-03",
            "file_path": "/data/alpha.txt",
            "closure_type": "Open",
            "opening_date": "2024-03-10",
            "end_date": "2024-05-10",
            "date_last_modified": "2024-06-20",
        },
        {
            "file_id": "file-b",
            "file_name": "bravo.txt",
            "transferring_body_id": "body-one",
            "transferring_body": "First Body",
            "series_id": "series-one",
            "series_name": "HO 405",
            "consignment_id": "consignment-one",
            "consignment_reference": "AYR-2026-KSJ2",
            "consignment_transfer_complete_date": "2024-02-03",
            "file_path": "/data/bravo.txt",
            "closure_type": "Open",
            "opening_date": "2024-11-15",
            "date_last_modified": "2024-03-01",
        },
        {
            "file_id": "file-c",
            "file_name": "charlie.txt",
            "transferring_body_id": "body-one",
            "transferring_body": "First Body",
            "series_id": "series-two",
            "series_name": "HO 406",
            "consignment_id": "consignment-two",
            "consignment_reference": "AYR-2026-OTHER",
            "consignment_transfer_complete_date": "2023-02-03",
            "file_path": "/data/charlie.txt",
            "closure_type": "Closed",
            "opening_date": "2023-01-01",
            "end_date": "2020-01-01",
        },
        {
            "file_id": "file-d",
            "file_name": "delta.txt",
            "transferring_body_id": "body-two",
            "transferring_body": "Second Body",
            "series_id": "series-three",
            "series_name": "HO 407",
            "consignment_id": "consignment-three",
            "consignment_reference": "AYR-2026-THIRD",
            "consignment_transfer_complete_date": "2022-02-03",
            "file_path": "/data/delta.txt",
            "closure_type": "Open",
            "opening_date": "2022-01-01",
        },
    ]

    try:
        for document in documents:
            client.index(
                index=index,
                id=document["file_id"],
                body=document,
            )
        client.indices.refresh(index=index)
        yield client, index
    finally:
        if client.indices.exists(index=index):
            client.indices.delete(index=index)


def _file_ids(response):
    return [hit["_source"]["file_id"] for hit in response["hits"]["hits"]]


def test_browse_filter_options_and_autofill_use_indexed_documents(browse_index):
    client, index = browse_index
    app = Flask(__name__)
    app.config["OPEN_SEARCH_TIMEOUT"] = 10

    with app.app_context():
        transferring_bodies = get_transferring_body_options_from_opensearch(
            client,
            index=index,
        )
        autofill_rows = get_autofill_options_rows_from_opensearch(
            client,
            accessible_body_names=None,
            selected_series="ho 405",
            selected_consignment="",
            index=index,
        )
        selected_body, selected_series = autofill_selected_filters(
            "",
            "ho 405",
            "",
            autofill_rows,
        )
        body_scoped_rows = get_autofill_options_rows_from_opensearch(
            client,
            accessible_body_names=["Second Body"],
            selected_series="ho 405",
            selected_consignment="",
            index=index,
        )

    assert transferring_bodies == ["First Body", "Second Body"]
    assert (selected_body, selected_series) == ("First Body", "ho 405")
    assert body_scoped_rows == []


def test_browse_query_filters_match_indexed_documents(browse_index):
    client, index = browse_index
    query = build_browse_records_search_query(
        transferring_body_id="body-one",
        filters={
            "transferring_body": "first body",
            "series": "ho 405",
            "consignment_reference": "ayr-2026-ksj2",
            "record_status": "open",
            "date_filter_field": "opening_date",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
        },
        sort_option="file_name-asc",
    )

    response = client.search(index=index, body=query)

    assert _file_ids(response) == ["file-a", "file-b"]

    partial_reference_query = build_browse_records_search_query(
        filters={"consignment_reference": "AYR-2026-KSJ"}
    )
    response = client.search(index=index, body=partial_reference_query)
    assert response["hits"]["total"]["value"] == 0


def test_browse_date_filter_includes_timestamps_through_selected_end_date(
    browse_index,
):
    client, index = browse_index
    for file_id, opening_date in (
        ("last-moment", "2024-12-31T23:59:59.999Z"),
        ("next-day", "2025-01-01T00:00:00Z"),
    ):
        client.index(
            index=index,
            id=file_id,
            body={"file_id": file_id, "opening_date": opening_date},
        )
    client.indices.refresh(index=index)

    query = build_browse_records_search_query(
        filters={
            "date_filter_field": "opening_date",
            "date_from": "2024-12-31",
            "date_to": "2024-12-31",
        }
    )
    response = client.search(index=index, body=query)

    assert "last-moment" in _file_ids(response)
    assert "next-day" not in _file_ids(response)


@pytest.mark.parametrize(
    ("sort_option", "expected_ids"),
    [
        (
            "date_of_record-desc",
            ["file-a", "file-b", "file-c", "file-d"],
        ),
        (
            "date_of_record-asc",
            ["file-c", "file-b", "file-a", "file-d"],
        ),
    ],
)
def test_browse_date_sort_places_undated_documents_last(
    browse_index, sort_option, expected_ids
):
    client, index = browse_index
    query = build_browse_records_search_query(sort_option=sort_option)

    response = client.search(index=index, body=query)

    assert _file_ids(response) == expected_ids


def test_execute_search_paginates_and_respects_result_window(browse_index):
    client, index = browse_index
    app = Flask(__name__)
    app.config["OPEN_SEARCH_TIMEOUT"] = 10
    query = build_browse_records_search_query(sort_option="file_name-asc")

    with app.app_context():
        response = execute_search(
            client,
            query,
            page=2,
            per_page=2,
            max_results=3,
            index=index,
        )
        with pytest.raises(NotFound):
            execute_search(
                client,
                query,
                page=3,
                per_page=2,
                max_results=3,
                index=index,
            )

    assert _file_ids(response) == ["file-c"]
