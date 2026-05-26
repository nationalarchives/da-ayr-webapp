from playwright.sync_api import Page


class TestBrowseTransferringBody:
    @property
    def route_url(self):
        return "/browse/transferring_body"

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    def test_browse_transferring_body_404_for_no_access(
        self, standard_user_page: Page
    ):
        """
        Scenario: Attempting to browse non-existent transferring body results in Page not found

        Given an id that does not correspond to a id of a Body in the database
        When the user navigates to browse/transferring_body/id
        Then they see Page not found
        """
        transferring_body_id = "8ccc8cd1-c0ee-431d-afad-70cf404ba337"

        standard_user_page.goto(f"{self.route_url}/{transferring_body_id}")
        assert standard_user_page.inner_html("text='Page not found'")
        assert standard_user_page.inner_html(
            "text='If you typed the web address, check it is correct.'"
        )
        assert standard_user_page.inner_html(
            "text='If you pasted the web address, check you copied the entire address.'"
        )

    def test_browse_transferring_body_no_results_found(
        self, standard_user_page: Page
    ):
        """
        Scenario: Attempting to browse non-existent transferring body results in Page not found

        Given an id that does not correspond to a id of a Body in the database
        When the user navigates to browse/transferring_body/id
        Then they see Page not found
        """
        standard_user_page.goto(f"{self.route_url}/{self.transferring_body_id}")
        standard_user_page.locator("#series_filter").click()
        standard_user_page.locator("#series_filter").fill("junk")
        standard_user_page.get_by_role("button", name="Apply filters").click()

        assert standard_user_page.inner_html("text='No results found'")
        assert standard_user_page.inner_html("text='Help with your search'")
        assert standard_user_page.inner_html(
            "text='Try changing or removing one or more applied filters.'"
        )
        assert standard_user_page.locator(
            "text='Alternatively, use the breadcrumbs to navigate back to the'"
        ).is_visible()

    def test_browse_transferring_body_clear_filter_functionality(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.transferring_body_id}")
        standard_user_page.get_by_label("Sort by").select_option("series-desc")
        standard_user_page.get_by_role(
            "button", name="Apply", exact=True
        ).click()
        standard_user_page.get_by_role("link", name="Clear filters").click()
        assert standard_user_page.inner_text("#series_filter") == ""
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
            == "Series reference (Z to A)"
        )
