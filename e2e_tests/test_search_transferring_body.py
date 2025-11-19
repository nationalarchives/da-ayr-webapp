from playwright.sync_api import Page, expect


def _check_row_count(page: Page):
    # Check if there are any results
    try:
        page.wait_for_selector("tbody .govuk-table__row--primary", timeout=3000)
        rows = page.locator("tbody .govuk-table__row--primary")
        row_count = rows.count()
        return row_count
    except Exception:
        # No results found (timeout or selector not found)
        return 0


class TestSearchResults:
    """
    Essential integration tests for non-fuzzy field matching in search functionality.
    These tests verify the end-to-end behavior that consignment_ref, series, and date fields
    only match in a non-fuzzy, phrase type way and not with fuzzy matching.
    Most detailed testing of this logic is done via unit tests in test_search_utils.py.
    """

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    @property
    def transferring_body_search_url(self):
        return f"/search/transferring_body/{self.transferring_body_id}"

    def test_search_fuzzy_search(self, standard_user_page: Page):
        """
        Given a search query is submitted with a typo (e.g., minor misspelling) on the
        search_results/transferring_body/<body_id> page
        When the results are displayed
        Then the results should use fuzziness logic to account for the typo and display relevant matches
        """
        url = f"{self.transferring_body_search_url}?query=a#browse-records"

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

    def test_exact_consignment_ref_returns_results(
        self, standard_user_page: Page
    ):
        """
        Integration test verifying that exact consignment reference matches return results.
        """
        url = f"{self.transferring_body_search_url}?query=TDR-2023-GXFH&search_area=everywhere#browse-records"
        standard_user_page.goto(url)
        row_count = _check_row_count(standard_user_page)
        assert row_count > 0, "Expected results for exact consignment reference"

        # Verify the consignment reference appears in the results
        tbody_locator = standard_user_page.locator("tbody.govuk-table__body")
        inner_html = tbody_locator.inner_html()
        assert (
            "TDR-2023-GXFH" in inner_html
        ), "Consignment reference should appear in results"

    def test_fuzzy_consignment_ref_returns_no_results(
        self, standard_user_page: Page
    ):
        """
        Integration test verifying that fuzzy/typo consignment reference matches return no results.
        """
        url = f"{self.transferring_body_search_url}?query=TDR-2023-GXFG&search_area=everywhere#browse-records"
        standard_user_page.goto(url)
        row_count = _check_row_count(standard_user_page)
        assert (
            row_count == 0
        ), "Expected no results for fuzzy consignment reference match"

    def test_fuzzy_fields_still_work(self, standard_user_page: Page):
        """
        Integration test verifying that fuzzy matching still works for appropriate fields.
        Ensures we didn't break fuzzy matching entirely when disabling it for specific fields.
        """
        url = f"{self.transferring_body_search_url}?query=fil&search_area=everywhere#browse-records"
        standard_user_page.goto(url)
        row_count = _check_row_count(standard_user_page)
        assert (
            row_count > 0
        ), "Expected results for fuzzy matching on content fields"

        # Verify fuzzy matching highlighted results
        tbody_locator = standard_user_page.locator("tbody.govuk-table__body")
        inner_html = tbody_locator.inner_html()
        assert (
            "<mark>file</mark>" in inner_html
        ), "Expected fuzzy matching to highlight 'file' for query 'fil'"

    def test_minimum_should_match_prevents_returning_all_results(
        self, standard_user_page: Page
    ):
        """
        Integration test verifying that minimum_should_match prevents returning all files
        when search terms don't match anything.
        """
        # Test with completely nonsense terms that shouldn't match anything
        url = (
            f"{self.transferring_body_search_url}?"
            "query=xyzabcnonexistentterms123&search_area=everywhere#browse-records"
        )

        standard_user_page.goto(url)
        row_count = _check_row_count(standard_user_page)

        # Should find no results due to minimum_should_match requirement
        assert row_count == 0, "Expected no results for nonsense query terms"
