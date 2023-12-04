from unittest.mock import patch

from bs4 import BeautifulSoup
from flask.testing import FlaskClient
from sqlalchemy import exc

from app.main.db.queries import get_file_data_using_series_filter
from app.tests.mock_database import create_two_test_records


def test_browse_series_get(client: FlaskClient):
    """
    Given a user accessing the browse view series page
    When they make a GET request
    Then they should see the series browse view page and page content.
    """
    response = client.get("/poc-browse-series")

    assert response.status_code == 200
    assert b"Browse View - Series" in response.data
    assert b"Series :" in response.data
    # assert b"Search" in response.data


def test_browse_series_no_query(client: FlaskClient):
    """
    Given a user accessing the browse view series page
    When they make a POST request without a query
    Then they should not see any records found.
    """
    form_data = {"foo": "bar"}
    response = client.post("/poc-browse-series", data=form_data)

    assert response.status_code == 200
    assert b"Browse View - Series" in response.data
    assert b"Series :" in response.data


def test_browse_series_with_no_results(client: FlaskClient):
    """
    Given a user with a search query
    When they make a request on the browse view series page, and no results are found
    Then they should see no records found.
    """
    create_two_test_records()

    form_data = {"series": "junk"}
    response = client.post("/poc-browse-series", data=form_data)

    assert response.status_code == 200
    assert b"0 record(s) found"


def test_browse_series_results_displayed(client: FlaskClient):
    """
    Given a user with a search query which should return n results
    When they make a request on the browse series page
    Then a table is populated with the n results with metadata fields.
    """
    create_two_test_records()

    form_data = {"series": "test series1"}
    response = client.post("/poc-browse-series", data=form_data)

    assert response.status_code == 200
    assert b"1 record(s) found" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table", class_="govuk-table")
    rows = table.find_all("tr", class_="govuk-table__row")
    header_row = rows[0]
    results_rows = rows[1:]

    headers = header_row.find_all("th")

    expected_results_table = [
        [
            "Transferring Body",
            "Series",
            "Last Record Transferred",
            "Records held",
            "Consignment Reference",
        ],
        [
            "test body1",
            "test series1",
            "2023-01-01 00:00:00",
            "1",
            "test consignment1",
        ],
    ]

    assert [header.text for header in headers] == expected_results_table[0]
    for row_index, row in enumerate(results_rows):
        assert [
            result.text for result in row.find_all("td")
        ] == expected_results_table[row_index + 1]


@patch("app.main.db.queries.db")
def test_browse_series_exception_raised(db, capsys):
    """
    Given a browse series function
    When a call made to browse series , when database execution failed with error
    Then list should be empty and should raise an exception
    """

    def mock_execute(_):
        raise exc.SQLAlchemyError("foo bar")

    db.session.execute.side_effect = mock_execute
    results = get_file_data_using_series_filter("")
    assert results == []
    assert (
        "Failed to return results from database with error : foo bar"
        in capsys.readouterr().out
    )
