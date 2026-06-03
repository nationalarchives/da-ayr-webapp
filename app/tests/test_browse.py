from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html
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

    def test_browse_check_transferring_bodies_list_filled_for_all_access_user(
        self, client: FlaskClient, browse_files, mock_all_access_user
    ):
        """
        Given an all_access_user accessing the browse page
        When they make a GET request
        Then they should see the browse page content
        and transferring body dropdown will be filled with list of all transferring bodies available in database
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}")

        assert response.status_code == 200

        html = response.data.decode()

        expected_html = """
                <input
                    class="govuk-input"
                    id="transferring_body_filter"
                    name="transferring_body_filter"
                    type="text"
                    list="transferring_bodies"
                    autocomplete="off"
                >
            """

        assert_contains_html(
            expected_html,
            html,
            "input",
            {"name": "transferring_body_filter"},
        )

    def test_browse_submit_search_query(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given an all_access_user accessing the browse page
        When they make a POST request
        Then they should see results in content.
        """
        mock_all_access_user(client)

        query = "test"
        response = client.get(f"{self.route_url}", data={"query": query})

        assert response.status_code == 200

        assert b"Search for digital records" in response.data
        assert b"Browse records 27" in response.data

    def test_browse_filter_sort_and_choose_transferring_body_contract(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given an all access user with browse fixtures
        When they apply transferring body and date filters with sort order
        Then results are filtered/sorted and include a selectable transferring body link
        """
        mock_all_access_user(client)

        response = client.get(
            "/browse?sort=transferring_body-desc&transferring_body_filter=first_body"
            "&date_from_day=01&date_from_month=01&date_from_year=2023"
        )

        assert response.status_code == 200
        verify_browse_view_header_row(response.data)
        verify_desktop_data_rows(
            response.data,
            [["'first_body', 'first_series', '07/02/2023', '3', '2'"]],
        )

        soup = BeautifulSoup(response.data, "html.parser")
        decompose_desktop_invisible_elements(soup)
        body_link = soup.find(
            "a",
            href=f"{self.transferring_body_route_url}/{browse_files[0].consignment.series.body.BodyId}",
        )
        assert body_link is not None
