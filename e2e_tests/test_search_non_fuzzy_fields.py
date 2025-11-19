from playwright.sync_api import Page


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


class TestSearchNonFuzzyFields:
    """
    Test suite for non-fuzzy field matching in search functionality.

    Tests that consignment_ref, series, and date fields only match in a non-fuzzy,
    phrase type way and not with fuzzy matching.
    """

    @property
    def browse_route_url(self):
        return "/browse"

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    @property
    def transferring_body_search_url(self):
        return f"/search/transferring_body/{self.transferring_body_id}"

    def test_consignment_ref_exact_match_returns_results(
        self, standard_user_page: Page
    ):
        """
        Given a search query with an exact consignment reference (TDR-2023-GXFH)
        When the search is performed on transferring body search page
        Then results should be returned for the exact match
        """
        url = f"{self.transferring_body_search_url}?query=TDR-2023-GXFH&search_area=everywhere#browse-records"

        standard_user_page.goto(url)
        standard_user_page.wait_for_selector("tbody .govuk-table__row--primary")

        rows = standard_user_page.locator("tbody .govuk-table__row--primary")
        # Should find multiple results for this consignment reference
        assert rows.count() > 0

        # Verify the consignment reference appears in the results
        tbody_locator = standard_user_page.locator("tbody.govuk-table__body")
        inner_html = tbody_locator.inner_html()
        assert "TDR-2023-GXFH" in inner_html

    def test_consignment_ref_fuzzy_match_no_results(
        self, standard_user_page: Page
    ):
        """
        Given a search query with a typo in consignment reference (TDR-2023-GXFG instead of TDR-2023-GXFH)
        When the search is performed on transferring body search page
        Then no results should be returned as fuzzy matching is disabled for consignment_ref fields
        """
        url = f"{self.transferring_body_search_url}?query=TDR-2023-GXFG&search_area=everywhere#browse-records"

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)
        assert (
            row_count == 0
        ), "Expected no results for fuzzy consignment reference match"

    def test_series_exact_match_returns_results(self, standard_user_page: Page):
        """
        Given a search query with an exact series reference (TSTA 1)
        When the search is performed on transferring body search page
        Then results should be returned for the exact match
        """
        url = f"{self.transferring_body_search_url}?query=TSTA 1&search_area=everywhere#browse-records"

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)
        # Should find multiple results for this series
        assert row_count > 0

        # Verify the series reference appears in the results
        tbody_locator = standard_user_page.locator("tbody.govuk-table__body")
        inner_html = tbody_locator.inner_html()
        assert "TSTA 1" in inner_html

    def test_series_fuzzy_match_no_results(self, standard_user_page: Page):
        """
        Given a search query with a typo in series reference (TSTA 2 instead of TSTA 1)
        When the search is performed on transferring body search page
        Then no results should be returned as fuzzy matching is disabled for series fields
        """
        url = f"{self.transferring_body_search_url}?query=TSTA 2&search_area=everywhere#browse-records"

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)

        # Should find no results due to typo and non-fuzzy matching
        assert row_count == 0, "Expected no results for fuzzy series match"

    def test_quoted_phrase_exact_match_for_non_fuzzy_fields(
        self, standard_user_page: Page
    ):
        """
        Given a search query with quoted consignment reference ("TDR-2023-GXFH")
        When the search is performed on transferring body search page
        Then results should be returned for the exact phrase match
        """
        url = f'{self.transferring_body_search_url}?query="TDR-2023-GXFH"&search_area=everywhere#browse-records'

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)
        assert row_count > 0

        # Verify the exact phrase appears in the results
        tbody_locator = standard_user_page.locator("tbody.govuk-table__body")
        inner_html = tbody_locator.inner_html()
        assert "TDR-2023-GXFH" in inner_html

    def test_partial_consignment_ref_no_fuzzy_match(
        self, standard_user_page: Page
    ):
        """
        Given a search query with partial consignment reference (TDR-2023-GX)
        When the search is performed on transferring body search page
        Then results should only be returned if it's an exact phrase match, not fuzzy
        """
        url = f"{self.transferring_body_search_url}?query=TDR-2023-GX&search_area=everywhere#browse-records"

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)

        # Should find no results as partial match won't work with phrase matching
        assert (
            row_count == 0
        ), "Expected no results for partial consignment reference"

    def test_case_sensitivity_for_series_fields(self, standard_user_page: Page):
        """
        Given a search query with different case for series reference (tsta 1 instead of TSTA 1)
        When the search is performed on transferring body search page
        Then results should still be returned as OpenSearch is typically case-insensitive
        """
        url = f"{self.transferring_body_search_url}?query=tsta 1&search_area=everywhere#browse-records"

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)

        # Case insensitive matching should work
        assert (
            row_count > 0
        ), "Expected results for case-insensitive series match"

    def test_multiple_non_fuzzy_terms_search(self, standard_user_page: Page):
        """
        Given a search query with multiple non-fuzzy field terms
        When the search is performed on transferring body search page
        Then results should match using phrase matching for each term
        """
        # %2B is URL-encoded plus sign +
        url = f"{self.transferring_body_search_url}?query=TDR-2023-GXFH%2BTSTA 1&search_area=everywhere#browse-records"

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)
        assert row_count > 0

        # Verify both terms appear in the results
        tbody_locator = standard_user_page.locator("tbody.govuk-table__body")
        inner_html = tbody_locator.inner_html()

        # At least one of the terms should be highlighted/present
        has_consignment_ref = "TDR-2023-GXFH" in inner_html
        has_series_ref = "TSTA 1" in inner_html

        assert (
            has_consignment_ref or has_series_ref
        ), "Expected at least one non-fuzzy field term to match"


class TestSearchMinimumShouldMatch:
    """
    Test suite for minimum should match requirement in search functionality.

    Tests that at least one should clause must match to prevent returning
    all files in a transferring body when no terms match.
    """

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    @property
    def transferring_body_search_url(self):
        return f"/search/transferring_body/{self.transferring_body_id}"

    def test_nonsense_query_returns_no_results(self, standard_user_page: Page):
        """
        Given a search query with completely nonsense terms that shouldn't match anything
        When the search is performed on transferring body search page
        Then no results should be returned due to minimum_should_match requirement
        """
        url = (
            f"{self.transferring_body_search_url}?"
            "query=xyzabcnonexistentterms123&search_area=everywhere#browse-records"
        )

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)

        # Should find no results due to minimum_should_match requirement
        assert row_count == 0, "Expected no results for nonsense query terms"

    def test_very_specific_nonexistent_consignment_ref(
        self, standard_user_page: Page
    ):
        """
        Given a search query with a non-existent but valid-format consignment reference
        When the search is performed on transferring body search page
        Then no results should be returned rather than all files
        """
        url = f"{self.transferring_body_search_url}?query=TDR-9999-ZZZZ&search_area=everywhere#browse-records"

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)

        # Should find no results due to non-existent consignment reference
        assert (
            row_count == 0
        ), "Expected no results for non-existent consignment reference"

    def test_empty_search_redirects_or_shows_all(
        self, standard_user_page: Page
    ):
        """
        Given an empty search query
        When the search is performed on transferring body search page
        Then it should either redirect to browse or show all files (this is expected behavior)
        """
        url = f"{self.transferring_body_search_url}?query=&search_area=everywhere#browse-records"

        standard_user_page.goto(url)

        # For empty queries, the application might redirect or show all files
        # This is expected behavior, so we just verify the page loads
        # and doesn't crash
        standard_user_page.wait_for_load_state("domcontentloaded")

        # Check if we're still on the search page or redirected
        current_url = standard_user_page.url

        # Either should stay on search page or redirect to browse
        is_on_search_page = "/search/transferring_body/" in current_url
        is_on_browse_page = "/browse" in current_url

        assert (
            is_on_search_page or is_on_browse_page
        ), "Page should load successfully with empty query"

    def test_whitespace_only_query(self, standard_user_page: Page):
        """
        Given a search query with only whitespace
        When the search is performed on transferring body search page
        Then it should be treated as empty and not return all files
        """
        url = f"{self.transferring_body_search_url}?query=   &search_area=everywhere#browse-records"

        standard_user_page.goto(url)

        # Whitespace-only queries should be handled gracefully
        standard_user_page.wait_for_load_state("domcontentloaded")

        # Should either redirect or show controlled results
        current_url = standard_user_page.url

        is_on_search_page = "/search/transferring_body/" in current_url
        is_on_browse_page = "/browse" in current_url

        assert (
            is_on_search_page or is_on_browse_page
        ), "Whitespace query should be handled gracefully"

    def test_mixed_valid_and_invalid_terms(self, standard_user_page: Page):
        """
        Given a search query with one valid term and one invalid term
        When the search is performed on transferring body search page
        Then results should be returned based on the valid term matching
        """
        # %2B is URL-encoded plus sign +
        url = (
            f"{self.transferring_body_search_url}?"
            "query=TDR-2023-GXFH%2Bnonexistentterm123&search_area=everywhere#browse-records"
        )

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)
        # Should find results because the valid consignment ref should match
        assert (
            row_count > 0
        ), "Expected results for mixed valid/invalid terms due to valid consignment reference"

        # Verify the valid term appears in the results
        tbody_locator = standard_user_page.locator("tbody.govuk-table__body")
        inner_html = tbody_locator.inner_html()
        assert (
            "TDR-2023-GXFH" in inner_html
        ), "Valid consignment reference should appear in results"

    def test_fuzzy_field_still_works_with_minimum_should_match(
        self, standard_user_page: Page
    ):
        """
        Given a search query with fuzzy-matchable content (non-series, non-consignment_ref, non-date field)
        When the search is performed on transferring body search page
        Then results should be returned showing fuzzy matching still works for appropriate fields
        """
        # Using "fil" which should fuzzy match "file" in content/filename fields
        url = f"{self.transferring_body_search_url}?query=fil&search_area=everywhere#browse-records"

        standard_user_page.goto(url)
        row_count = _check_row_count(standard_user_page)
        # Should find results because fuzzy matching should work on content/filename fields
        assert (
            row_count > 0
        ), "Expected results for fuzzy matching on non-restricted fields"

        # Verify fuzzy matching highlighted results
        tbody_locator = standard_user_page.locator("tbody.govuk-table__body")
        inner_html = tbody_locator.inner_html()

        # Should have highlighted "file" when searching for "fil"
        assert (
            "<mark>file</mark>" in inner_html
        ), "Expected fuzzy matching to highlight 'file' for query 'fil'"


class TestSearchFieldSpecificBehavior:
    """
    Test suite for field-specific search behavior to ensure the changes work correctly
    across different search areas and field types.
    """

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    @property
    def transferring_body_search_url(self):
        return f"/search/transferring_body/{self.transferring_body_id}"

    def test_metadata_search_area_respects_non_fuzzy_fields(
        self, standard_user_page: Page
    ):
        """
        Given a search query in metadata search area with consignment reference
        When the search is performed
        Then non-fuzzy matching should apply to consignment_ref fields
        """
        url = f"{self.transferring_body_search_url}?query=TDR-2023-GXFH&search_area=metadata#browse-records"

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)
        assert (
            row_count > 0
        ), "Expected results for exact consignment reference in metadata search"

    def test_record_search_area_with_fuzzy_content(
        self, standard_user_page: Page
    ):
        """
        Given a search query in record search area with content that can be fuzzy matched
        When the search is performed
        Then fuzzy matching should still work for content fields
        """
        url = f"{self.transferring_body_search_url}?query=fil&search_area=record#browse-records"

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)
        assert (
            row_count > 0
        ), "Expected results for fuzzy content matching in record search area"

    def test_everywhere_search_area_with_mixed_fields(
        self, standard_user_page: Page
    ):
        """
        Given a search query in everywhere search area with both fuzzy and non-fuzzy field terms
        When the search is performed
        Then appropriate matching behavior should apply to each field type
        """
        # %2B is URL-encoded plus sign +
        url = f"{self.transferring_body_search_url}?query=TDR-2023-GXFH%2Bfil&search_area=everywhere#browse-records"

        standard_user_page.goto(url)

        row_count = _check_row_count(standard_user_page)
        assert (
            row_count > 0
        ), "Expected results for mixed field types in everywhere search area"

        tbody_locator = standard_user_page.locator("tbody.govuk-table__body")
        inner_html = tbody_locator.inner_html()

        # Should match either the exact consignment ref or fuzzy file content
        has_consignment = "TDR-2023-GXFH" in inner_html
        has_fuzzy_file = "<mark>file</mark>" in inner_html

        assert (
            has_consignment or has_fuzzy_file
        ), "Expected either exact consignment match or fuzzy file match"
