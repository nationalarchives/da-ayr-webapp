from unittest.mock import patch

from bs4 import BeautifulSoup
from flask.testing import FlaskClient
from sqlalchemy import exc

from app.main.db.queries import browse_view_transferring_body
from app.tests.mock_database import create_two_test_records


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_browse_transferring_body_get(
    mock_decode_keycloak_access_token, app, client: FlaskClient
):
    """
    Given a user accessing the browse view body page
    When they make a GET request
    Then they should see the browse view body page content.
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["application_1/foo", "application_2/bar"],
    }

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        response = client.get("/poc-browse-transferring-body")

    assert response.status_code == 200
    assert b"Browse View" in response.data
    assert b"Transferring Body :" in response.data


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_browse_transferring_body_with_no_results(
    mock_decode_keycloak_access_token, app, client: FlaskClient
):
    """
    Given user logged in application
    When they make a request on the browse view body page, and no results are found
    Then they should see no records found.
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["application_1/foo", "application_2/bar"],
    }

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

        form_data = {}
        response = client.post("/poc-browse-transferring-body", data=form_data)

    assert response.status_code == 200
    assert b"0 record(s) found"


@patch(
    "app.main.authorize.access_token_sign_in_required.keycloak.KeycloakOpenID.introspect"
)
def test_browse_transferring_body_results_displayed(
    mock_decode_keycloak_access_token, app, client: FlaskClient
):
    """
    Given user logged in application
    When they make a request on the browse page
    Then a table is populated with the n results with metadata fields.
    """
    mock_decode_keycloak_access_token.return_value = {
        "active": True,
        "groups": ["application_1/foo", "application_2/bar"],
    }

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["access_token"] = "valid_token"

    create_two_test_records()

    form_data = {"transferring-body": "test body1"}
    response = client.post("/poc-browse-transferring-body", data=form_data)

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
            "Consignment in Series",
        ],
        ["test body1", "test series1", "2023-01-01 00:00:00", "1", "1"],
    ]

    assert [header.text for header in headers] == expected_results_table[0]
    for row_index, row in enumerate(results_rows):
        assert [
            result.text for result in row.find_all("td")
        ] == expected_results_table[row_index + 1]


@patch("app.main.db.queries.db")
def test_browse_view_exception_raised(db, capsys):
    """
    Given a browse view function
    When a call made to browse view , when database execution failed with error
    Then list should be empty and should raise an exception
    """

    def mock_execute(_):
        raise exc.SQLAlchemyError("foo bar")

    db.session.execute.side_effect = mock_execute
    results = browse_view_transferring_body("")
    assert results == []
    assert (
        "Failed to return results from database with error : foo bar"
        in capsys.readouterr().out
    )
