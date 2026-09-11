import re

from playwright.sync_api import Page, expect


class TestSearchResultsFlow:
    @property
    def browse_route_url(self):
        return "/browse"

    @property
    def canonical_search_results_route(self):
        return "/search/results"

    @property
    def browse_transferring_body_route_url(self):
        return "/browse/transferring_body"

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    def test_search_from_browse_opens_canonical_search_results(
        self, aau_user_page: Page
    ):
        aau_user_page.goto(self.browse_route_url)
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.wait_for_selector("#tbl_result")

        assert self.canonical_search_results_route in aau_user_page.url
        assert "query=a" in aau_user_page.url
        assert aau_user_page.locator("#tbl_result").is_visible()

    def test_clear_filters_keeps_all_access_user_on_search_results(
        self, aau_user_page: Page
    ):
        aau_user_page.goto(self.browse_route_url)
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Clear filters").click()

        expect(aau_user_page).to_have_url(
            re.compile(r".*/search/results\?query=a.*#browse-records")
        )

    def test_clear_filters_keeps_standard_user_on_search_results(
        self, standard_user_page: Page
    ):
        url = (
            f"{self.browse_transferring_body_route_url}/"
            f"{self.transferring_body_id}#browse-records"
        )
        standard_user_page.goto(url)
        standard_user_page.locator("#search-input").fill("a")
        standard_user_page.get_by_role("button", name="Search").click()
        standard_user_page.get_by_role("link", name="Clear filters").click()

        expect(standard_user_page).to_have_url(
            re.compile(r".*/search/results\?query=a.*#browse-records")
        )

    def test_search_results_shows_browse_filter_component(
        self, aau_user_page: Page
    ):
        aau_user_page.goto(f"{self.canonical_search_results_route}?query=a")
        expect(aau_user_page.get_by_role("heading", name="Filters")).to_be_visible()
        expect(aau_user_page.get_by_text("Closed")).to_be_visible()
