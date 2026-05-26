import re

from playwright.sync_api import Page, expect


def verify_search_results_summary_header_row(header_rows):
    assert header_rows == [
        "Results found within each Transferring body",
        "Records found",
    ]


def verify_search_transferring_body_header_row(header_rows):
    assert header_rows == [
        "Found within",
        "Search results",
        "Series",
        "Consignment ref",
        "Status",
        "Record opening date",
    ]


def verify_search_transferring_body_table_header_row(header_rows):
    assert header_rows == [
        "Found within",
        "Search results",
    ]


def verify_search_transferring_body_inner_table_row(header_rows):
    assert set(header_rows) == {
        "Consignment ref",
        "Record opening date",
        "Series",
        "Status",
    }


class TestSearch:
    @property
    def browse_route_url(self):
        return "/browse"

    def test_search_returns_results_summary(self, aau_user_page: Page):
        """
        Given a standard user
        When they interact with the search form and submit a query
        Then they should be routed to a search results summary screen
        with the expected table and controls visible
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.wait_for_selector("#tbl_result")

        assert "/search_results_summary" in aau_user_page.url
        assert "query=a" in aau_user_page.url
        assert aau_user_page.locator("#tbl_result").is_visible()


class TestSearchResultsSummary:
    @property
    def search_results_summary_route_url(self):
        return "/search_results_summary?query=a"

    def test_select_transferring_body_search_results(self, aau_user_page: Page):
        """
        Given a user on the search results summary page for a query
        When they click on one of the transferring bodies
        Then they are redirected to the search results for that transferring body for the query
        and the results table renders
        """
        aau_user_page.goto(self.search_results_summary_route_url)
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.wait_for_selector("#tbl_result")
        assert "/search/transferring_body/" in aau_user_page.url
        assert "query=a" in aau_user_page.url
        assert aau_user_page.locator("#tbl_result").is_visible()


class TestSearchTransferringBody:
    @property
    def browse_route_url(self):
        return "/browse"

    @property
    def browse_transferring_body_route_url(self):
        return "/browse/transferring_body"

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    def test_remove_all_terms_as_standard_user_redirects_to_browse_transferring_body(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with a search term
        and then remove the search term
        Then they should be redirected to browse transferring body page.
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        locator = aau_user_page.locator(
            "a.search-term-link[aria-label=\"Remove filter for 'a'\"] img.close-icon"
        )
        locator.wait_for(state="visible")
        locator.click()

        browse_transferring_body_url = re.escape(
            self.browse_transferring_body_route_url
        )
        params = r"\?.*search_area=everywhere.*"
        # Use regex to match URL with additional query parameters
        pattern = rf""".*{browse_transferring_body_url}/{re.escape(self.transferring_body_id)}{params}"""
        url_pattern = re.compile(pattern)
        expect(aau_user_page).to_have_url(url_pattern)

    def test_click_on_clear_all_as_aau_user_redirects_to_browse(
        self, aau_user_page: Page
    ):
        """
        Given an all access user on the search transferring body page
        When they interact with the search form and submit a query with multiple search terms
        and the click on clear all option
        Then they should be redirected to browse all page.
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.get_by_role("link", name="Clear all").click()

        expect(aau_user_page).to_have_url(
            f"{self.browse_route_url}#browse-records"
        )

    def test_click_on_clear_all_as_standard_user_redirects_to_browse_transferring_body(
        self, standard_user_page: Page
    ):
        """
        Given a standard access user on the search transferring body page
        When they interact with the search form and submit a query with multiple search terms
        and the click on clear all option
        Then they should be redirected to browse all page.
        """
        url = f"{self.browse_transferring_body_route_url}/{self.transferring_body_id}#browse-records"
        standard_user_page.goto(url)
        standard_user_page.locator("#search-input").click()
        standard_user_page.locator("#search-input").fill("a")
        standard_user_page.get_by_role("button", name="Search").click()
        standard_user_page.get_by_role("link", name="Clear all").click()

        expect(standard_user_page).to_have_url(url)
