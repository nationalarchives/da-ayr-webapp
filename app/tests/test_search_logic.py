from unittest.mock import Mock, patch

import pytest
from opensearchpy import ImproperlyConfigured

from app.main.search.search_logic import (
    generate_open_search_client_and_make_poc_search,
)


@patch(
    "app.main.search.search_logic.generate_open_search_client_from_current_app_config"
)
def test_generate_open_search_client_and_make_poc_search(
    mock_generate_open_search_client_from_current_app_config,
):
    """
    Given a query and index
    When generate_open_search_client_and_make_poc_search is called
        and a ping is successfully made to the instance
    Then the search query is executed, and the results are returned.
    """
    query = "foo bar"
    index = "test_index"

    mock_open_search_client = Mock()
    mock_open_search_client.search.return_value = ["result 1", "result 2"]
    mock_generate_open_search_client_from_current_app_config.return_value = (
        mock_open_search_client
    )

    results = generate_open_search_client_and_make_poc_search(query, index)

    mock_open_search_client.ping.assert_called_once()

    mock_open_search_client.search.assert_called_once_with(
        body={
            "query": {
                "multi_match": {
                    "query": "foo bar",
                    "fields": [
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
                    ],
                    "fuzziness": "AUTO",
                    "type": "best_fields",
                }
            }
        },
        index="test_index",
    )
    assert results == ["result 1", "result 2"]


@patch(
    "app.main.search.search_logic.generate_open_search_client_from_current_app_config"
)
def test_generate_open_search_client_and_make_poc_search_raises_connection_error(
    mock_generate_open_search_client_from_current_app_config,
):
    """
    Given a query and index
    When generate_open_search_client_and_make_poc_search is called with them,
        but an ImproperlyConfigured error occurs when pinging the OpenSearch instance
    Then an ImproperlyConfigured exception is raised, with additional logging message
    """
    query = "foo bar"
    index = "test_index"

    mock_open_search_client = Mock()
    mock_open_search_client.search.return_value = ["result 1", "result 2"]

    def raise_improperly_configured_exception():
        raise ImproperlyConfigured()

    mock_open_search_client.ping.side_effect = (
        raise_improperly_configured_exception
    )
    mock_generate_open_search_client_from_current_app_config.return_value = (
        mock_open_search_client
    )

    with pytest.raises(ImproperlyConfigured):
        generate_open_search_client_and_make_poc_search(query, index)
        mock_open_search_client.ping.assert_called_once()
        mock_open_search_client.search.assert_not_called()
