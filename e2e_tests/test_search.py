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


class TestSearchResultsSummary:
    @property
    def browse_route_url(self):
        return "/browse"

    def test_search_results_summary_search_single_term(
        self, aau_user_page: Page, utils
    ):
        """
        Given a standard user on the search page
        When they interact with the search form and submit a query with single search term
        Then the table should contain the expected headers and entries
        and sorted transferring bodies in alphabetic order (A to Z)
        on a search results summary screen
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("dtp")
        aau_user_page.get_by_role("button", name="Search").click()

        aau_user_page.wait_for_selector("#tbl_result")

        header_rows = utils.get_page_table_headers(aau_user_page)
        rows = utils.get_page_table_rows(aau_user_page)

        expected_rows = [["Mock 1 Department", "16"], ["Testing A", "12"]]

        verify_search_results_summary_header_row(header_rows)
        assert rows == expected_rows

    def test_search_results_summary_search_multiple_terms(
        self, aau_user_page: Page, utils
    ):
        """
        Given a standard user on the search page
        When they interact with the search form and submit a query with multiple search terms
        Then the table should contain the expected headers and entries
        and sorted transferring bodies in alphabetic order (A to Z)
        on a search results summary screen
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("dtp,tdr-2023-tmt")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.wait_for_selector("#tbl_result")

        header_rows = utils.get_page_table_headers(aau_user_page)
        rows = utils.get_page_table_rows(aau_user_page)

        expected_rows = [["Testing A", "4"]]

        verify_search_results_summary_header_row(header_rows)
        assert rows == expected_rows


class TestSearchTransferringBody:
    @property
    def route_url(self):
        return "/search/transferring_body"

    @property
    def browse_route_url(self):
        return "/browse"

    @property
    def browse_transferring_body_route_url(self):
        return "/browse/transferring_body"

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    def test_search_transferring_body_search_single_term(
        self, aau_user_page: Page, utils
    ):
        """
        Given a standard user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        Then the table should contain the expected headers and entries
        and sort the results based on the sorting order selection from dropdown list
        on a search transferring body screen
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("dtp")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()

        header_rows = utils.get_page_table_headers(aau_user_page)
        rows = utils.get_page_table_rows(aau_user_page)

        expected_rows = [
            [
                "TSTA 1",
                "TDR-2023-TH4",
                "DTP_ Digital Transfer process diagram UG.docx",
                "Open",
                "–",
            ],
            [
                "TSTA 1",
                "TDR-2023-TH4",
                "DTP_ Digital Transfer process diagram v 6.docx",
                "Open",
                "–",
            ],
            ["TSTA 1", "TDR-2023-TH4", "DTP.docx", "Open", "–"],
            [
                "TSTA 1",
                "TDR-2023-TH4",
                "DTP_ Sensitivity review process.docx",
                "Open",
                "–",
            ],
            [
                "TSTA 1",
                "TDR-2023-TMT",
                "DTP_ Digital Transfer process diagram UG.docx",
                "Open",
                "–",
            ],
        ]

        verify_search_transferring_body_header_row(header_rows)

        assert rows == expected_rows

    def test_search_transferring_body_search_multiple_terms(
        self, aau_user_page: Page, utils
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with multiple search terms
        Then the table should contain the expected headers and entries.
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("dtp,tdr-2023-tmt")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()

        header_rows = utils.get_page_table_headers(aau_user_page)
        rows = utils.get_page_table_rows(aau_user_page)

        expected_rows = [
            [
                "TSTA 1",
                "TDR-2023-TMT",
                "DTP_ Digital Transfer process diagram UG.docx",
                "Open",
                "–",
            ],
            [
                "TSTA 1",
                "TDR-2023-TMT",
                "DTP_ Digital Transfer process diagram v 6.docx",
                "Open",
                "–",
            ],
            ["TSTA 1", "TDR-2023-TMT", "DTP.docx", "Open", "–"],
            [
                "TSTA 1",
                "TDR-2023-TMT",
                "DTP_ Sensitivity review process.docx",
                "Open",
                "–",
            ],
        ]

        verify_search_transferring_body_header_row(header_rows)
        assert rows == expected_rows

    def test_search_transferring_body_remove_all_terms_redirect_to_browse_transferring_body(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with a search term
        and then remove the search term
        Then they should be redirected to browse transferring body page.
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("dtp")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.get_by_role("link", name="dtp", exact=True).click()

        url = f"{self.browse_transferring_body_route_url}/{self.transferring_body_id}"
        expect(aau_user_page).to_have_url(url)

    def test_search_transferring_body_aau_user_and_click_on_clear_all(
        self, aau_user_page: Page
    ):
        """
        Given an all access user on the search transferring body page
        When they interact with the search form and submit a query with multiple search terms
        and the click on clear all option
        Then they should be redirected to browse all page.
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("dtp,tdr-2023-tmt")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.get_by_role("link", name="Clear all").click()

        expect(aau_user_page).to_have_url(
            f"{self.browse_route_url}#browse-records"
        )

    def test_search_transferring_body_standard_user_and_click_on_clear_all(
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
        standard_user_page.locator("#search-input").fill("dtp,tdr-2023-tmt")
        standard_user_page.get_by_role("button", name="Search").click()
        standard_user_page.get_by_role("link", name="Clear all").click()

        expect(standard_user_page).to_have_url(url)

    def test_search_transferring_body_pagination_check_only_one_page_returned(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        Then the table should contain the expected headers and entries
        and return only one page without pagination object
        """

        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("closed_file_r")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()

        pagination_element = aau_user_page.query_selector(
            "nav.govuk-pagination"
        )
        assert not pagination_element

    def test_search_transferring_body_pagination_available(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        Then the table should contain the expected headers and entries and pagination object
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.wait_for_selector(".govuk-pagination")

        assert (
            aau_user_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )

    def test_search_transferring_body_pagination_get_first_page(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        Then the table should contain the expected headers and entries and pagination object
        with first page link available
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.wait_for_selector(".govuk-pagination")

        assert (
            aau_user_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        url = f" {self.route_url}/{self.transferring_body_id}?page=1&query=a "

        assert (
            aau_user_page.locator(
                "data-testid=pagination-link"
            ).first.get_attribute("href")
            == url
        )
        links = aau_user_page.locator("data-testid=pagination-link-title").all()
        assert links[0].text_content() == "Nextpage"

    def test_search_transferring_body_pagination_get_previous_page(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        and click on page 2 link
        Then the table should contain the expected headers and entries and pagination object
        with previous page link
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.get_by_label("Page 2").click()
        aau_user_page.wait_for_selector(".govuk-pagination")

        assert (
            aau_user_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        links = aau_user_page.locator("data-testid=pagination-link-title").all()

        assert links[0].text_content() == "Previouspage"

    def test_search_transferring_body_pagination_get_next_page(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        and click on page 2 link
        Then the table should contain the expected headers and entries and pagination object
        with previous and next page link
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.wait_for_selector(".govuk-pagination")

        assert (
            aau_user_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        url = f" {self.route_url}/{self.transferring_body_id}?page=1&query=a "
        assert (
            aau_user_page.locator(
                "data-testid=pagination-link"
            ).first.get_attribute("href")
            == url
        )
        aau_user_page.get_by_label("Page 2").click()
        links = aau_user_page.locator("data-testid=pagination-link-title").all()
        assert links[0].text_content() == "Previouspage"
        if len(links) > 1:
            assert links[1].text_content() == "Nextpage"

    def test_search_transferring_body_pagination_get_ellipses_page(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        Then the table should contain the expected headers and entries and pagination object
        with ellipses page link
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.wait_for_selector(".govuk-pagination")

        assert (
            aau_user_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        page_links = aau_user_page.locator("data-testid=pagination-link").all()
        last_page = page_links[len(page_links) - 1].text_content()

        assert page_links[0].inner_text() == "1"
        assert page_links[1].inner_text() == "2"
        assert page_links[3].text_content() == last_page
        ellipsis_link = aau_user_page.locator(
            ".govuk-pagination__item--ellipses"
        ).all()
        assert ellipsis_link[0].inner_text() == "…"
        links = aau_user_page.locator("data-testid=pagination-link-title").all()
        assert links[0].text_content() == "Nextpage"

    def test_search_transferring_body_pagination_click_previous_page_link(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        and click on page 2 link
        Then the table should contain the expected headers and entries and pagination object
        and expected page 1 response
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.wait_for_selector(".govuk-pagination")

        assert (
            aau_user_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )

        aau_user_page.get_by_label("Page 2").click()

        links = aau_user_page.locator("data-testid=pagination-link-title").all()

        assert links[0].text_content() == "Previouspage"

        aau_user_page.get_by_label("Page 1", exact=True).click()

        url = f"{self.route_url}/{self.transferring_body_id}?page=1&query=a"
        expect(aau_user_page).to_have_url(url)

    def test_search_transferring_body_pagination_click_next_page_link(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        and click on page 2 link
        Then the table should contain the expected headers and entries and pagination object
        and expected page 3 response
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.wait_for_selector(".govuk-pagination")

        assert (
            aau_user_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )

        aau_user_page.get_by_label("Page 2", exact=True).click()

        aau_user_page.wait_for_selector(".govuk-pagination")

        links = aau_user_page.locator("data-testid=pagination-link-title").all()

        assert links[1].text_content() == "Nextpage"

        aau_user_page.get_by_label("Page 3", exact=True).click()

        aau_user_page.wait_for_selector(".govuk-pagination")

        url = f"{self.route_url}/{self.transferring_body_id}?page=3&query=a"
        expect(aau_user_page).to_have_url(url)

    def test_search_transferring_body_pagination_get_last_page(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        and click on last page
        Then the table should contain the expected headers and entries and pagination object
        with previous page link
        """

        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.wait_for_selector(".govuk-pagination")

        assert (
            aau_user_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        page_links = aau_user_page.locator("data-testid=pagination-link").all()
        last_page = page_links[len(page_links) - 1].text_content()
        aau_user_page.get_by_role("link").get_by_text(last_page).click()
        links = aau_user_page.locator("data-testid=pagination-link-title").all()
        assert links[0].text_content() == "Previouspage"
