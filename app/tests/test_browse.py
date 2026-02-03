from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.factories import BodyFactory
from app.tests.utils import decompose_desktop_invisible_elements


def verify_desktop_data_rows(data, expected_rows):
    """
    this function check data rows for data table compared with expected rows
    :param data: response data
    :param expected_rows: expected rows to be compared
    """
    soup = BeautifulSoup(data, "html.parser")
    decompose_desktop_invisible_elements(soup)
    table = soup.find("table")
    top_rows = table.find_all("tr")

    row_data = ""
    cells_as_text = []
    for row in top_rows:
        cells = row.find_all("td")
        for cell in cells:
            text = cell.text.replace("\n", " ").strip(" ")
            cells_as_text.append(f"'{text}'")
    row_data = ", ".join(cells_as_text)
    assert [row_data] == expected_rows[0]


def verify_browse_view_header_row(data):
    """
    this function check header row column values against expected row
    :param data: response data
    """
    soup = BeautifulSoup(data, "html.parser")
    decompose_desktop_invisible_elements(soup)
    table = soup.find("table")
    headers = table.find_all("th")

    expected_row = (
        [
            "Transferring body",
            "Series reference",
            "Last transfer date",
            "Record total",
            "Consignments within series",
        ],
    )
    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_row[0]


class TestBrowse:
    @property
    def route_url(self):
        return "/browse"

    @property
    def transferring_body_route_url(self):
        return "/browse/transferring_body"

    def test_standard_user_redirected_to_browse_transferring_body_when_accessing_browse(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request
        Then they should be redirected to the transferring_body browse page for
            the body they have access to
        """
        body = BodyFactory()
        mock_standard_user(client, body.Name)

        response = client.get(f"{self.route_url}")

        assert response.status_code == 302
        assert response.headers[
            "Location"
        ] == self.transferring_body_route_url + "/" + str(body.BodyId)

    def test_browse_get_view(self, client: FlaskClient, mock_all_access_user):
        """
        Given an all_access_user accessing the browse page
        When they make a GET request
        Then they should see the browse page content.
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}")

        assert response.status_code == 200
        assert b"Search for digital records" in response.data
        assert b"You are viewing" in response.data
        assert b"All available records" in response.data
