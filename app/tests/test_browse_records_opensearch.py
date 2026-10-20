from unittest.mock import Mock, patch

import pytest
from bs4 import BeautifulSoup
from werkzeug.exceptions import NotFound

from app.main.util.browse_utils import (
    get_autofill_options_rows_from_opensearch,
    get_transferring_body_options_from_opensearch,
)
from app.main.util.search_utils import build_browse_records_search_query


def _search_response(total=6):
    return {
        "hits": {
            "total": {"value": total, "relation": "eq"},
            "hits": [
                {
                    "_source": {
                        "file_id": "a8514206-0ebb-4762-9022-fee2edce6436",
                        "file_name": "indexed_file.txt",
                        "file_path": "first_body/series/consignment/indexed_file.txt",
                        "closure_type": "Open",
                        "opening_date": "2024-01-02T00:00:00",
                        "date_last_modified": "2024-01-03T00:53:25.593740+00:00",
                        "series_id": "series-id",
                        "series_name": "HO 405",
                        "transferring_body_id": "body-id",
                        "transferring_body": "first_body",
                        "consignment_id": "consignment-id",
                        "consignment_reference": "AYR-2026-KSJ2",
                    }
                }
            ],
        }
    }


def _open_search_client():
    client = Mock()
    client.search.return_value = {
        "aggregations": {
            "browse_transferring_bodies": {"buckets": []},
            "browse_autofill_options": {"buckets": []},
        }
    }
    return client


def test_autofill_options_returns_empty_when_user_has_no_accessible_bodies():
    with patch(
        "app.main.util.browse_utils.execute_search_query"
    ) as execute_search_query:
        options = get_autofill_options_rows_from_opensearch(
            Mock(), [], "HO 405", "AYR-2026-KSJ2"
        )

    assert options == []
    execute_search_query.assert_not_called()


def test_autofill_options_query_applies_access_and_selection_filters():
    response = {
        "aggregations": {
            "browse_autofill_options": {
                "buckets": [],
            }
        }
    }
    with patch(
        "app.main.util.browse_utils.execute_search_query",
        return_value=response,
    ) as execute_search_query:
        options = get_autofill_options_rows_from_opensearch(
            Mock(),
            ["First Body"],
            "HO 405",
            "AYR-2026-KSJ2",
        )

    assert options == []
    query = execute_search_query.call_args.args[1]
    assert query["query"]["bool"]["filter"] == [
        {"terms": {"transferring_body.keyword": ["First Body"]}},
        {
            "term": {
                "series_name.keyword": {
                    "value": "HO 405",
                    "case_insensitive": True,
                }
            }
        },
        {
            "term": {
                "consignment_reference.keyword": {
                    "value": "AYR-2026-KSJ2",
                    "case_insensitive": True,
                }
            }
        },
    ]


def test_browse_query_defaults_to_match_all_and_exact_hit_tracking():
    query = build_browse_records_search_query()

    assert query["query"] == {"match_all": {}}
    assert query["track_total_hits"] is True
    assert "file_id" in query["_source"]
    assert "content" not in query["_source"]
    assert query["sort"][-1] == {"file_id.keyword": {"order": "asc"}}
    assert "end_date" in query["sort"][0]["_script"]["script"]["source"]
    assert (
        "return Long.MIN_VALUE;"
        in query["sort"][0]["_script"]["script"]["source"]
    )
    assert (
        "date_last_modified" in query["sort"][0]["_script"]["script"]["source"]
    )


@pytest.mark.parametrize(
    ("sort_option", "missing_value"),
    [
        ("date_of_record-desc", "Long.MIN_VALUE"),
        ("date_of_record-asc", "Long.MAX_VALUE"),
    ],
)
def test_browse_date_sort_places_missing_dates_last(sort_option, missing_value):
    query = build_browse_records_search_query(sort_option=sort_option)

    script = query["sort"][0]["_script"]["script"]["source"]
    assert f"return {missing_value};" in script


def test_browse_query_builds_indexed_field_filters():
    query = build_browse_records_search_query(
        transferring_body_id="body-id",
        filters={
            "transferring_body": "first_body",
            "series": "HO 405",
            "consignment_reference": "AYR-2026-KSJ2",
            "record_status": "open",
            "date_filter_field": "opening_date",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
        },
        sort_option="file_name-asc",
    )

    filters = query["query"]["bool"]["filter"]
    assert {"term": {"transferring_body_id.keyword": "body-id"}} in filters
    assert {"match_phrase": {"transferring_body": "first_body"}} in filters
    assert {"match_phrase": {"series_name": "HO 405"}} in filters
    assert {
        "match_phrase": {"consignment_reference": "AYR-2026-KSJ2"}
    } in filters
    assert any(
        "closure_type.keyword" in clause.get("terms", {}) for clause in filters
    )
    assert {
        "range": {
            "opening_date": {
                "gte": "2024-01-01",
                "lt": "2025-01-01",
            }
        }
    } in filters
    assert query["sort"][0] == {
        "file_name.keyword": {
            "order": "asc",
            "missing": "_last",
            "unmapped_type": "keyword",
        }
    }


@pytest.mark.parametrize(
    ("date_filter_field", "expected_filter"),
    [
        (
            "date_last_modified",
            {
                "bool": {
                    "should": [
                        {
                            "range": {
                                "end_date": {
                                    "gte": "2024-01-01",
                                    "lt": "2025-01-01",
                                }
                            }
                        },
                        {
                            "bool": {
                                "must_not": [{"exists": {"field": "end_date"}}],
                                "filter": [
                                    {
                                        "range": {
                                            "date_last_modified": {
                                                "gte": "2024-01-01",
                                                "lt": "2025-01-01",
                                            }
                                        }
                                    }
                                ],
                            }
                        },
                    ],
                    "minimum_should_match": 1,
                }
            },
        ),
        (
            "transferred",
            {
                "range": {
                    "end_date": {
                        "gte": "2024-01-01",
                        "lt": "2025-01-01",
                    }
                }
            },
        ),
        (
            "date_of_record",
            {
                "bool": {
                    "should": [
                        {
                            "range": {
                                "end_date": {
                                    "gte": "2024-01-01",
                                    "lt": "2025-01-01",
                                }
                            }
                        },
                        {
                            "bool": {
                                "must_not": [{"exists": {"field": "end_date"}}],
                                "filter": [
                                    {
                                        "range": {
                                            "date_last_modified": {
                                                "gte": "2024-01-01",
                                                "lt": "2025-01-01",
                                            }
                                        }
                                    }
                                ],
                            }
                        },
                    ],
                    "minimum_should_match": 1,
                }
            },
        ),
    ],
)
def test_browse_query_uses_selected_date_filter_field(
    date_filter_field, expected_filter
):
    query = build_browse_records_search_query(
        filters={
            "date_filter_field": date_filter_field,
            "date_from": "2024-01-01",
            "date_to": "2024-12-31",
        }
    )

    assert expected_filter in query["query"]["bool"]["filter"]


@pytest.mark.parametrize(
    "sort_option",
    ["file_name-sideways", "unknown_field-asc"],
)
def test_browse_query_uses_default_sort_for_invalid_sort_options(sort_option):
    query = build_browse_records_search_query(sort_option=sort_option)
    default_sort = build_browse_records_search_query()["sort"]

    assert query["sort"] == default_sort


def test_transferring_body_options_fetch_all_composite_pages(monkeypatch):
    first_page = {
        "aggregations": {
            "browse_transferring_bodies": {
                "buckets": [
                    {"key": {"transferring_body": "First Body"}},
                ],
                "after_key": {"transferring_body": "First Body"},
            }
        }
    }
    second_page = {
        "aggregations": {
            "browse_transferring_bodies": {
                "buckets": [
                    {"key": {"transferring_body": "Second Body"}},
                ],
            }
        }
    }
    execute_query = Mock(side_effect=[first_page, second_page])
    monkeypatch.setattr(
        "app.main.util.browse_utils.execute_search_query",
        execute_query,
    )

    options = get_transferring_body_options_from_opensearch(Mock())

    assert options == ["First Body", "Second Body"]
    second_query = execute_query.call_args_list[1].args[1]
    aggregation = second_query["aggs"]["browse_transferring_bodies"]
    assert aggregation["composite"]["after"] == {
        "transferring_body": "First Body"
    }


def test_browse_renders_and_keeps_navigation_on_browse(
    client, mock_all_access_user
):
    mock_all_access_user(client)
    with (
        patch("app.main.routes.setup_opensearch") as setup_opensearch,
        patch("app.main.routes.execute_search") as execute_search,
    ):
        setup_opensearch.return_value = _open_search_client()
        execute_search.return_value = _search_response()

        response = client.get("/browse")

    assert response.status_code == 200
    assert b"6 records" in response.data
    assert b"indexed_file.txt" in response.data

    _, query, page, per_page = execute_search.call_args.args
    assert query["query"] == {"match_all": {}}
    assert page == 1
    assert per_page == 5
    assert execute_search.call_args.kwargs == {
        "max_results": 10_000,
        "index": "documents",
    }

    soup = BeautifulSoup(response.data, "html.parser")
    rendered_dates = [
        element.get_text(strip=True) for element in soup.select("time")
    ]
    assert "03/01/2024" in rendered_dates
    assert "02/01/2024" in rendered_dates
    assert all("T" not in date for date in rendered_dates)
    consignment_row = soup.select_one(".browse-record-row__row--consignment")
    assert consignment_row is not None
    assert " ".join(consignment_row.get_text(" ", strip=True).split()) == (
        "consignment AYR-2026-KSJ2 on -"
    )
    assert soup.select_one("form[action^='/browse']") is not None
    assert (
        soup.select_one(".govuk-pagination__next a[href^='/browse']")
        is not None
    )
    series_link = soup.find("a", string="HO 405")
    assert series_link is not None
    assert series_link["href"].startswith("/browse?")


def test_browse_redirects_invalid_page_to_browse(client, mock_all_access_user):
    mock_all_access_user(client)
    with (
        patch("app.main.routes.setup_opensearch") as setup_opensearch,
        patch("app.main.routes.execute_search", side_effect=NotFound()),
    ):
        setup_opensearch.return_value = _open_search_client()

        response = client.get("/browse?page=99")

    assert response.status_code == 302
    assert response.location.startswith("/browse")


@pytest.mark.parametrize(
    ("per_page", "page", "expected_summary", "has_next_page"),
    [
        (5, 5, "Showing 21–25 of 10,000", True),
        (5, 2000, "Showing 9996–10000 of 10,000", False),
        (6, 1667, "Showing 9997–10000 of 10,000", False),
        (10, 1000, "Showing 9991–10000 of 10,000", False),
        (20, 500, "Showing 9981–10000 of 10,000", False),
    ],
)
def test_browse_caps_pagination_at_10000_results(
    client,
    mock_all_access_user,
    per_page,
    page,
    expected_summary,
    has_next_page,
):
    mock_all_access_user(client)
    with (
        patch("app.main.routes.setup_opensearch") as setup_opensearch,
        patch("app.main.routes.execute_search") as execute_search,
    ):
        setup_opensearch.return_value = _open_search_client()
        execute_search.return_value = _search_response(total=1_144_224)

        response = client.get(f"/browse?page={page}&per_page={per_page}")

    assert response.status_code == 200
    assert b"1,144,224 records" in response.data
    soup = BeautifulSoup(response.data, "html.parser")
    summary = soup.select_one(".browse__header-cell")
    assert summary is not None
    assert summary.get_text(" ", strip=True) == expected_summary
    assert (soup.select_one(".govuk-pagination__next") is not None) is (
        has_next_page
    )


def test_browse_redirects_pages_beyond_result_window(
    client, mock_all_access_user
):
    mock_all_access_user(client)
    with (
        patch("app.main.routes.setup_opensearch") as setup_opensearch,
        patch("app.main.routes.execute_search") as execute_search,
    ):
        setup_opensearch.return_value = _open_search_client()

        response = client.get("/browse?page=2001")

    assert response.status_code == 302
    assert response.location.startswith("/browse")
    execute_search.assert_not_called()


def test_browse_does_not_read_index_settings(client, mock_all_access_user):
    mock_all_access_user(client)
    with (
        patch("app.main.routes.setup_opensearch") as setup_opensearch,
        patch("app.main.routes.execute_search") as execute_search,
    ):
        open_search = _open_search_client()
        open_search.indices.get_settings.side_effect = AssertionError(
            "Browsing must not read index settings"
        )
        setup_opensearch.return_value = open_search
        execute_search.return_value = _search_response(total=120_000)

        response = client.get("/browse")

    assert response.status_code == 200
    summary = BeautifulSoup(response.data, "html.parser").select_one(
        ".browse__header-cell"
    )
    assert summary is not None
    assert summary.get_text(" ", strip=True) == "Showing 1–5 of 10,000"
    open_search.indices.get_settings.assert_not_called()
    assert execute_search.call_args.kwargs == {
        "max_results": 10_000,
        "index": "documents",
    }
