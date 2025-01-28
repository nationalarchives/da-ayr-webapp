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

        expected_rows = [["Testing A", "14"]]
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
            ["TSTA 1", "TDR-2023-GXFH", "", "–"],
            ["TSTA 1", "TDR-2023-BV6", "", "–"],
            ["TSTA 1", "TDR-2023-BV6", "", "–"],
            ["TSTA 1", "TDR-2023-BV6", "", "–"],
            ["TSTA 1", "TDR-2023-GXFH", "", "–"],
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


class TestOpenSearchResults:
    @property
    def search_route_url(self):
        return "/search_results_summary"

    @property
    def browse_transferring_body_route_url(self):
        return "/search/transferring_body"

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    def test_test_search(self, aau_user_page: Page):
        """
        Given a valid search query is entered on the search page
        When the query is submitted
        Then the search_results_summary page should display relevant results,
        ensuring the results are fetched from OpenSearch and shown with correct metadata formatting
        And when a transferring body is clicked on
        Then the search_results/transferring_body/<body_id> page should display the filtered results correctly
        """
        url = f"{self.search_route_url}?query=a&search_area=everywhere"

        aau_user_page.goto("/browse")

        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        expect(aau_user_page).to_have_url(url)

        assert (
            "Testing A"
            in aau_user_page.locator("tbody.govuk-table__body td")
            .nth(0)
            .text_content()
        )

    def test_test_search_fuzzy_search(self, standard_user_page: Page):
        """
        Given a search query is submitted with a typo (e.g., minor misspelling) on the
        search_results/transferring_body/<body_id> page
        When the results are displayed
        Then the results should use fuzziness logic to account for the typo and display relevant matches
        """
        url = f"{self.browse_transferring_body_route_url}/{self.transferring_body_id}#browse-records"

        standard_user_page.goto(url)
        expect(standard_user_page).to_have_url(url)

        standard_user_page.locator("#search-input").click()
        standard_user_page.locator("#search-input").fill("a")
        standard_user_page.get_by_role("button", name="Search").click()
        standard_user_page.locator("#search_filter").fill("samplt")
        standard_user_page.get_by_role("button", name="Apply terms").click()
        standard_user_page.locator("#search_filter").fill("a1")
        standard_user_page.get_by_role("button", name="Apply terms").click()
        rows = standard_user_page.locator("tbody .govuk-table__row")
        assert rows.count() == 18

        found = False
        for i in range(rows.count()):
            row_text = rows.nth(i).text_content().strip()
            if "sample" in row_text:
                found = True
                break

        assert found

        expected_search_terms = ["a", "samplt", "a1"]
        tags_container = standard_user_page.locator(".ayr-filter-tags")
        assert tags_container.is_visible()

        search_terms = tags_container.locator(".search-term")
        assert search_terms.count() == len(expected_search_terms)

        for i, expected_term in enumerate(expected_search_terms):
            tag = search_terms.nth(i)
            assert tag.is_visible()

            tag_text = tag.text_content().strip()
            assert expected_term in tag_text
