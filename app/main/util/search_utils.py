import opensearchpy
from flask import abort, current_app, request
from opensearchpy import OpenSearch, RequestsHttpConnection

from app.main.util.pagination import calculate_total_pages, get_pagination


def get_query_and_search_area():
    """Fetch query and search_area from form or request args"""
    query = request.form.get("query", "") or request.args.get("query", "")
    search_area = request.form.get("search_area", "") or request.args.get(
        "search_area", ""
    )
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
    size = per_page
    from_ = size * (page - 1)
    try:
        return open_search.search(
            dsl_query,
            from_=from_,
            size=size,
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


def get_all_fields_excluding(open_search, index_name, exclude_fields=None):
    """Retrieve all fields from the index and exclude certain fields"""
    mappings = open_search.indices.get_mapping(index=index_name)
    all_fields = list(mappings[index_name]["mappings"]["properties"].keys())
    filtered_fields = [
        field for field in all_fields if field not in exclude_fields or []
    ]

    return filtered_fields


def build_dsl_query(query, search_area, open_search, _id=None):
    """Construct the DSL query for OpenSearch"""
    fields_record = ["file_name", "file_path", "content"]
    fields_metadata = get_all_fields_excluding(
        open_search, "documents", fields_record
    )
    fields = ["*"]

    if search_area == "metadata":
        fields = fields_metadata
    elif search_area == "record":
        fields = fields_record

    must_clauses = [
        {
            "multi_match": {
                "query": query,
                "fields": fields,
                "operator": "AND",
                "fuzziness": "AUTO",
                "lenient": True,
            }
        }
    ]

    filter_clauses = (
        [{"term": {"transferring_body_id.keyword": _id}}] if _id else []
    )

    query = {
        "query": {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses,
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
    return query
