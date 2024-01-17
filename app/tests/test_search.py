from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    SeriesFactory,
)


def test_search_get(client: FlaskClient, mock_standard_user):
    """
    Given a user accessing the search page
    When they make a GET request
    Then they should see the search form and page content.
    """
    mock_standard_user(client)
    response = client.get("/search")

    assert response.status_code == 200
    assert b"Search" in response.data
    assert b"Search for digital records" in response.data
    assert b"Search" in response.data


def test_search_no_query(client: FlaskClient, mock_standard_user):
    """
    Given a user accessing the search page
    When they make a POST request without a query
    Then they should not see any records found.
    """
    mock_standard_user(client)
    form_data = {"foo": "bar"}
    response = client.post("/search", data=form_data)

    assert response.status_code == 200
    assert b"records found" not in response.data


def test_search_with_no_results(client: FlaskClient, mock_standard_user):
    """
    Given a user with a search query
    When they make a request on the search page, and no results are found
    Then they should see no records found.
    """
    mock_standard_user(client)
    FileFactory(FileType="file", FileName="foo")

    form_data = {"query": "bar"}
    response = client.post("/search", data=form_data)

    assert response.status_code == 200
    assert b"0 record(s) found"


def test_search_results_displayed_single_page(
    client: FlaskClient, app, mock_standard_user
):
    """
    Given a user with a search query which should return n results
    When they make a request on the search page
    Then a table is populated with the n results with metadata fields.
    """
    mock_standard_user(client)
    [
        FileFactory(
            FileType="file",
            FileName=file_name,
            consignment=ConsignmentFactory(
                ContactName="test_contact",
                ConsignmentReference="consignment_foo",
                series=SeriesFactory(
                    Name="series_foo", body=BodyFactory(Name="body_foo")
                ),
            ),
        )
        for file_name in ["a", "b", "c"]
    ]

    app.config["DEFAULT_PAGE_SIZE"] = 5
    form_data = {"query": "test_contact"}
    response = client.post("/search", data=form_data)

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
        ["body_foo", "series_foo", "consignment_foo", "a"],
        ["body_foo", "series_foo", "consignment_foo", "b"],
        ["body_foo", "series_foo", "consignment_foo", "c"],
    ]

    assert [header.text for header in headers] == expected_results_table[0]
    for row_index, row in enumerate(results_rows):
        assert [
            result.text for result in row.find_all("td")
        ] == expected_results_table[row_index + 1]

    assert (
        b'<nav class="govuk-pagination govuk-pagination--centred" role="navigation" aria-label="Pagination">'
        not in response.data
    )


def test_search_results_displayed_multiple_pages(
    client: FlaskClient, app, mock_standard_user
):
    """
    Given a user with a search query which should return n results
    When they make a request on the search page
    Then a table is populated with the n results with metadata fields.
    """
    mock_standard_user(client)

    [
        FileFactory(
            FileType="file",
            FileName=file_name,
            consignment=ConsignmentFactory(
                ContactName="test_contact",
                ConsignmentReference="consignment_foo",
                series=SeriesFactory(
                    Name="series_foo", body=BodyFactory(Name="body_foo")
                ),
            ),
        )
        for file_name in ["a", "b", "c", "d", "e", "f", "g", "h"]
    ]

    app.config["DEFAULT_PAGE_SIZE"] = 2
    form_data = {"query": "test_contact"}
    response = client.post("/search", data=form_data)

    assert response.status_code == 200
    assert b"8 record(s) found" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table", class_="govuk-table")
    rows = table.find_all("tr", class_="govuk-table__row")
    header_row = rows[0]
    results_rows = rows[1:]

    headers = header_row.find_all("th")

    expected_results_table = [
        ["Transferring body", "Series", "Consignment reference", "File name"],
        ["body_foo", "series_foo", "consignment_foo", "a"],
        ["body_foo", "series_foo", "consignment_foo", "b"],
    ]

    assert [header.text for header in headers] == expected_results_table[0]
    for row_index, row in enumerate(results_rows):
        assert [
            result.text for result in row.find_all("td")
        ] == expected_results_table[row_index + 1]
    # check pagination
    assert b'aria-label="Page 1"' in response.data
    assert b'aria-label="Page 2"' in response.data
