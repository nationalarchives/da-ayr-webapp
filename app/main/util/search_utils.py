import opensearchpy
from flask import abort, current_app
from opensearchpy import OpenSearch, RequestsHttpConnection

from app.main.util.date_validator import format_opensearch_date
from app.main.util.pagination import calculate_total_pages, get_pagination


def format_opensearch_results(results):
    results_clone = results
    for result in results_clone:
        for key, value in result["_source"].items():
            if "date" in key:
                result["_source"][key] = format_opensearch_date(value or "")
    return results_clone


def get_open_search_fields_to_search_on(open_search, search_area):
    """Retrieve a list of fields depending on the search area (all fields, metadata, record, etc.)"""
    fields_record = ["content"]
    if search_area == "metadata":
        return get_all_fields_excluding(open_search, "documents", fields_record)
    elif search_area == "record":
        return fields_record
    return ["*"]


def get_param(param, request):
    """Get a specific param from either form or args"""
    return request.form.get(param, "") or request.args.get(param, "")


def get_query_and_search_area(request):
    """Fetch query and search_area from form or request args"""
    query = get_param("query", request)
    search_area = get_param("search_area", request)
    return query.strip(), search_area


def setup_opensearch():
    """Setup and return an OpenSearch client"""
    return OpenSearch(
        hosts=current_app.config.get("OPEN_SEARCH_HOST"),
        http_auth=current_app.config.get("OPEN_SEARCH_HTTP_AUTH"),
        use_ssl=True,
        verify_certs=True,
        ca_certs=current_app.config.get("OPEN_SEARCH_CA_CERTS"),
        connection_class=RequestsHttpConnection,
    )


def execute_search(open_search, dsl_query, page, per_page):
    """Execute the search query using OpenSearch"""
    from_ = per_page * (page - 1)
    try:
        return open_search.search(
            dsl_query,
            from_=from_,
            size=per_page,
            timeout=current_app.config["OPEN_SEARCH_TIMEOUT"],
        )
    except opensearchpy.exceptions.ConnectionTimeout:
        abort(504)


def get_pagination_info(results, page, per_page):
    """Calculate pagination information"""
    total_records = (
        results["hits"]["total"]["value"] if "hits" in results else 0
    )
    page_count = calculate_total_pages(total_records, per_page)
    pagination = get_pagination(page, page_count)
    return total_records, pagination


def get_filtered_list(to_filter, filter):
    """Filters a list based on the contents of another list"""
    return [field for field in to_filter if field not in filter or []]


def get_all_fields_excluding(open_search, index_name, exclude_fields=None):
    """Retrieve all fields from the index and exclude certain fields"""
    mappings = open_search.indices.get_mapping(index=index_name)
    all_fields = list(mappings[index_name]["mappings"]["properties"].keys())
    filtered_fields = get_filtered_list(all_fields, exclude_fields)

    return filtered_fields


def build_dsl_search_query(
    query, search_fields, sorting_orders, filter_clauses
):
    """Constructs the base DSL query for OpenSearch"""
    return {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": search_fields,
                            "fuzziness": "AUTO",
                            "lenient": True,
                        }
                    }
                ],
                "filter": filter_clauses,
            }
        },
        # set as {} until sorting ticket is in done
        "sort": {},
        "_source": True,
    }


def build_search_results_summary_query(query, search_fields, sorting_orders):
    filter_clauses = []
    dsl_query = build_dsl_search_query(
        query, search_fields, sorting_orders, filter_clauses
    )
    aggregations = {
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
    return {**dsl_query, **aggregations}


def build_search_transferring_body_query(
    query, search_fields, sorting_orders, transferring_body_id
):
    filter_clauses = [
        {"term": {"transferring_body_id.keyword": transferring_body_id}}
    ]
    dsl_query = build_dsl_search_query(
        query, search_fields, sorting_orders, filter_clauses
    )
    highlighting = {
        "highlight": {
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
            "fields": {
                "*": {},
            },
        },
    }
    return {**dsl_query, **highlighting}
