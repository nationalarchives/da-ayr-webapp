from playwright.sync_api import Page


class TestBrowseSeries:
    @property
    def route_url(self):
        return "/browse/series"

    @property
    def series_id(self):
        return "1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7"

    def test_browse_series_404_for_no_access(self, standard_user_page: Page):
        """
        Scenario: Accessing a series page with invalid ID

        Given a standard user
        When the user tries to access a series page with an invalid ID
        Then the user should see a 'Page not found' message
        And should be prompted to check the web address correctness
        """
        series_id = "8bd7ad22-90d1-4c7f-ae00-645dfd1987cc"

        standard_user_page.goto(f"{self.route_url}/{series_id}")

        assert standard_user_page.inner_html("text='Page not found'")
        assert standard_user_page.inner_html(
            "text='If you typed the web address, check it is correct.'"
        )
        assert standard_user_page.inner_html(
            "text='If you pasted the web address, check you copied the entire address.'"
        )

    def test_browse_series_clear_filter_functionality(
        self, standard_user_page: Page
    ):
        """
        Scenario: Clearing filters for series records

        Given a standard user with applied filters
        When the user clicks on 'Clear filters' link
        Then all filter fields should be cleared
        And the sorting should revert to default ('Records total (most)')
        """
        standard_user_page.goto(f"{self.route_url}/{self.series_id}")
        standard_user_page.get_by_label("Sort by").select_option(
            "records_held-desc"
        )
        standard_user_page.get_by_role(
            "button", name="Apply", exact=True
        ).click()
        standard_user_page.get_by_role("link", name="Clear filters").click()

        assert standard_user_page.inner_text("#date_from_day") == ""
        assert standard_user_page.inner_text("#date_from_month") == ""
        assert standard_user_page.inner_text("#date_from_year") == ""
        assert standard_user_page.inner_text("#date_to_day") == ""
        assert standard_user_page.inner_text("#date_to_month") == ""
        assert standard_user_page.inner_text("#date_to_year") == ""
        assert (
            standard_user_page.get_by_label("Sort by", exact=True).evaluate(
                "el => el.options[el.selectedIndex].text"
            )
            == "Records total (most)"
        )
