from unittest.mock import patch

from bs4 import BeautifulSoup
from werkzeug.exceptions import NotFound

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


def test_browse_query_defaults_to_match_all_and_exact_hit_tracking():
    query = build_browse_records_search_query()

    assert query["query"] == {"match_all": {}}
    assert query["track_total_hits"] is True
    assert "file_id" in query["_source"]
    assert "content" not in query["_source"]
    assert query["sort"][-1] == {"file_id.keyword": {"order": "asc"}}
    assert "end_date" in query["sort"][0]["_script"]["script"]["source"]
    assert "Long.MAX_VALUE" in query["sort"][0]["_script"]["script"]["source"]
    assert (
        "date_last_modified" in query["sort"][0]["_script"]["script"]["source"]
    )


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
    assert {
        "term": {
            "transferring_body.keyword": {
                "value": "first_body",
                "case_insensitive": True,
            }
        }
    } in filters
    assert {
        "term": {
            "series_name.keyword": {
                "value": "HO 405",
                "case_insensitive": True,
            }
        }
    } in filters
    assert {
        "term": {
            "consignment_reference.keyword": {
                "value": "AYR-2026-KSJ2",
                "case_insensitive": True,
            }
        }
    } in filters
    assert any(
        "closure_type.keyword" in clause.get("terms", {}) for clause in filters
    )
    assert {
        "range": {
            "opening_date": {
                "gte": "2024-01-01",
                "lte": "2024-12-31",
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


def test_browse_records_opensearch_renders_and_keeps_navigation_on_test_route(
    client, mock_all_access_user
):
    mock_all_access_user(client)
    with (
        patch("app.main.routes.setup_opensearch") as setup_opensearch,
        patch("app.main.routes.execute_search") as execute_search,
        patch(
            "app.main.routes.build_browse_records_query_factory"
        ) as sql_query_factory,
    ):
        setup_opensearch.return_value = object()
        execute_search.return_value = _search_response()

        response = client.get("/browse/records-opensearch")

    assert response.status_code == 200
    assert b"6 records" in response.data
    assert b"indexed_file.txt" in response.data
    sql_query_factory.assert_not_called()

    _, query, page, per_page = execute_search.call_args.args
    assert query["query"] == {"match_all": {}}
    assert page == 1
    assert per_page == 5

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
    assert (
        soup.select_one("form[action^='/browse/records-opensearch']")
        is not None
    )
    assert (
        soup.select_one(
            ".govuk-pagination__next a[href^='/browse/records-opensearch']"
        )
        is not None
    )
    series_link = soup.find("a", string="HO 405")
    assert series_link is not None
    assert series_link["href"].startswith("/browse/records-opensearch?")


def test_browse_records_opensearch_scopes_standard_user_by_body_id(
    client, mock_standard_user, browse_files
):
    body = browse_files[0].consignment.series.body
    mock_standard_user(client, body.Name)
    with (
        patch("app.main.routes.setup_opensearch") as setup_opensearch,
        patch("app.main.routes.execute_search") as execute_search,
    ):
        setup_opensearch.return_value = object()
        execute_search.return_value = _search_response()

        response = client.get("/browse/records-opensearch")

    assert response.status_code == 200
    _, query, _, _ = execute_search.call_args.args
    assert {
        "term": {"transferring_body_id.keyword": str(body.BodyId)}
    } in query["query"]["bool"]["filter"]


def test_browse_records_opensearch_redirects_invalid_page_to_same_endpoint(
    client, mock_all_access_user
):
    mock_all_access_user(client)
    with (
        patch("app.main.routes.setup_opensearch") as setup_opensearch,
        patch("app.main.routes.execute_search", side_effect=NotFound()),
    ):
        setup_opensearch.return_value = object()

        response = client.get("/browse/records-opensearch?page=99")

    assert response.status_code == 302
    assert response.location.startswith("/browse/records-opensearch")
