"""
Feature: Browse functionality
"""

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
