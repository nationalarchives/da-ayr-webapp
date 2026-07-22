import pytest
from bs4 import BeautifulSoup
from flask.testing import FlaskClient


def verify_browse_records_view_header_row(data, expected_first_header):
    """
    Check browse records header row values against expected values.
    """
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")

    expected_row = [
        expected_first_header,
        "Series",
        "Status",
        "Opening date",
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_row


class TestBrowseRecords:
    @property
    def route_url(self):
        return "/browse/records"

    def test_browse_records_get_view_for_all_access_user(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given an all-access user
        When they visit browse records
        Then they see the records table with key record details and first page pagination
        """
        mock_all_access_user(client)

        response = client.get(self.route_url)

        assert response.status_code == 200
        assert b"Search for digital records" in response.data
        assert b"Browse records 27" in response.data
        assert b"last modified" in response.data
        assert b"consignment" in response.data

        verify_browse_records_view_header_row(
            response.data, "Showing 1\u20135 of 27"
        )

        soup = BeautifulSoup(response.data, "html.parser")
        record_links = soup.select(
            "tbody.govuk-table__body td[colspan='4'] > a[href^='/record/']"
        )
        assert len(record_links) == 5

    def test_browse_records_for_standard_user_only_shows_accessible_body(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a standard user with access to one transferring body
        When they visit browse records
        Then they only see records for that body
        """
        mock_standard_user(client, "first_body")

        response = client.get(self.route_url)

        assert response.status_code == 200
        assert b"Browse records 3" in response.data
        assert b"first_file.txt" in response.data
        assert b"second_file.pdf" in response.data
        assert b"third_file.doc" in response.data
        assert b"fourth_file.docx" not in response.data

        soup = BeautifulSoup(response.data, "html.parser")
        record_links = soup.select(
            "tbody.govuk-table__body td[colspan='4'] > a[href^='/record/']"
        )
        assert len(record_links) == 3

    def test_browse_records_second_page_shows_expected_range_and_links(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given more than one page of records
        When the user opens page 2
        Then pagination displays expected range and previous/next links
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?page=2")

        assert response.status_code == 200
        verify_browse_records_view_header_row(
            response.data, "Showing 6\u201310 of 27"
        )

        soup = BeautifulSoup(response.data, "html.parser")

        previous_link = soup.select_one(".govuk-pagination__prev a")
        next_link = soup.select_one(".govuk-pagination__next a")

        assert previous_link is not None
        assert next_link is not None
        assert "page=1" in previous_link["href"]
        assert "page=3" in next_link["href"]

    @pytest.mark.parametrize(
        "per_page, expected_header, expected_count",
        [
            (10, "Showing 1\u201310 of 27", 10),
            (20, "Showing 1\u201320 of 27", 20),
        ],
    )
    def test_browse_records_per_page_query_updates_page_size(
        self,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
        per_page,
        expected_header,
        expected_count,
    ):
        """
        Given browse records supports per_page query input
        When per_page is requested from the frontend
        Then the first page size and range text match per_page
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?per_page={per_page}")

        assert response.status_code == 200
        verify_browse_records_view_header_row(response.data, expected_header)

        soup = BeautifulSoup(response.data, "html.parser")
        record_links = soup.select(
            "tbody.govuk-table__body td[colspan='4'] > a[href^='/record/']"
        )
        assert len(record_links) == expected_count

    def test_browse_records_invalid_page_redirects_to_first_page(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given an invalid out-of-range page number
        When browse records is requested
        Then the user is redirected to page 1
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?page=999")

        assert response.status_code == 302
        assert "page=1" in response.headers["Location"]
