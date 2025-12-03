"""
Feature: Browse functionality
"""

import pytest
from playwright.sync_api import Page


def verify_browse_all_header_row(header_rows):
    assert header_rows == [
        "Transferring body",
        "Series reference",
        "Last transfer date",
        "Record total",
        "Consignments within series",
    ]


class TestBrowse:
    @property
    def route_url(self):
        return "/browse"

    @pytest.mark.health_check
    def test_browse_page_loads(self, aau_user_page: Page):
        """
        Health check: Verify browse page loads and displays data.
        Simplified version for quick monitoring.
        """
        aau_user_page.goto(f"{self.route_url}")

        aau_user_page.wait_for_selector("table", timeout=10000)

        assert aau_user_page.get_by_label("Sort by").is_visible()
        assert aau_user_page.get_by_role(
            "button", name="Apply filters"
        ).is_visible()

    def test_browse_with_filter_sort_and_choose_transferring_body(
        self, aau_user_page: Page, utils
    ):
        """
        Scenario: Sorting, filtering, and selecting transferring body

        Given the user is on the browse page
        When the user selects "Sort by" as "transferring_body-desc"
        And the user applies the filters with:
        | Transferring body filter | Mock 1 Department |
        | Date from day            | 1                 |
        | Date from month          | 1                 |
        | Date from year           | 2024              |
        Then the table headers should be:
        | Transferring body       |
        | Series reference        |
        | Last transfer date      |
        | Record total            |
        | Consignments within series |
        And the table rows should be:
        | Mock 1 Department | MOCK1 123 | 05/03/2024 | 15 | 7 |
        """
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.get_by_label("Sort by").select_option(
            "transferring_body-desc"
        )
        aau_user_page.get_by_role("button", name="Apply", exact=True).click()

        aau_user_page.locator("#transferring_body_filter").fill(
            "Mock 1 Department"
        )
        aau_user_page.locator("#date_from_day").fill("1")
        aau_user_page.locator("#date_from_month").fill("1")
        aau_user_page.locator("#date_from_year").fill("2024")
        aau_user_page.get_by_role("button", name="Apply filters").click()

        header_rows = utils.get_desktop_page_table_headers(aau_user_page)
        rows = utils.get_desktop_page_table_rows(aau_user_page)

        expected_rows = [
            ["Mock 1 Department", "MOCK1 123", "05/03/2024", "15", "7"]
        ]

        verify_browse_all_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_clear_filter_functionality(self, aau_user_page: Page):
        """
        Scenario: Clearing filter functionality

        Given the user navigates to the browse page with filters
        When the user selects "Sort by" as "transferring_body-desc"
        And the user applies the filters
        And the user clicks the "Clear filters" link
        Then the filters should be reset:
        | Series filter  | "" |
        | Date from day  | "" |
        | Date from month| "" |
        | Date from year | "" |
        | Date to day    | "" |
        | Date to month  | "" |
        | Date to year   | "" |
        And the "Sort by" dropdown should display "Transferring body (Z to A)"
        """
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.get_by_label("Sort by").select_option(
            "transferring_body-desc"
        )
        aau_user_page.get_by_role("button", name="Apply", exact=True).click()
        aau_user_page.get_by_role("link", name="Clear filters").click()
        assert aau_user_page.inner_text("#series_filter") == ""
        assert aau_user_page.inner_text("#date_from_day") == ""
        assert aau_user_page.inner_text("#date_from_month") == ""
        assert aau_user_page.inner_text("#date_from_year") == ""
        assert aau_user_page.inner_text("#date_to_day") == ""
        assert aau_user_page.inner_text("#date_to_month") == ""
        assert aau_user_page.inner_text("#date_to_year") == ""
        assert (
            aau_user_page.get_by_label("Sort by", exact=True).evaluate(
                "el => el.options[el.selectedIndex].text"
            )
            == "Transferring body (Z to A)"
        )
