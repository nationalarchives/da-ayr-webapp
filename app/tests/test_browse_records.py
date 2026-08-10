from unittest.mock import patch

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


def verify_scope_text(data, expected_text):
    """
    Check the scope text above records count against expected value.
    """
    soup = BeautifulSoup(data, "html.parser")
    scope_text = soup.find("span", class_="browse__scope-text")

    assert scope_text is not None
    assert " ".join(scope_text.get_text(separator=" ").split()) == expected_text


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
        Then they see the records table with key record details
        and first page pagination
        """
        mock_all_access_user(client)

        response = client.get(self.route_url)

        assert response.status_code == 200
        assert b"Search for digital records" in response.data
        assert b"27 records" in response.data
        assert b"last modified" in response.data
        assert b"consignment" in response.data
        assert b"Land Registry" in response.data
        verify_filters_heading(response.data, "Filters (0)")
        verify_scope_text(response.data, "All available records")

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
        assert b"3 records" in response.data
        assert b"first_file.txt" in response.data
        assert b"second_file.pdf" in response.data
        assert b"third_file.doc" in response.data
        assert b"fourth_file.docx" not in response.data
        assert b"Land Registry" not in response.data
        verify_filters_heading(response.data, "Filters (0)")
        verify_scope_text(response.data, "first_body")

        soup = BeautifulSoup(response.data, "html.parser")
        transferring_body_filter = soup.find(
            "input", id="transferring_body_filter"
        )
        record_links = soup.select(
            "tbody.govuk-table__body td[colspan='4'] > a[href^='/record/']"
        )
        assert transferring_body_filter is not None
        assert transferring_body_filter.get("value") == "first_body"
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
        verify_scope_text(response.data, "All available records")

        soup = BeautifulSoup(response.data, "html.parser")

        previous_link = soup.select_one(".govuk-pagination__prev a")
        next_link = soup.select_one(".govuk-pagination__next a")

        assert previous_link is not None
        assert next_link is not None
        assert "page=1" in previous_link["href"]
        assert "page=3" in next_link["href"]

    def test_browse_records_standard_user_transferring_body_does_not_count(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a standard user with one accessible transferring body
        When they explicitly submit that transferring body filter
        Then it does not contribute to the filter count
        """
        mock_standard_user(client, "first_body")

        response = client.get(
            f"{self.route_url}?transferring_body_filter=first_body"
        )

        assert response.status_code == 200
        verify_filters_heading(response.data, "Filters (0)")

    def test_browse_records_standard_user_consignment_filter_backfills_series(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a standard user with a consignment filter
        When browse records is requested
        Then the matching series value is auto-populated
        """
        mock_standard_user(client, "first_body")

        response = client.get(
            f"{self.route_url}?consignment_reference=TDR-2023-FI1"
        )

        assert response.status_code == 200

        soup = BeautifulSoup(response.data, "html.parser")
        transferring_body_filter = soup.find(
            "input", id="transferring_body_filter"
        )
        series_filter = soup.find("input", id="series_filter")
        consignment_filter = soup.find("input", id="consignment_reference")

        assert transferring_body_filter is not None
        assert series_filter is not None
        assert consignment_filter is not None
        assert transferring_body_filter.get("value") == "first_body"
        assert series_filter.get("value") == "first_series"
        assert consignment_filter.get("value") == "TDR-2023-FI1"

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
        assert b"3 records found" in response.data
        assert b"fourth_file.docx" in response.data
        assert b"fifth_file.docx" in response.data
        assert b"sixth_file.ppt" in response.data
        assert b"first_file.txt" not in response.data
        assert b'value="TDR-2023-TH3"' in response.data
        verify_filters_heading(response.data, "Filters (3)")
        verify_scope_text(response.data, "All available records")

        soup = BeautifulSoup(response.data, "html.parser")
        transferring_body_filter = soup.find(
            "input", id="transferring_body_filter"
        )
        series_filter = soup.find("input", id="series_filter")

        assert transferring_body_filter is not None
        assert series_filter is not None
        assert transferring_body_filter.get("value") == "second_body"
        assert series_filter.get("value") == "second_series"

        record_links = soup.select(
            "tbody.govuk-table__body td[colspan='4'] > a[href^='/record/']"
        )
        assert len(record_links) == 3

    def test_browse_records_series_filter_backfills_transferring_body(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given a series filter that maps to a single transferring body
        When browse records is requested with that series
        Then the transferring body filter is auto-populated
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?series_filter=second_series")

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        transferring_body_filter = soup.find(
            "input", id="transferring_body_filter"
        )
        series_filter = soup.find("input", id="series_filter")

        assert transferring_body_filter is not None
        assert series_filter is not None
        assert transferring_body_filter.get("value") == "second_body"
        assert series_filter.get("value") == "second_series"

    @patch("app.main.util.browse_records_utils.get_autofill_options_rows")
    def test_browse_records_skips_autofill_query_on_initial_load(
        self,
        mock_get_autofill_options_rows,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
    ):
        """
        Given no series or consignment filter in the request
        When browse records is requested
        Then the targeted autofill options query is not executed
        """
        mock_all_access_user(client)
        mock_get_autofill_options_rows.return_value = []

        response = client.get(self.route_url)

        assert response.status_code == 200
        mock_get_autofill_options_rows.assert_not_called()

    @patch("app.main.util.browse_records_utils.get_autofill_options_rows")
    def test_browse_records_uses_targeted_autofill_query_for_series_filter(
        self,
        mock_get_autofill_options_rows,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
    ):
        """
        Given a series filter without an explicit transferring body
        When browse records is requested
        Then the targeted autofill options query executes with the series value
        """
        mock_all_access_user(client)
        mock_get_autofill_options_rows.return_value = []

        response = client.get(f"{self.route_url}?series_filter=second_series")

        assert response.status_code == 200
        mock_get_autofill_options_rows.assert_called_once_with(
            None,
            "second_series",
            "",
        )

    @patch("app.main.util.browse_records_utils.get_transferring_body_options")
    def test_browse_records_queries_transferring_body_options_once_for_all_access_user(
        self,
        mock_get_transferring_body_options,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
    ):
        """
        Given an all-access user
        When browse records is requested
        Then transferring body options are queried exactly once
        """
        mock_all_access_user(client)
        mock_get_transferring_body_options.return_value = [
            "first_body",
            "second_body",
        ]

        response = client.get(self.route_url)

        assert response.status_code == 200
        mock_get_transferring_body_options.assert_called_once_with(None)

    @patch("app.main.util.browse_records_utils.get_autofill_options_rows")
    @patch("app.main.util.browse_records_utils.get_transferring_body_options")
    def test_browse_records_series_filter_uses_expected_filter_queries_once_each(
        self,
        mock_get_transferring_body_options,
        mock_get_autofill_options_rows,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
    ):
        """
        Given an all-access user with series filter only
        When browse records is requested
        Then transferring body options and autofill options queries each run once
        """
        mock_all_access_user(client)
        mock_get_transferring_body_options.return_value = [
            "first_body",
            "second_body",
        ]
        mock_get_autofill_options_rows.return_value = []

        response = client.get(f"{self.route_url}?series_filter=second_series")

        assert response.status_code == 200
        mock_get_transferring_body_options.assert_called_once_with(None)
        mock_get_autofill_options_rows.assert_called_once_with(
            None,
            "second_series",
            "",
        )

    @patch("app.main.util.browse_records_utils.get_transferring_body_options")
    def test_browse_records_standard_user_skips_transferring_body_options_query(
        self,
        mock_get_transferring_body_options,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
    ):
        """
        Given a standard user with a single scope
        When browse records is requested
        Then transferring body options query is skipped
        """
        mock_standard_user(client, "first_body")

        response = client.get(self.route_url)

        assert response.status_code == 200
        mock_get_transferring_body_options.assert_not_called()

    def test_browse_records_series_filter_has_no_datalist(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given the browse records page
        When the series filter is rendered
        Then it is a plain text input without a datalist
        """
        mock_all_access_user(client)

        response = client.get(self.route_url)

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        series_filter = soup.find("input", id="series_filter")
        series_datalist = soup.find("datalist", id="series_options")

        assert series_filter is not None
        assert series_filter.get("list") is None
        assert series_datalist is None

    def test_browse_records_status_and_date_radio_defaults(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given the browse records page
        When filters render
        Then status defaults to all and dates defaults to last modified
        """
        mock_all_access_user(client)

        response = client.get(self.route_url)

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        status_all = soup.find("input", id="recordStatus-all")
        status_open = soup.find("input", id="recordStatus-open")
        status_closed = soup.find("input", id="recordStatus-closed")
        last_modified_date = soup.find("input", id="date_last_modified")
        transferred_date = soup.find("input", id="transferred_date")

        assert status_all is not None
        assert status_open is not None
        assert status_closed is not None
        assert last_modified_date is not None
        assert transferred_date is not None
        assert status_all.has_attr("checked")
        assert not status_open.has_attr("checked")
        assert not status_closed.has_attr("checked")
        assert last_modified_date.has_attr("checked")
        assert not transferred_date.has_attr("checked")

    def test_browse_records_status_filter_open_selection_persists(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given the open status filter
        When browse records is requested
        Then the open status option is selected
        and any visible status tags are open
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?record_status=open")

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        status_all = soup.find("input", id="recordStatus-all")
        status_open = soup.find("input", id="recordStatus-open")
        status_closed = soup.find("input", id="recordStatus-closed")

        assert status_all is not None
        assert status_open is not None
        assert status_closed is not None
        assert not status_all.has_attr("checked")
        assert status_open.has_attr("checked")
        assert not status_closed.has_attr("checked")

        status_tags = soup.select(
            "td.browse-records__meta-cell--status strong.govuk-tag"
        )
        assert all(
            tag.get_text(strip=True) in ["Open", "Unknown"]
            for tag in status_tags
        )

    def test_browse_records_date_filter_field_selection_persists(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given an opening date filter field selection
        When browse records is requested
        Then opening date radio remains selected
        """
        mock_all_access_user(client)

        response = client.get(
            f"{self.route_url}?date_filter_field=opening_date"
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        opening_date = soup.find("input", id="opening_date")

        assert opening_date is not None
        assert opening_date.has_attr("checked")

    def test_browse_records_consignment_filter_has_no_datalist(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given the browse records page
        When the consignment filter is rendered
        Then it is a plain text input without a datalist
        """
        mock_all_access_user(client)

        response = client.get(self.route_url)

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        consignment_filter = soup.find("input", id="consignment_reference")
        consignment_datalist = soup.find("datalist", id="consignment_options")

        assert consignment_filter is not None
        assert consignment_filter.get("list") is None
        assert consignment_datalist is None

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

    def test_browse_records_per_page_persists_in_filter_controls(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given records-per-page is explicitly selected
        When browse records filters are rendered
        Then per_page is preserved in filter form submits and clear-filters link
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?per_page=20")

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        filters_form = soup.find(
            "form", action="/browse/records#browse-records"
        )
        assert filters_form is not None

        hidden_per_page = filters_form.find(
            "input",
            {"type": "hidden", "name": "per_page", "value": "20"},
        )
        clear_filters_link = filters_form.find("a", string="Clear filters")

        assert hidden_per_page is not None
        assert clear_filters_link is not None
        assert "per_page=20" in clear_filters_link.get("href", "")

    def test_browse_records_filters_and_sort_persist_in_per_page_controls(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given browse records has active filters and sort
        When per-page controls are rendered
        Then they preserve active query params except page and per_page
        """
        mock_all_access_user(client)

        response = client.get(
            f"{self.route_url}?consignment_reference=TDR-2023-TH3&sort=file_name-desc&page=1&per_page=10"
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        per_page_forms = soup.select(
            "form.sort-list-records-form, form.sort-list-records-no-js-form"
        )
        assert len(per_page_forms) == 2

        for form in per_page_forms:
            hidden_consignment = form.find(
                "input",
                {
                    "type": "hidden",
                    "name": "consignment_reference",
                    "value": "TDR-2023-TH3",
                },
            )
            hidden_sort = form.find(
                "input",
                {
                    "type": "hidden",
                    "name": "sort",
                    "value": "file_name-desc",
                },
            )
            hidden_page = form.find("input", {"type": "hidden", "name": "page"})
            hidden_per_page = form.find(
                "input", {"type": "hidden", "name": "per_page"}
            )

            assert hidden_consignment is not None
            assert hidden_sort is not None
            assert hidden_page is None
            assert hidden_per_page is None

    def test_browse_records_no_results_for_nonsensical_filter(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given a nonsensical filter term
        When browse records is requested
        Then no records found is displayed
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?series_filter=zzzzzzzzzzzzzz")

        assert response.status_code == 200
        assert b"No records found" in response.data
        verify_scope_text(response.data, "All available records")

    @pytest.mark.parametrize("body_name", ["first_body", "second_body"])
    def test_browse_records_scope_text_changes_for_different_accounts(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
        body_name,
    ):
        """
        Given different standard user accounts
        When browse records is requested
        Then transferring body scope text reflects each account
        """
        mock_standard_user(client, body_name)
        response = client.get(self.route_url)

        assert response.status_code == 200
        verify_scope_text(response.data, body_name)
