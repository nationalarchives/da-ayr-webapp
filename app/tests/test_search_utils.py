from unittest.mock import patch

import pytest

from app.main.util.search_utils import (
    build_dsl_query,
    execute_search,
    get_all_fields_excluding,
    get_filtered_list,
    get_pagination_info,
    get_param,
    get_query_and_search_area,
    get_query_multi_match,
    get_query_source_rules,
    setup_opensearch,
)
from app.tests.test_search import MockOpenSearch


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


@patch("app.main.util.search_utils.OpenSearch", MockOpenSearch)
def test_setup_opensearch(app):
    with app.app_context():
        client = setup_opensearch()
        assert isinstance(client, MockOpenSearch)


@patch("app.main.util.search_utils.OpenSearch")
def test_execute_search(mock_open_search, app):
    with app.app_context():
        dsl_query = {"query": {"match_all": {}}}
        execute_search(mock_open_search, dsl_query, page=1, per_page=10)
        mock_open_search.search.assert_called_once()


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
def test_get_query_multi_match(mock_get_all_fields_excluding):
    query = "test_query"
    search_area = "metadata"
    result = get_query_multi_match(
        query, search_area, MockOpenSearch(), _id="12345"
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


def test_get_query_source_rules():
    source_rules = get_query_source_rules()
    assert source_rules == {"_source": {"exclude": ["*.keyword"]}}


@patch(
    "app.main.util.search_utils.get_query_source_rules",
    return_value={"_source": {"exclude": ["*.keyword"]}},
)
@patch(
    "app.main.util.search_utils.get_query_multi_match",
    return_value={"query": {"bool": {}}},
)
@patch(
    "app.main.util.search_utils.get_query_aggregations",
    return_value={"aggs": {}},
)
@patch(
    "app.main.util.search_utils.get_query_highlighting",
    return_value={"highlight": {}},
)
@patch(
    "app.main.util.search_utils.get_query_sorting", return_value={"sort": []}
)
def test_build_dsl_query(
    mock_get_query_source_rules,
    mock_get_query_multi_match,
    mock_get_query_aggregations,
    mock_get_query_highlighting,
    mock_get_query_sorting,
):
    query = "test_query"
    search_area = "metadata"
    dsl_query = build_dsl_query(query, search_area, MockOpenSearch(), _id=None)
    assert "_source" in dsl_query
    assert "query" in dsl_query
    assert "aggs" in dsl_query
    assert "highlight" in dsl_query
    assert "sort" in dsl_query
