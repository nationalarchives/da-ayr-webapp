from unittest.mock import patch
from bs4 import BeautifulSoup
from flask.testing import FlaskClient


def test_poc_search_get(client: FlaskClient):
    """
    Given a user accessing the search page
    When they make a GET request
    Then they should see the search form and page content.
    """
    response = client.get("/poc-search-view")

    assert response.status_code == 200
    assert b"Search design PoC" in response.data
    assert b"Search for digital records" in response.data
    assert b"Search" in response.data


def test_poc_search_no_query(client: FlaskClient):
    """
    Given a user accessing the search page
    When they make a POST request without a query
    Then they should not see any records found.
    """
    form_data = {"foo": "bar"}
    response = client.post("/poc-search-view", data=form_data)

    assert response.status_code == 200
    assert b"records found" not in response.data


@patch("app.main.routes.search_logic.generate_open_search_client_and_make_poc_search")
def test_poc_search_with_no_results(mock_open_search, client: FlaskClient):
    """
    Given a user with a search query
    When they make a request on the search page, and no results are found
    Then they should see no records found.
    """
    mock_open_search.return_value = {"hits": {"hits": []}}

    form_data = {"query": "test_query"}
    response = client.post("/poc-search-view", data=form_data)

    assert response.status_code == 200
    assert b"records found" not in response.data


@patch("app.main.routes.search_logic.generate_open_search_client_and_make_poc_search")
def test_poc_search_results_displayed(mock_open_search, client: FlaskClient):
    """
    Given a user with a search query which should return n results
    When they make a request on the search page
    Then a table is populated with the n results with metadata fields.
    """
    mock_open_search.return_value = {
        "hits": {
            "hits": [
                {
                    "_source": {
                        "file_name": "Mocked Result 1",
                        "description": "Description 1",
                        "date_last_modified": "2023-02-27T12:28:08",
                        "legal_status": "Public Record(s)",
                        "closure_period": 20,
                    }
                },
                {
                    "_source": {
                        "file_name": "Mocked Result 2",
                        "description": "Description 2",
                        "date_last_modified": "2023-02-27T12:28:13",
                        "legal_status": "Public Record(s)",
                        "closure_period": 5,
                    }
                },
            ]
        }
    }

    form_data = {"query": "test_query"}
    response = client.post("/poc-search-view", data=form_data)

    assert response.status_code == 200
    assert b"2 records found" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table", class_="govuk-table")
    rows = table.find_all("tr", class_="govuk-table__row")
    header_row = rows[0]
    results_rows = rows[1:]

    headers = header_row.find_all("th")

    expected_results_table = [
        ["Title", "Description", "Last modified", "Status", "Closure period (years)"],
        [
            "Mocked Result 1",
            "Description 1",
            "2023-02-27T12:28:08",
            "Public Record(s)",
            "20",
        ],
        [
            "Mocked Result 2",
            "Description 2",
            "2023-02-27T12:28:13",
            "Public Record(s)",
            "5",
        ],
    ]

    assert [header.text for header in headers] == expected_results_table[0]
    for row_index, row in enumerate(results_rows):
        assert [result.text for result in row.find_all("td")] == expected_results_table[
            row_index + 1
        ]
