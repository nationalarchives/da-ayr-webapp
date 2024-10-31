from unittest.mock import patch

import pytest
from opensearchpy import OpenSearch

from app.main.util.search_utils import (
    build_dsl_query,
    build_query_multi_match,
    build_query_source_rules,
    execute_search,
    format_opensearch_results,
    get_all_fields_excluding,
    get_filtered_list,
    get_open_search_fields_to_search_on,
    get_pagination_info,
    get_param,
    get_query_and_search_area,
    setup_opensearch,
)


@pytest.mark.parametrize(
    "results, expected",
    [
        # typical case with one date in correct format
        (
            [{"_source": {"event_date": "2024-10-30T13:45:30"}}],
            [{"_source": {"event_date": "30/10/2024"}}],
        ),
        # multiple dates in the correct format
        (
            [
                {
                    "_source": {
                        "event_date": "2024-10-30T13:45:30",
                        "creation_date": "2023-08-20T07:15:00",
                    }
                }
            ],
            [
                {
                    "_source": {
                        "event_date": "30/10/2024",
                        "creation_date": "20/08/2023",
                    }
                }
            ],
        ),
        # no date field
        (
            [
                {
                    "_source": {
                        "name": "Test Event",
                        "description": "An event description",
                    }
                }
            ],
            [
                {
                    "_source": {
                        "name": "Test Event",
                        "description": "An event description",
                    }
                }
            ],
        ),
        # empty date string
        ([{"_source": {"event_date": ""}}], [{"_source": {"event_date": ""}}]),
        # invalid date format (should return the original string)
        (
            [{"_source": {"event_date": "30-10-2024 13:45"}}],
            [{"_source": {"event_date": "30-10-2024 13:45"}}],
        ),
        # empty results list
        ([], []),
    ],
)
def test_format_opensearch_results(results, expected):
    actual = format_opensearch_results(results)
    assert actual == expected


@pytest.mark.parametrize(
    "search_area, expected_fields",
    [
        # default "all" fields (no specific search area)
        ("all", ["*"]),
        # "metadata" search area
        (
            "metadata",
            ["metadata_field_1", "metadata_field_2", "metadata_field_3"],
        ),
        # "record" search area
        ("record", ["file_name", "file_path", "content"]),
        # empty search_area string (should default to "all" behavior)
        ("", ["*"]),
        # none as search_area (should default to "all" behavior)
        (None, ["*"]),
        # invalid search_area (should default to "all" behavior)
        ("invalid_area", ["*"]),
    ],
)
@patch("app.main.util.search_utils.OpenSearch")
@patch("app.main.util.search_utils.get_all_fields_excluding")
def test_get_open_search_fields_to_search_on(
    mock_get_all_fields_excluding, mock_opensearch, search_area, expected_fields
):
    mock_get_all_fields_excluding.return_value = [
        "metadata_field_1",
        "metadata_field_2",
        "metadata_field_3",
    ]
    actual_fields = get_open_search_fields_to_search_on(
        mock_opensearch, search_area
    )
    assert actual_fields == expected_fields


def test_get_param(app):
    with patch(
        "flask.request.form.get", return_value="test_form_value"
    ) as mock_form_get, patch(
        "flask.request.args.get", return_value="test_arg_value"
    ):

        assert get_param("param") == "test_form_value"

        mock_form_get.return_value = ""
        assert get_param("param") == "test_arg_value"


@patch(
    "app.main.util.search_utils.get_param",
    side_effect=["test_query", "test_area"],
)
def test_get_query_and_search_area(mock_get_param):
    query, search_area = get_query_and_search_area()
    assert query == "test_query"
    assert search_area == "test_area"


def test_setup_opensearch(app):
    app.config["OPEN_SEARCH_HOST"] = "localhost"
    with app.app_context():
        client = setup_opensearch()
        assert isinstance(client, OpenSearch)


@patch("app.main.util.search_utils.OpenSearch")
def test_execute_search(mock_open_search, app):
    with app.app_context():
        dsl_query = {"query": {"match_all": {}}}
        execute_search(mock_open_search, dsl_query, page=1, per_page=10)
        mock_open_search.search.assert_called_once_with(
            {"query": {"match_all": {}}}, from_=0, size=10, timeout=10
        )


@patch("app.main.util.pagination.calculate_total_pages", return_value=10)
@patch("app.main.util.pagination.get_pagination", return_value={"page": 1})
def test_get_pagination_info(mock_calculate_total_pages, mock_get_pagination):
    results = {"hits": {"total": {"value": 100}}}
    total_records, pagination = get_pagination_info(results, 1, 10)
    assert total_records == 100
    assert pagination == {
        "next": 2,
        "pages": [1, 2, "ellipses", 10],
        "previous": None,
    }


@pytest.mark.parametrize(
    "to_filter, filter, expected",
    [
        (["a", "b", "c"], ["b"], ["a", "c"]),
        (["a", "b", "c"], [], ["a", "b", "c"]),
        ([], ["a", "b"], []),
        ([], [], []),
        (["a", "b", "c"], ["a", "b", "c"], []),
        (["a", "b", "c", "d"], ["b", "d"], ["a", "c"]),
        (["a", "b", "c"], ["x", "y", "z"], ["a", "b", "c"]),
        (["a", 1, "b", 2, "c"], ["a", 2], [1, "b", "c"]),
        ([1, 2, 3, "a", "b"], [2, "a"], [1, 3, "b"]),
    ],
)
def test_get_filtered_list(to_filter, filter, expected):
    assert get_filtered_list(to_filter, filter) == expected


@patch("app.main.util.search_utils.OpenSearch")
def test_get_all_fields_excluding(mock_open_search):
    mock_open_search.indices.get_mapping.return_value = {
        "documents": {
            "mappings": {
                "properties": {
                    "field1": {},
                    "field2": {},
                    "field3": {},
                }
            }
        }
    }
    fields = get_all_fields_excluding(mock_open_search, "documents", ["field2"])
    mock_open_search.indices.get_mapping.assert_called_once()
    assert fields == ["field1", "field3"]


@patch(
    "app.main.util.search_utils.get_all_fields_excluding",
    return_value=["fieldA", "fieldB"],
)
def test_build_query_multi_match(mock_get_all_fields_excluding):
    query = "test_query"
    result = build_query_multi_match(
        query, ["fieldA"], transferring_body_id="12345"
    )
    assert result["query"]["bool"]["must"][0]["multi_match"]["query"] == query
    assert (
        "fieldA" in result["query"]["bool"]["must"][0]["multi_match"]["fields"]
    )
    assert (
        result["query"]["bool"]["filter"][0]["term"][
            "transferring_body_id.keyword"
        ]
        == "12345"
    )


def test_build_query_source_rules():
    source_rules = build_query_source_rules()
    assert source_rules == {"_source": {"exclude": ["*.keyword"]}}


@pytest.mark.parametrize(
    "transferring_body_id, expected_keys",
    [
        ("test_id", ["_source", "query", "highlight", "sort"]),
        (None, ["_source", "query", "aggs", "sort"]),
    ],
)
@patch(
    "app.main.util.search_utils.build_query_sorting", return_value={"sort": []}
)
def test_build_dsl_query(
    mock_build_query_sorting, transferring_body_id, expected_keys
):
    query = "test_query"
    dsl_query = build_dsl_query(query, [], transferring_body_id)
    for key in expected_keys:
        assert key in dsl_query
