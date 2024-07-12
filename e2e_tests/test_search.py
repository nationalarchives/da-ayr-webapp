from playwright.sync_api import Page, expect


def verify_search_results_summary_header_row(header_rows):
    assert header_rows == [
        "Results found within each Transferring body",
        "Records found",
    ]


def verify_search_transferring_body_header_row(header_rows):
    assert header_rows == [
        "Series reference",
        "Consignment reference",
        "File name",
        "Status",
        "Record opening date",
    ]


class TestSearch:
    @property
    def browse_route_url(self):
        return "/browse"

    def test_search_returns_results_summary(self, aau_user_page: Page, utils):
        """
        Given a standard user
        When they interact with the search form and submit a query
        Then the table should contain the expected headers and entries
        and sorted transferring bodies in alphabetic order (A to Z)
        on a search results summary screen
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.wait_for_selector("#tbl_result")

        header_rows = utils.get_desktop_page_table_headers(aau_user_page)
        rows = utils.get_desktop_page_table_rows(aau_user_page)

        expected_rows = [["Mock 1 Department", "83"], ["Testing A", "16"]]
        verify_search_results_summary_header_row(header_rows)
        assert rows == expected_rows


class TestSearchResultsSummary:
    @property
    def search_results_summary_route_url(self):
        return "/search_results_summary?query=a"

    def test_select_transferring_body_search_results(
        self, aau_user_page: Page, utils
    ):
        """
        Given a user on the search results summary page for a query
        When they click on one of the transferring bodies
        Then they are redirected to the search results for that transferring body for the query
        """
        aau_user_page.goto(self.search_results_summary_route_url)
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.wait_for_selector("#tbl_result")

        header_rows = utils.get_desktop_page_table_headers(aau_user_page)
        rows = utils.get_desktop_page_table_rows(aau_user_page)

        expected_rows = [
            ["TSTA 1", "TDR-2023-BV6", "closed_file_R.pdf", "Open", "–"],
            [
                "TSTA 1",
                "TDR-2023-BV6",
                "closed_file.txt",
                "Closed",
                "18/10/2048",
            ],
            ["TSTA 1", "TDR-2023-BV6", "file-a1.txt", "Open", "–"],
            ["TSTA 1", "TDR-2023-BV6", "file-a2.txt", "Open", "–"],
            ["TSTA 1", "TDR-2023-BV6", "file-b1.txt", "Open", "–"],
        ]

        verify_search_transferring_body_header_row(header_rows)
        assert rows == expected_rows


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
        aau_user_page.get_by_role("link", name="a", exact=True).click()

        url = f"{self.browse_transferring_body_route_url}/{self.transferring_body_id}"
        expect(aau_user_page).to_have_url(url)

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
