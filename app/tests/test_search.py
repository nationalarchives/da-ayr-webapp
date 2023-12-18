from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.mock_database import create_multiple_test_records


def test_search_get(client: FlaskClient, app):
    """
    Given a user accessing the search page
    When they make a GET request
    Then they should see the search form and page content.
    """
    app.config["DEFAULT_PAGE_SIZE"] = 5

    response = client.get("/poc-search")

    assert response.status_code == 200
    assert b"Search design PoC" in response.data
    assert b"Search for digital records" in response.data
    assert b"Search" in response.data


def test_search_no_query(client: FlaskClient, app):
    """
    Given a user accessing the search page
    When they make a POST request without a query
    Then they should not see any records found.
    """
    app.config["DEFAULT_PAGE_SIZE"] = 5
    form_data = {"foo": "bar"}
    response = client.post("/poc-search", data=form_data)

    assert response.status_code == 200
    assert b"records found" not in response.data


def test_search_with_no_results(client: FlaskClient, app):
    """
    Given a user with a search query
    When they make a request on the search page, and no results are found
    Then they should see no records found.
    """
    create_multiple_test_records()
    app.config["DEFAULT_PAGE_SIZE"] = 5
    form_data = {"query": "junk"}
    response = client.post("/poc-search", data=form_data)

    assert response.status_code == 200
    assert b"0 record(s) found"


def test_search_results_displayed_single_page(client: FlaskClient, app):
    """
    Given a user with a search query which should return n results
    When they make a request on the search page
    Then a table is populated with the n results with metadata fields.
    """
    create_multiple_test_records()
    app.config["DEFAULT_PAGE_SIZE"] = 5
    form_data = {"query": "test body"}
    response = client.post("/poc-search", data=form_data)

    assert response.status_code == 200
    assert b"3 record(s) found" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table", class_="govuk-table")
    rows = table.find_all("tr", class_="govuk-table__row")
    header_row = rows[0]
    results_rows = rows[1:]

    headers = header_row.find_all("th")

    expected_results_table = [
        ["Transferring body", "Series", "Consignment reference", "File name"],
        ["test body1", "test series1", "test consignment1", "test_file1.pdf"],
        ["test body2", "test series2", "test consignment2", "test_file2.txt"],
        [
            "testing body11",
            "test series11",
            "test consignment11",
            "test_file11.txt",
        ],
    ]

    assert [header.text for header in headers] == expected_results_table[0]
    for row_index, row in enumerate(results_rows):
        assert [
            result.text for result in row.find_all("td")
        ] == expected_results_table[row_index + 1]
    # check pagination
    assert b'aria-label="Page 1"' in response.data


def test_search_results_displayed_multiple_pages(client: FlaskClient, app):
    """
    Given a user with a search query which should return n results
    When they make a request on the search page
    Then a table is populated with the n results with metadata fields.
    """
    create_multiple_test_records()
    app.config["DEFAULT_PAGE_SIZE"] = 5
    form_data = {"query": "testing body"}
    response = client.post("/poc-search", data=form_data)

    assert response.status_code == 200
    assert b"5 record(s) found" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table", class_="govuk-table")
    rows = table.find_all("tr", class_="govuk-table__row")
    header_row = rows[0]
    results_rows = rows[1:]

    headers = header_row.find_all("th")

    expected_results_table = [
        ["Transferring body", "Series", "Consignment reference", "File name"],
        [
            "testing body10",
            "test series10",
            "test consignment10",
            "test_file10.txt",
        ],
        [
            "testing body11",
            "test series11",
            "test consignment11",
            "test_file11.txt",
        ],
        [
            "testing body3",
            "test series3",
            "test consignment3",
            "test_file3.pdf",
        ],
        [
            "testing body4",
            "test series4",
            "test consignment4",
            "test_file4.txt",
        ],
        [
            "testing body5",
            "test series5",
            "test consignment5",
            "test_file5.txt",
        ],
    ]

    assert [header.text for header in headers] == expected_results_table[0]
    for row_index, row in enumerate(results_rows):
        assert [
            result.text for result in row.find_all("td")
        ] == expected_results_table[row_index + 1]
    # check pagination
    assert b'aria-label="Page 1"' in response.data
    assert b'aria-label="Page 2"' in response.data
