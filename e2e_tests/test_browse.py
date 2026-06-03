"""
Feature: Browse functionality
"""

from playwright.sync_api import Page


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
