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


def verify_filters_heading(data, expected_heading):
    """
    Check the filters heading text against expected value.
    """
    soup = BeautifulSoup(data, "html.parser")
    heading = soup.find("h2", class_="govuk-heading-m--browse-all-filter-title")

    assert heading is not None
    assert " ".join(heading.get_text(separator=" ").split()) == expected_heading


def get_datalist_values(data, datalist_id):
    """
    Return all option values from a datalist.
    """
    soup = BeautifulSoup(data, "html.parser")
    datalist = soup.find("datalist", id=datalist_id)

    assert datalist is not None
    return [
        option.get("value")
        for option in datalist.find_all("option")
        if option.get("value")
    ]


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
        verify_filters_heading(response.data, "Filters (0)")

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

    def test_browse_records_consignment_filter_limits_results(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given a consignment reference filter
        When browse records is requested with that filter
        Then only matching records are shown and the filter value is retained
        """
        mock_all_access_user(client)

        response = client.get(
            f"{self.route_url}?consignment_reference=TDR-2023-TH3"
        )

        assert response.status_code == 200
        assert b"Browse records 3" in response.data
        assert b"fourth_file.docx" in response.data
        assert b"fifth_file.docx" in response.data
        assert b"sixth_file.ppt" in response.data
        assert b"first_file.txt" not in response.data
        assert b'value="TDR-2023-TH3"' in response.data
        verify_filters_heading(response.data, "Filters (1)")

        soup = BeautifulSoup(response.data, "html.parser")
        transferring_body_filter = soup.find("input", id="transferring_body_filter")
        series_filter = soup.find("input", id="series_filter")

        assert transferring_body_filter is not None
        assert series_filter is not None
        assert transferring_body_filter.get("value") == "second_body"
        assert series_filter.get("value") == "second_series"

        record_links = soup.select(
            "tbody.govuk-table__body td[colspan='4'] > a[href^='/record/']"
        )
        assert len(record_links) == 3

    def test_browse_records_transferring_body_selection_limits_series_options(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given a transferring body filter
        When browse records is requested
        Then only series for that transferring body are offered
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?transferring_body_filter=first_body")

        assert response.status_code == 200
        series_values = get_datalist_values(response.data, "series_options")

        assert "first_series" in series_values
        assert "second_series" not in series_values

    def test_browse_records_series_selection_limits_consignment_options(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given a series filter
        When browse records is requested
        Then only consignments for that series are offered
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?series_filter=second_series")

        assert response.status_code == 200
        consignment_values = get_datalist_values(
            response.data, "consignment_options"
        )

        assert "TDR-2023-TH3" in consignment_values
        assert "TDR-2023-FO4" in consignment_values
        assert "TDR-2023-FI1" not in consignment_values

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
