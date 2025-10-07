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

        expected_rows = [["Testing A", "16"], ["AYR Test Data Department", "2"]]
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
        aau_user_page.click('label[for="contact"]')
        aau_user_page.locator(
            ".govuk-button.govuk-button__sort-container-update-button"
        ).nth(1).click()

        header_rows = utils.get_desktop_page_transferring_body_table_headers(
            aau_user_page
        )

        inner_table_header_rows = (
            utils.get_desktop_page_transferring_body_inner_table_headers(
                aau_user_page
            )
        )

        table_row_metadata = utils.get_desktop_page_table_metadata(
            aau_user_page
        )

        expected_row_metadata = [
            ["TSTA 1", "TDR-2023-BV6", "Open", "–"],
            ["TSTA 1", "TDR-2023-BV6", "Open", "–"],
            ["TSTA 1", "TDR-2023-GXFH", "Open", "–"],
            ["TSTA 1", "TDR-2023-GXFH", "Open", "–"],
            ["TSTA 1", "TDR-2023-BV6", "Open", "–"],
            ["TSTA 1", "TDR-2023-BV6", "Open", "–"],
            ["TSTA 1", "TDR-2023-BV6", "Closed", "18/10/2048"],
            ["TSTA 1", "TDR-2023-BV6", "Open", "–"],
            ["TSTA 1", "TDR-2023-BV6", "Open", "–"],
            ["TSTA 1", "TDR-2023-GXFH", "Open", "–"],
        ]

        assert table_row_metadata == expected_row_metadata

        verify_search_transferring_body_table_header_row(header_rows)
        verify_search_transferring_body_inner_table_row(inner_table_header_rows)


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

        url = f"{self.browse_transferring_body_route_url}/{self.transferring_body_id}?search_area=everywhere"
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


class TestSearchResults:
    @property
    def search_route_url(self):
        return "/search_results_summary"

    @property
    def browse_transferring_body_route_url(self):
        return "/search/transferring_body"

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    def test_search_fuzzy_search(self, standard_user_page: Page):
        """
        Given a search query is submitted with a typo (e.g., minor misspelling) on the
        search_results/transferring_body/<body_id> page
        When the results are displayed
        Then the results should use fuzziness logic to account for the typo and display relevant matches
        """
        url = f"{self.browse_transferring_body_route_url}/{self.transferring_body_id}?query=a#browse-records"

        standard_user_page.goto(url)
        expect(standard_user_page).to_have_url(url)

        standard_user_page.locator("#search-input").click()
        standard_user_page.locator("#search-input").fill("fil")
        standard_user_page.get_by_role("button", name="Search").click()
        standard_user_page.wait_for_selector("tbody .govuk-table__row--primary")
        rows = standard_user_page.locator("tbody .govuk-table__row--primary")
        assert rows.count() == 9

        tbody_locator = standard_user_page.locator("tbody.govuk-table__body")
        inner_html = tbody_locator.inner_html()

        assert "<mark>file</mark>" in inner_html
