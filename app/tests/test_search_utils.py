from unittest.mock import MagicMock, patch

import pytest
from opensearchpy import OpenSearch

from app.main.util.search_utils import (
    build_dsl_search_query,
    build_search_results_summary_query,
    build_search_transferring_body_query,
    execute_search,
    filter_opensearch_highlight_results,
    format_opensearch_results,
    get_all_fields_excluding,
    get_filtered_list,
    get_open_search_fields_to_search_on_and_sorting,
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
    "_source": True,
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
    "search_area, expected_fields, sort",
    [
        (
            "all",
            [
                "metadata_field_1",
                "metadata_field_2",
                "metadata_field_3",
                "file_name^3",
            ],
            "file_name",
        ),
        (
            "metadata",
            [
                "metadata_field_1^100",
                "metadata_field_2^100",
                "metadata_field_3^100",
                "file_name^0.2",
                "content^0.1",
            ],
            "metadata",
        ),
        ("record", ["content", "file_name^3"], "file_name"),
        (
            "all",
            [
                "metadata_field_1",
                "metadata_field_2",
                "metadata_field_3",
                "file_name^3",
            ],
            "file_name",
        ),
        (
            "all",
            [
                "metadata_field_1",
                "metadata_field_2",
                "metadata_field_3",
                "description^3",
                "file_name^2",
            ],
            "description",
        ),
        (
            "all",
            [
                "metadata_field_1",
                "metadata_field_2",
                "metadata_field_3",
                "content^3",
                "file_name^2",
            ],
            "content",
        ),
        (
            "all",
            ["metadata_field_1", "metadata_field_2", "metadata_field_3"],
            "least_matches",
        ),
        (
            "",
            [
                "metadata_field_1",
                "metadata_field_2",
                "metadata_field_3",
                "file_name^3",
            ],
            "file_name",
        ),
        (
            None,
            [
                "metadata_field_1",
                "metadata_field_2",
                "metadata_field_3",
                "file_name^3",
            ],
            "file_name",
        ),
        (
            "invalid_area",
            [
                "metadata_field_1",
                "metadata_field_2",
                "metadata_field_3",
                "file_name^3",
            ],
            "file_name",
        ),
    ],
)
@patch("app.main.util.search_utils.OpenSearch")
@patch("app.main.util.search_utils.get_all_fields_excluding")
def test_get_open_search_fields_to_search_on_and_sorting(
    mock_get_all_fields_excluding,
    mock_opensearch,
    search_area,
    expected_fields,
    sort,
):
    mock_get_all_fields_excluding.return_value = [
        "metadata_field_1",
        "metadata_field_2",
        "metadata_field_3",
    ]
    actual_fields, _ = get_open_search_fields_to_search_on_and_sorting(
        mock_opensearch, search_area, sort
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
        [{"clause_1": "test_2"}],
        {"sort_1": "test_1"},
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
        "test_query",
        ["field_1"],
        transferring_body_id,
        "test_highlight_key",
        {"sort_1": "test_1"},
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
            "pre_tags": ["<test_highlight_key>"],
            "post_tags": ["</test_highlight_key>"],
            "fields": {
                "*": {},
            },
        },
    }


@pytest.mark.parametrize(
    "input_results, expected_output",
    [
        # standard case, one .keyword field with array value
        (
            [
                {
                    "highlight": {
                        "field1.keyword": ["match1"],
                        "field2": ["match2"],
                    }
                }
            ],
            [{"highlight": {"field2": ["match2"]}}],
        ),
        # multiple .keyword fields in a single result
        (
            [
                {
                    "highlight": {
                        "field1.keyword": ["match1"],
                        "field2.keyword": ["match2"],
                        "field3": ["match3"],
                    }
                }
            ],
            [{"highlight": {"field3": ["match3"]}}],
        ),
        # no .keyword fields
        (
            [{"highlight": {"field1": ["match1"], "field2": ["match2"]}}],
            [{"highlight": {"field1": ["match1"], "field2": ["match2"]}}],
        ),
        # empty highlight field
        ([{"highlight": {}}], [{"highlight": {}}]),
        # multiple result entries, mixed content
        (
            [
                {
                    "highlight": {
                        "field1.keyword": ["match1"],
                        "field2": ["match2"],
                    }
                },
                {
                    "highlight": {
                        "field3.keyword": ["match3"],
                        "field4": ["match4"],
                    }
                },
                {"highlight": {"field5": ["match5"]}},
            ],
            [
                {"highlight": {"field2": ["match2"]}},
                {"highlight": {"field4": ["match4"]}},
                {"highlight": {"field5": ["match5"]}},
            ],
        ),
        # no highlight key in results
        (
            [{"title": "Title without highlight"}],
            [{"title": "Title without highlight"}],
        ),
        # empty list input
        ([], []),
        # large input with many .keyword and non-.keyword fields
        (
            [
                {
                    "highlight": {
                        f"field{i}.keyword": [f"match{i}"],
                        f"field{i}": [f"match_non_keyword{i}"],
                    }
                }
                for i in range(100)
            ],
            [
                {"highlight": {f"field{i}": [f"match_non_keyword{i}"]}}
                for i in range(100)
            ],
        ),
    ],
)
def test_filter_opensearch_highlight_results(input_results, expected_output):
    assert filter_opensearch_highlight_results(input_results) == expected_output
