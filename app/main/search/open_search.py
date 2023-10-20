import logging
from typing import Any, List, Tuple

import boto3
from opensearchpy import AWSV4SignerAuth, ImproperlyConfigured, OpenSearch

from app.main.aws import parameter

AWS_ENVIRONMENT_PREFIX = parameter.get_aws_environment_prefix()


def generate_open_search_client_and_make_poc_search(query: str) -> Any:
    open_search_client = generate_open_search_client_from_aws_params()
    open_search_index = parameter.get_parameter_store_key_value(
        AWS_ENVIRONMENT_PREFIX + "AWS_OPEN_SEARCH_INDEX"
    )
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
    open_search_response = make_multi_match_fuzzy_search(
        open_search_client, query, open_search_index, fields
    )
    return open_search_response


def make_multi_match_fuzzy_search(
    open_search: OpenSearch, search_text: str, index: str, fields: List[str]
):
    open_search_query = {
        "query": {
            "multi_match": {
                "query": search_text,
                "fields": fields,
                "fuzziness": "AUTO",
                "type": "best_fields",
            }
        }
    }
    search_results = open_search.search(body=open_search_query, index=index)
    return search_results


def generate_open_search_client_from_aws_params() -> OpenSearch:
    host = parameter.get_parameter_store_key_value(
        AWS_ENVIRONMENT_PREFIX + "AWS_OPEN_SEARCH_HOST"
    )
    http_auth = _get_open_search_http_auth()

    open_search_client = OpenSearch(
        hosts=[{"host": host, "port": 443}],
        http_auth=http_auth,
        use_ssl=True,
        verify_certs=True,
        http_compress=True,  # enables gzip compression for request bodies
        ssl_assert_hostname=False,
        ssl_show_warn=True,
    )
    try:
        open_search_client.ping()
    except ImproperlyConfigured as e:
        logging.error("OpenSearch client improperly configured: " + str(e))

    logging.info("OpenSearch client has been connected successfully")
    return open_search_client


def _get_open_search_http_auth(
    auth_method: str = "username_password",
) -> Tuple[str, str] | AWSV4SignerAuth:
    if auth_method == "username_password":
        return _get_open_search_username_password_auth()
    return _get_open_search_iam_auth()


def _get_open_search_username_password_auth() -> Tuple[str, str]:
    username = parameter.get_parameter_store_key_value(
        AWS_ENVIRONMENT_PREFIX + "AWS_OPEN_SEARCH_USERNAME"
    )
    password = parameter.get_parameter_store_key_value(
        AWS_ENVIRONMENT_PREFIX + "AWS_OPEN_SEARCH_PASSWORD"
    )
    return (username, password)


def _get_open_search_iam_auth() -> AWSV4SignerAuth:
    credentials = boto3.Session().get_credentials()
    aws_region = parameter.get_parameter_store_key_value(
        AWS_ENVIRONMENT_PREFIX + "AWS_REGION"
    )
    service = "es"
    aws_auth = AWSV4SignerAuth(credentials, aws_region, service)
    return aws_auth
