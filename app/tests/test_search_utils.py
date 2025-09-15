from unittest.mock import patch

import pytest
from opensearchpy import OpenSearch

from app.main.util.search_utils import (
    OPENSEARCH_FIELD_NAME_MAP,
    build_dsl_search_query,
    build_search_results_summary_query,
    build_search_transferring_body_query,
    execute_search,
    extract_search_terms,
    filter_opensearch_highlight_results,
    format_opensearch_results,
    get_all_fields_excluding,
    get_filtered_list,
    get_open_search_fields_to_search_on_and_sorting,
    get_pagination_info,
    rearrange_opensearch_results_for_relevant_fields,
    reorder_fields,
    setup_opensearch,
)

fields_all = [
    "file_name^1",
    "description^1",
    "transferring_body^1",
    "foi_exemption_code^1",
    "content^1",
    "closure_start_date^1",
    "end_date^1",
    "date_last_modified^1",
    "citeable_reference^1",
    "series_name^1",
    "transferring_body_description^1",
    "consignment_reference^1",
]

fields_metadata = [
    "description^1",
    "transferring_body^1",
    "foi_exemption_code^1",
    "closure_start_date^1",
    "end_date^1",
    "date_last_modified^1",
    "citeable_reference^1",
    "series_name^1",
    "transferring_body_description^1",
    "consignment_reference^1",
]

fields_without_file_name = [
    "description^1",
    "transferring_body^1",
    "foi_exemption_code^1",
    "content^1",
    "closure_start_date^1",
    "end_date^1",
    "date_last_modified^1",
    "citeable_reference^1",
    "series_name^1",
    "transferring_body_description^1",
    "consignment_reference^1",
]

expected_base_dsl_search_query = {
    "query": {
        "bool": {
            "should": [
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
    "sort": {"sort": "foobar"},
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
    "search_area, expected_fields, sort, expected_sorting",
    [
        (
            "all",
            [
                "file_name^3",
                *fields_without_file_name,
            ],
            "file_name",
            [{"_score": {"order": "desc"}}],
        ),
        (
            "metadata",
            [
                "description^1",
                "transferring_body^1",
                "foi_exemption_code^1",
                "closure_start_date^1",
                "end_date^1",
                "date_last_modified^1",
                "citeable_reference^1",
                "series_name^1",
                "transferring_body_description^1",
                "consignment_reference^1",
            ],
            "metadata",
            [{"_score": {"order": "desc"}}],
        ),
        (
            "record",
            ["file_name^3", "content^1"],
            "file_name",
            [{"_score": {"order": "desc"}}],
        ),
        (
            "all",
            [
                "file_name^3",
                *fields_without_file_name,
            ],
            "file_name",
            [{"_score": {"order": "desc"}}],
        ),
        (
            "all",
            [
                "file_name^2",
                "description^3",
                "transferring_body^1",
                "foi_exemption_code^1",
                "content^1",
                "closure_start_date^1",
                "end_date^1",
                "date_last_modified^1",
                "citeable_reference^1",
                "series_name^1",
                "transferring_body_description^1",
                "consignment_reference^1",
            ],
            "description",
            [{"_score": {"order": "desc"}}],
        ),
        (
            "all",
            [
                "file_name^1",
                "description^1",
                "transferring_body^1",
                "foi_exemption_code^1",
                "content^1",
                "closure_start_date^1",
                "end_date^1",
                "date_last_modified^1",
                "citeable_reference^1",
                "series_name^1",
                "transferring_body_description^1",
                "consignment_reference^1",
            ],
            "content",
            [{"_score": {"order": "desc"}}],
        ),
        (
            "all",
            fields_all,
            "least_matches",
            [{"_score": {"order": "asc"}}],
        ),
        (
            "",
            [
                "file_name^3",
                *fields_without_file_name,
            ],
            "file_name",
            [{"_score": {"order": "desc"}}],
        ),
        (
            None,
            [
                "file_name^3",
                *fields_without_file_name,
            ],
            "file_name",
            [{"_score": {"order": "desc"}}],
        ),
        (
            "invalid_area",
            ["file_name^3", *fields_without_file_name],
            "file_name",
            [{"_score": {"order": "desc"}}],
        ),
    ],
)
def test_get_open_search_fields_to_search_on_and_sorting(
    search_area, expected_fields, sort, expected_sorting
):
    actual_fields, sorting = get_open_search_fields_to_search_on_and_sorting(
        search_area, sort
    )
    assert sorting == expected_sorting
    assert actual_fields == expected_fields


def test_setup_opensearch(app):
    app.config["OPEN_SEARCH_HOST"] = "localhost"
    app.config["OPEN_SEARCH_HTTP_AUTH"] = ("test_user", "test_pass")
    app.config["OPEN_SEARCH_CA_CERTS"] = "test/path/to/certs"
    app.config["OPEN_SEARCH_VERIFY_CERTS"] = True
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
        body={"query": {"match_all": {}}}, from_=0, size=10, timeout=10
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
    query = "test_query"
    quoted_phrases, single_terms = extract_search_terms(query)
    dsl_query = build_dsl_search_query(
        ["field_1"],
        [{"clause_1": "test_2"}],
        quoted_phrases,
        single_terms,
        {"sort": "foobar"},
    )
    assert dsl_query == expected_base_dsl_search_query


def test_build_dsl_search_query_and_non_fuzzy_fuzzy_search():
    query = '"non_fuzzy"+fuzzy+search'
    search_fields = ["field_1"]
    filter_clauses = [{"clause_1": "test_2"}]
    quoted_phrases, single_terms = extract_search_terms(query)

    expected_dsl_query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": "non_fuzzy",
                            "fields": search_fields,
                            "type": "phrase",
                            "fuzziness": "AUTO",
                            "lenient": True,
                        }
                    },
                    {
                        "multi_match": {
                            "query": "fuzzy",
                            "fields": search_fields,
                            "fuzziness": "AUTO",
                            "lenient": True,
                        }
                    },
                    {
                        "multi_match": {
                            "query": "search",
                            "fields": search_fields,
                            "fuzziness": "AUTO",
                            "lenient": True,
                        }
                    },
                ],
                "filter": filter_clauses,
            }
        },
        "sort": {"sort": "foobar"},
        "_source": True,
    }

    dsl_query = build_dsl_search_query(
        search_fields,
        filter_clauses,
        quoted_phrases,
        single_terms,
        {"sort": "foobar"},
    )
    assert dsl_query == expected_dsl_query


def test_build_search_results_summary_query():
    query = "test_query"
    quoted_phrases, single_terms = extract_search_terms(query)
    dsl_query = build_search_results_summary_query(
        ["field_1"],
        quoted_phrases,
        single_terms,
        {"sort": "foobar"},
    )
    assert dsl_query == {
        **expected_base_dsl_search_query,
        "query": {
            "bool": {
                "should": [
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
    query = '"non_fuzzy"+fuzzy'
    quoted_phrases, single_terms = extract_search_terms(query)
    search_fields = [
       "file_name",
        "description",
        "foi_exemption_code",
        "content",
        "closure_start_date",
        "end_date",
        "date_last_modified",
        "citeable_reference",
        "series_name",
        "consignment_reference",
    ]

    # Helper to determine if a field should be treated as non_fuzzy (no fuzziness)
    def is_non_fuzzy_field(field):
        return (
            field.startswith("consignment_ref")
            or field.startswith("series")
            or "date" in field
        )

    # Split fields into non_fuzzy and fuzzy
    non_fuzzy_fields = [f for f in search_fields if is_non_fuzzy_field(f)]
    fuzzy_fields = [f for f in search_fields if not is_non_fuzzy_field(f)]


    expected_should_clauses = [
        # phrase on non_fuzzy fields
        {
            "multi_match": {
                "query": "non_fuzzy",
                "fields": non_fuzzy_fields,
                "fuzziness": 0,
                "type": "phrase",
                "lenient": True,
            }
        },
        # phrase on fuzzy fields
        {
            "multi_match": {
                "query": "non_fuzzy",
                "fields": fuzzy_fields,
                "type": "phrase",
                "fuzziness": "AUTO",
                "lenient": True,
            }
        },
        # single term on non_fuzzy fields
        {
            "multi_match": {
                "query": "fuzzy",
                "fields": non_fuzzy_fields,
                "fuzziness": 0,
                "lenient": True,
            }
        },
        # single term on fuzzy fields
        {
            "multi_match": {
                "query": "fuzzy",
                "fields": fuzzy_fields,
                "fuzziness": "AUTO",
                "lenient": True,
            }
        },
    ]
    dsl_query = build_search_transferring_body_query(
        search_fields,
        transferring_body_id,
        "test_highlight_key",
        quoted_phrases,
        single_terms,
        {"sort": "foobar"},
    )
    assert dsl_query == {
        "query": {
            "bool": {
                "should": expected_should_clauses,
                "filter": [
                    {
                        "term": {
                            "transferring_body_id.keyword": transferring_body_id
                        }
                    }
                ],
            }
        },
        "sort": {"sort": "foobar"},
        "_source": True,
        "highlight": {
            "pre_tags": ["<test_highlight_key>"],
            "post_tags": ["</test_highlight_key>"],
            "type": "unified",
            "fragment_size": 200,
            "number_of_fragments": 5,
            "phrase_limit": 256,
            "require_field_match": False,
            "boundary_scanner": "sentence",
            "boundary_scanner_locale": "en",
            "order": "score",
            "fields": {"*": {}},
        },
    }


@pytest.mark.parametrize(
    "input_results, expected_output",
    [
        # Case 1: All keys in highlight are valid (present in OPENSEARCH_FIELD_NAME_MAP)
        (
            [
                {
                    "highlight": {
                        key: [f"match_{key}"]
                        for key in OPENSEARCH_FIELD_NAME_MAP.keys()
                    }
                }
            ],
            [
                {
                    "highlight": {
                        key: [f"match_{key}"]
                        for key in OPENSEARCH_FIELD_NAME_MAP.keys()
                    }
                }
            ],
        ),
        # Case 2: Some keys in highlight are invalid (not in OPENSEARCH_FIELD_NAME_MAP)
        (
            [
                {
                    "highlight": {
                        "invalid_key_1": ["match_invalid_1"],
                        "file_name": ["match_file_name"],
                        "invalid_key_2": ["match_invalid_2"],
                        "description": ["match_description"],
                    }
                }
            ],
            [
                {
                    "highlight": {
                        "file_name": ["match_file_name"],
                        "description": ["match_description"],
                    }
                }
            ],
        ),
        # Case 3: Highlight contains only invalid keys
        (
            [
                {
                    "highlight": {
                        "invalid_key_1": ["match_invalid_1"],
                        "invalid_key_2": ["match_invalid_2"],
                    }
                }
            ],
            [{"highlight": {}}],
        ),
        # Case 4: Highlight is empty
        (
            [{"highlight": {}}],
            [{"highlight": {}}],
        ),
        # Case 5: No highlight key in the result
        (
            [{"title": "Title without highlight"}],
            [{"title": "Title without highlight"}],
        ),
        # Case 6: Empty results list
        (
            [],
            [],
        ),
    ],
)
def test_filter_opensearch_highlight_results(input_results, expected_output):
    assert filter_opensearch_highlight_results(input_results) == expected_output


@pytest.mark.parametrize(
    "fields, priority_fields, last_fields, expected_order",
    [
        # test case 1: Prioritize file_name at the top
        (
            {
                "file_name": "file1",
                "description": "desc1",
                "content": "content1",
            },
            ["file_name"],
            [],
            {
                "file_name": "file1",
                "description": "desc1",
                "content": "content1",
            },
        ),
        # test case 2: Prioritize description and then file_name
        (
            {
                "file_name": "file1",
                "description": "desc1",
                "content": "content1",
            },
            ["description", "file_name"],
            [],
            {
                "description": "desc1",
                "file_name": "file1",
                "content": "content1",
            },
        ),
        # test case 3: Move file_name and content to the bottom
        (
            {
                "file_name": "file1",
                "description": "desc1",
                "content": "content1",
            },
            [],
            ["file_name", "content"],
            {
                "description": "desc1",
                "file_name": "file1",
                "content": "content1",
            },
        ),
        # test case 4: Prioritize content, then file_name
        (
            {
                "file_name": "file1",
                "description": "desc1",
                "content": "content1",
            },
            ["content", "file_name"],
            [],
            {
                "content": "content1",
                "file_name": "file1",
                "description": "desc1",
            },
        ),
        # edge case 1: No fields present
        ({}, ["file_name"], [], {}),
        # edge case 2: All fields should be prioritized
        ({"file_name": "file1"}, ["file_name"], [], {"file_name": "file1"}),
        # edge case 3: Priority and last fields overlap
        (
            {"file_name": "file1", "description": "desc1"},
            ["file_name"],
            ["file_name"],
            {"file_name": "file1", "description": "desc1"},
        ),
        # edge case 4: Fields exist in middle but should be prioritized to last
        (
            {"description": "desc1", "file_name": "file1"},
            [],
            ["file_name"],
            {"description": "desc1", "file_name": "file1"},
        ),
    ],
)
def test_reorder_fields(fields, priority_fields, last_fields, expected_order):
    """
    Test the reorder_fields function to ensure it rearranges fields correctly.
    """
    assert (
        reorder_fields(fields, priority_fields, last_fields) == expected_order
    )


@pytest.mark.parametrize(
    "results, sort, expected_results",
    [
        # test case 1: sort by file_name, so file_name should be first
        (
            [
                {
                    "highlight": {
                        "file_name": ["example.txt"],
                        "description": ["desc"],
                    }
                }
            ],
            "file_name",
            [
                {
                    "highlight": {
                        "file_name": ["example.txt"],
                        "description": ["desc"],
                    }
                }
            ],
        ),
        # test case 2: sort by description, so description should be first, file_name second
        (
            [
                {
                    "highlight": {
                        "file_name": ["example.txt"],
                        "description": ["desc"],
                    }
                }
            ],
            "description",
            [
                {
                    "highlight": {
                        "description": ["desc"],
                        "file_name": ["example.txt"],
                    }
                }
            ],
        ),
        # test case 3: sort by metadata, file_name should be second to last, content last
        (
            [
                {
                    "highlight": {
                        "file_name": ["example.txt"],
                        "content": ["content1"],
                        "description": ["desc"],
                    }
                }
            ],
            "metadata",
            [
                {
                    "highlight": {
                        "description": ["desc"],
                        "file_name": ["example.txt"],
                        "content": ["content1"],
                    }
                }
            ],
        ),
        # test case 4: sort by content, so content should be first, file_name second
        (
            [
                {
                    "highlight": {
                        "file_name": ["example.txt"],
                        "content": ["content1"],
                        "description": ["desc"],
                    }
                }
            ],
            "content",
            [
                {
                    "highlight": {
                        "content": ["content1"],
                        "file_name": ["example.txt"],
                        "description": ["desc"],
                    }
                }
            ],
        ),
        # edge case 1: empty highlight dictionary
        (
            [{"highlight": {}}],
            "content",
            [{"highlight": {}}],
        ),
        # edge case 2: highlight without relevant fields
        (
            [{"highlight": {"metadata.size": ["1MB"], "author": ["John Doe"]}}],
            "file_name",
            [{"highlight": {"metadata.size": ["1MB"], "author": ["John Doe"]}}],
        ),
        # edge case 3: missing highlight field entirely
        (
            [{}],
            "content",
            [{}],
        ),
        # edge case 4: sorting order has no effect with unrelated fields
        (
            [
                {
                    "highlight": {
                        "content": ["content1"],
                        "file_name": ["example.txt"],
                    }
                }
            ],
            "non_existing_field",
            [
                {
                    "highlight": {
                        "content": ["content1"],
                        "file_name": ["example.txt"],
                    }
                }
            ],
        ),
    ],
)
def test_rearrange_opensearch_results_for_relevant_fields(
    results, sort, expected_results
):
    """
    Test the rearrange_opensearch_results_for_relevant_fields function to ensure it correctly
    reorders the entire result.
    """
    rearranged_results = rearrange_opensearch_results_for_relevant_fields(
        results, sort
    )
    assert rearranged_results == expected_results
