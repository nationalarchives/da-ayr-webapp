from unittest.mock import patch

from bs4 import BeautifulSoup
from flask.testing import FlaskClient
from sqlalchemy import exc

from app.main.db.queries import browse_view
from app.tests.mock_database import create_two_test_records


def test_browse_view_get(client: FlaskClient):
    """
    Given a user accessing the browse page
    When they make a GET request
    Then they should see the browse page content.
    """
    response = client.get("/poc-browse")

    assert response.status_code == 200
    assert b"Browse View" in response.data
    assert b"Everything available to you" in response.data


def test_browse_view_with_no_results(client: FlaskClient):
    """
    Given user logged in application
    When they make a request on the browse page, and no results are found
    Then they should see no records found.
    """
    # no mock data function executed , so data not exist in db

    form_data = {}
    response = client.post("/poc-browse", data=form_data)

    assert response.status_code == 200
    assert b"0 record(s) found"


def test_browse_view_results_displayed(client: FlaskClient):
    """
    Given user logged in application
    When they make a request on the browse page
    Then a table is populated with the n results with metadata fields.
    """
    create_two_test_records()

    form_data = {"query": "test"}
    response = client.post("/poc-browse", data=form_data)

    assert response.status_code == 200
    assert b"2 record(s) found" in response.data

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
            "Consignment in Series",
        ],
        ["test body1", "test series1", "2023-01-01 00:00:00", "1", "1"],
        ["test body2", "test series2", "2023-01-01 00:00:00", "1", "1"],
    ]

    assert [header.text for header in headers] == expected_results_table[0]
    for row_index, row in enumerate(results_rows):
        assert [
            result.text for result in row.find_all("td")
        ] == expected_results_table[row_index + 1]


@patch("app.main.db.queries.db")
def test_fuzzy_search_exception_raised(db, capsys):
    """
    Given a fuzzy search function
    When a call made to fuzzy search , when database execution failed with error
    Then list should be empty and should raise an exception
    """

    def mock_execute(_):
        raise exc.SQLAlchemyError("foo bar")

    db.session.execute.side_effect = mock_execute
    results = browse_view()
    assert results == []
    assert (
        "Failed to return results from database with error : foo bar"
        in capsys.readouterr().out
    )
