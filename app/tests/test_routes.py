from bs4 import BeautifulSoup
from flask.testing import FlaskClient


def verify_cookies_header_row(data):
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")

    expected_row = (
        [
            "Cookie name",
            "What it does/typical content",
            "Duration",
        ],
    )
    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_row[0]


def verify_cookies_data_rows(data, expected_rows):
    """
    this function check data rows for data table compared with expected rows
    :param data: response data
    :param expected_rows: expected rows to be compared
    """
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    rows = table.find_all("td")

    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "

    assert [row_data] == expected_rows[0]


class TestRoutes:
    def test_route_accessibility(self, client: FlaskClient):
        response = client.get("/accessibility")
        assert response.status_code == 200

    def test_route_cookies(self, client: FlaskClient):
        response = client.get("/cookies")
        assert response.status_code == 200

    def test_route_privacy(self, client: FlaskClient):
        response = client.get("/privacy")
        assert response.status_code == 200

    def test_route_how_to_use(self, client: FlaskClient):
        response = client.get("/how-to-use-this-service")
        assert response.status_code == 200

    def test_route_terms_of_use(self, client: FlaskClient):
        response = client.get("/terms-of-use")
        assert response.status_code == 200
