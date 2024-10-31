from unittest.mock import MagicMock, patch

import pytest
from opensearchpy import OpenSearch

from app.main.util.search_utils import (
    build_dsl_search_query,
    build_search_results_summary_query,
    build_search_transferring_body_query,
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

expected_base_dsl_search_query = {
    "query": {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": "test_query",
                        "fields": ["field_1"],
                        "fuzziness": "AUTO",
                        "lenient": True,
                    }
                }
            ],
            "filter": [{"clause_1": "test_2"}],
        }
    },
    "sort": {"sort_1": "test_1"},
    "_source": {"exclude": ["*.keyword"]},
}


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


@pytest.mark.parametrize(
    "form_data, args_data, form_param, args_param, expected_form_param, expected_args_param",
    [
        # case where both form and args contain the parameters
        (
            {"param_form": "test_form_value"},
            {"param_args": "test_arg_value"},
            "param_form",
            "param_args",
            "test_form_value",
            "test_arg_value",
        ),
        # case where only form contains the parameter, args is empty
        (
            {"param_form": "test_form_only"},
            {},
            "param_form",
            "param_args",
            "test_form_only",
            "",
        ),
        # case where only args contains the parameter, form is empty
        (
            {},
            {"param_args": "test_arg_only"},
            "param_form",
            "param_args",
            "",
            "test_arg_only",
        ),
        # case where form has an empty value, args has the parameter with value
        (
            {"param_form": ""},
            {"param_args": "test_arg_value"},
            "param_form",
            "param_args",
            "",
            "test_arg_value",
        ),
        # case where args has an empty value, form has the parameter with value
        (
            {"param_form": "test_form_value"},
            {"param_args": ""},
            "param_form",
            "param_args",
            "test_form_value",
            "",
        ),
        # case where both form and args contain the parameter with different values, form should take precedence
        (
            {"param_mixed": "form_precedence"},
            {"param_mixed": "args_value"},
            "param_mixed",
            "param_mixed",
            "form_precedence",
            "form_precedence",
        ),
        # case where neither form nor args contains the parameter
        ({}, {}, "param_missing", "param_missing", "", ""),
        # case where parameter is None, should return empty regardless of form or args
        (
            {"param_form": "some_value"},
            {"param_args": "some_value"},
            None,
            None,
            "",
            "",
        ),
    ],
)
def test_get_param(
    form_data,
    args_data,
    form_param,
    args_param,
    expected_form_param,
    expected_args_param,
):
    # request is an object with attributes and not just a dict
    request = MagicMock()
    request.form = form_data
    request.args = args_data
    assert get_param(form_param, request) == expected_form_param
    assert get_param(args_param, request) == expected_args_param


@pytest.mark.parametrize(
    "form_data, args_data, expected_query, expected_search_area",
    [
        # case where both query and search_area are in form
        (
            {"query": "test_query_form", "search_area": "test_area_form"},
            {},
            "test_query_form",
            "test_area_form",
        ),
        # case where both query and search_area are in args
        (
            {},
            {"query": "test_query_args", "search_area": "test_area_args"},
            "test_query_args",
            "test_area_args",
        ),
    ],
)
def test_get_query_and_search_area(
    form_data, args_data, expected_query, expected_search_area
):
    request = MagicMock()
    request.form = form_data
    request.args = args_data
    query, search_area = get_query_and_search_area(request)
    assert query == expected_query
    assert search_area == expected_search_area


def test_setup_opensearch(app):
    app.config["OPEN_SEARCH_HOST"] = "localhost"
    app.config["OPEN_SEARCH_HTTP_AUTH"] = ("test_user", "test_pass")
    app.config["OPEN_SEARCH_CA_CERTS"] = "test/path/to/certs"
    client = setup_opensearch()
    assert isinstance(client, OpenSearch)
    assert client.transport.hosts == [{"host": "localhost"}]
    assert client.transport.kwargs.get("http_auth") == (
        "test_user",
        "test_pass",
    )
    assert client.transport.kwargs.get("ca_certs") == "test/path/to/certs"


@patch("app.main.util.search_utils.OpenSearch")
def test_execute_search(mock_open_search, app):
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


def test_build_dsl_search_query():
    dsl_query = build_dsl_search_query(
        "test_query",
        ["field_1"],
        {"sort_1": "test_1"},
        [{"clause_1": "test_2"}],
    )
    assert dsl_query == expected_base_dsl_search_query


def test_build_search_results_summary_query():
    dsl_query = build_search_results_summary_query(
        "test_query", ["field_1"], {"sort_1": "test_1"}
    )
    assert dsl_query == {
        **expected_base_dsl_search_query,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": "test_query",
                            "fields": ["field_1"],
                            "fuzziness": "AUTO",
                            "lenient": True,
                        }
                    }
                ],
                "filter": [],
            }
        },
        "aggs": {
            "aggregate_by_transferring_body": {
                "terms": {"field": "transferring_body_id.keyword"},
                "aggs": {
                    "top_transferring_body_hits": {
                        "top_hits": {
                            "size": 1,
                            "_source": ["transferring_body"],
                        }
                    }
                },
            }
        },
    }


def test_build_search_transferring_body_query():
    transferring_body_id = "test_transferring_body_id"
    dsl_query = build_search_transferring_body_query(
        "test_query", ["field_1"], {"sort_1": "test_1"}, transferring_body_id
    )
    assert dsl_query == {
        **expected_base_dsl_search_query,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": "test_query",
                            "fields": ["field_1"],
                            "fuzziness": "AUTO",
                            "lenient": True,
                        }
                    }
                ],
                "filter": [
                    {
                        "term": {
                            "transferring_body_id.keyword": transferring_body_id
                        }
                    }
                ],
            }
        },
        "highlight": {
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
            "fields": {
                "*": {},
            },
        },
    }
