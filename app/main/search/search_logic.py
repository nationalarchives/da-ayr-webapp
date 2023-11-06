import logging
from typing import Any

from opensearchpy import ImproperlyConfigured

from app.main.aws.open_search import (
    generate_open_search_client_from_current_app_config,
)


def generate_open_search_client_and_make_poc_search(query: str, index) -> Any:
    open_search_client = generate_open_search_client_from_current_app_config()
    try:
        open_search_client.ping()
    except ImproperlyConfigured as e:
        logging.error("OpenSearch client improperly configured: " + str(e))
        raise e

    logging.info("OpenSearch client has been connected successfully")

    fields = [
        "legal_status",
        "description",
        "closure_type",
        "Internal-Sender_Identifier",
        "id",
        "Contact_Email",
        "Source_Organization",
        "Consignment_Series.keyword",
        "Consignment_Series",
        "Contact_Name",
    ]

    open_search_query = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": fields,
                "fuzziness": "AUTO",
                "type": "best_fields",
            }
        }
    }

    search_results = open_search_client.search(
        body=open_search_query, index=index
    )
    return search_results
