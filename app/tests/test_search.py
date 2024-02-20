from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    SeriesFactory,
)


def test_search_get(client: FlaskClient, mock_superuser):
    """
    Given a superuser accessing the search page
    When they make a GET request
    Then they should see the search form and page content.
    """
    mock_superuser(client)
    response = client.get("/search")

    assert response.status_code == 200
    assert b"Search" in response.data
    assert b"Search for digital records" in response.data
    assert b"Search" in response.data


def test_search_no_query(client: FlaskClient, mock_superuser):
    """
    Given a superuser accessing the search page
    When they make a GET request without a query
    Then they should not see any records found.
    """
    mock_superuser(client)
    form_data = {"foo": "bar"}
    response = client.get("/search", data=form_data)

    assert response.status_code == 200
    assert b"records found" not in response.data


def test_search_with_no_results(client: FlaskClient, mock_superuser):
    """
    Given a superuser with a search query
    When they make a request on the search page, and no results are found
    Then they should see no records found.
    """
    mock_superuser(client)
    FileFactory(FileType="file", FileName="foo")

    form_data = {"query": "bar"}
    response = client.get("/search", data=form_data)

    assert response.status_code == 200
    assert b"0 record(s) found"


def test_search_box(client, mock_superuser):
    mock_superuser(client)

    response = client.get("/search")

    assert response.status_code == 200

    html = response.data.decode()

    search_html = """<div class="search__container govuk-grid-column-full">
    <div class="search__container__content">
        <p class="govuk-body search__heading">Search for digital records</p>
        <form method="get" action="/search">
            <div class="govuk-form-group govuk-form-group__search-form">
                <label for="searchInput"></label>
                <input class="govuk-input govuk-!-width-three-quarters"
                       id="searchInput"
                       name="query"
                       type="text">
                <button class="govuk-button govuk-button__search-button"
                        data-module="govuk-button"
                        type="submit">Search</button>
            </div>
            <p class="govuk-body-s">
                Search using a record metadata term, for example – transferring body, series,
                consignment
                ref etc.
            </p>
        </form>
    </div>
</div>"""

    assert_contains_html(
        search_html,
        html,
        "div",
        {"class": "search__container govuk-grid-column-full"},
    )


def test_search_results_displayed_single_page(
    client: FlaskClient, app, mock_standard_user
):
    """
    Given a standard user with access to a body, and there are files from that body and another body
        and a search query which matches a property from related file data
    When they make a request on the search page with the search term
    Then a table is populated with the n results with metadata fields for the files from there body.
    """
    body = BodyFactory(Name="body_foo")

    [
        FileFactory(
            FileType="file",
            FileName=file_name,
            consignment=ConsignmentFactory(
                ContactName="test_contact",
                ConsignmentReference="consignment_foo",
                series=SeriesFactory(
                    Name="series_bar", body=BodyFactory(Name="body_bar")
                ),
            ),
        )
        for file_name in ["a", "b", "c"]
    ]

    [
        FileFactory(
            FileType="file",
            FileName=file_name,
            consignment=ConsignmentFactory(
                ContactName="test_contact",
                ConsignmentReference="consignment_foo",
                series=SeriesFactory(Name="series_foo", body=body),
            ),
        )
        for file_name in ["d", "e"]
    ]

    mock_standard_user(client, body.Name)

    app.config["DEFAULT_PAGE_SIZE"] = 5
    form_data = {"query": "test_contact"}
    response = client.get("/search", data=form_data)

    assert response.status_code == 200
    assert b"Results found 2" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table", class_="govuk-table")
    rows = table.find_all("tr", class_="govuk-table__row")
    header_row = rows[0]
    results_rows = rows[1:]

    headers = header_row.find_all("th")

    expected_results_table = [
        ["Transferring body", "Series", "Consignment reference", "File name"],
        ["body_foo", "series_foo", "consignment_foo", "d"],
        ["body_foo", "series_foo", "consignment_foo", "e"],
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
    Given a standard user with access to a body, and there are files from that body and another body
        and a search query which matches a property from related file data
        and the pagination size K is set to less than the number of files in the body
    When they make a request on the search page with the search term
    Then a table is populated with the first K results with metadata fields for the files from there body.
    And the pagination widget is displayed
    """
    body = BodyFactory(Name="body_foo")

    [
        FileFactory(
            FileType="file",
            FileName=file_name,
            consignment=ConsignmentFactory(
                ContactName="test_contact",
                ConsignmentReference="consignment_bar",
                series=SeriesFactory(
                    Name="series_bar", body=BodyFactory(Name="body_bar")
                ),
            ),
        )
        for file_name in ["a", "b", "c"]
    ]

    [
        FileFactory(
            FileType="file",
            FileName=file_name,
            consignment=ConsignmentFactory(
                ContactName="test_contact",
                ConsignmentReference="consignment_foo",
                series=SeriesFactory(Name="series_foo", body=body),
            ),
        )
        for file_name in ["d", "e", "f", "g", "h"]
    ]

    mock_standard_user(client, body.Name)

    app.config["DEFAULT_PAGE_SIZE"] = 2
    form_data = {"query": "test_contact"}
    response = client.get("/search", data=form_data)

    assert response.status_code == 200
    assert b"Results found 5" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table", class_="govuk-table")
    rows = table.find_all("tr", class_="govuk-table__row")
    header_row = rows[0]
    results_rows = rows[1:]

    headers = header_row.find_all("th")

    expected_results_table = [
        ["Transferring body", "Series", "Consignment reference", "File name"],
        ["body_foo", "series_foo", "consignment_foo", "d"],
        ["body_foo", "series_foo", "consignment_foo", "e"],
        ["body_foo", "series_foo", "consignment_foo", "f"],
        ["body_foo", "series_foo", "consignment_foo", "g"],
        ["body_foo", "series_foo", "consignment_foo", "h"],
    ]

    assert [header.text for header in headers] == expected_results_table[0]
    for row_index, row in enumerate(results_rows):
        assert [
            result.text for result in row.find_all("td")
        ] == expected_results_table[row_index + 1]
    # check pagination
    assert b'aria-label="Page 1"' in response.data
    assert b'aria-label="Page 2"' in response.data
