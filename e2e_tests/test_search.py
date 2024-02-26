from playwright.sync_api import Page, expect


class TestSearchResultsSummary:
    @property
    def route_url(self):
        return "/search_results_summary"

    def test_search_results_summary_sorting(self, authenticated_page: Page):
        """
        Given a standard user on the search page
        When they interact with the search form and submit a query
        Then the table should contain the expected headers and entries
        and sorted transferring body in alphabetic order (A to Z)
        on a search results summary screen
        """
        authenticated_page.goto(f"{self.route_url}?query=")
        authenticated_page.get_by_label("", exact=True).click()
        authenticated_page.get_by_label("", exact=True).fill("dtp")
        authenticated_page.get_by_role("button", name="Search").click()

        table = authenticated_page.locator("table")

        # Use JavaScript to extract the text of header elements (th) within the table
        header_texts = table.evaluate(
            '(table) => Array.from(table.querySelectorAll("th")).map(th => th.textContent)'
        )
        # List of expected header values
        expected_headers = [
            "Results found within each Transferring body",
            "Records found",
        ]
        for expected_header in expected_headers:
            assert expected_header in header_texts

        # Use JavaScript to extract the text of table cell elements (td) within the table
        cell_texts = table.evaluate(
            '(table) => Array.from(table.querySelectorAll("td")).map(td => td.textContent)'
        )

        expected_entries = [
            "Testing A",
            "132",
        ]
        assert expected_entries == cell_texts


def verify_search_transferring_body_header_row(table):
    # Use JavaScript to extract the text of header elements (th) within the table
    header_texts = table.evaluate(
        '(table) => Array.from(table.querySelectorAll("th")).map(th => th.textContent)'
    )
    # List of expected header values
    expected_headers = [
        "Series",
        "Consignment reference",
        "Title",
        "Status",
        "Record opening",
    ]
    for expected_header in expected_headers:
        assert expected_header in header_texts


def verify_search_data_rows(table):
    # Use JavaScript to extract the text of table cell elements (td) within the table
    cell_texts = table.evaluate(
        '(table) => Array.from(table.querySelectorAll("td")).map(td => td.textContent)'
    )

    expected_entries = [
        "TSTA 1",
        "TDR-2024-H5DN",
        "DTP.docx",
        "Open",
        "-",
        "TSTA 1",
        "TDR-2024-H5DN",
        "DTP_ Sensitivity review process.docx",
        "Open",
        "-",
        "TSTA 1",
        "TDR-2024-H5DN",
        "DTP_ Digital Transfer process diagram UG.docx",
        "Open",
        "-",
        "TSTA 1",
        "TDR-2024-H5DN",
        "DTP_ Digital Transfer process diagram v 6.docx",
        "Open",
        "-",
        "TSTA 1",
        "TDR-2023-TMT",
        "DTP_ Sensitivity review process.docx",
        "Open",
        "-",
    ]
    assert expected_entries == cell_texts


class TestSearchTransferringBody:
    @property
    def route_url(self):
        return "/search/transferring_body"

    @property
    def transferring_body_id(self):
        return "c969a99f-dd61-4890-a8b4-6556d5d69915"

    def test_search_transferring_body_sorting(self, authenticated_page: Page):
        """
        Given a standard user on the search page
        When they interact with the search form and submit a query
        Then the table should contain the expected headers and entries
        and sort the results based on the sorting order selection from dropdown list
        on a search transferring body screen
        """
        authenticated_page.goto(
            f"{self.route_url}/{self.transferring_body_id}?query="
        )
        authenticated_page.fill("#searchInput", "dtp")
        authenticated_page.get_by_role("button").get_by_text("Search").click()
        authenticated_page.get_by_label("Sort by").select_option(
            "consignment_reference-desc"
        )
        authenticated_page.get_by_role("button", name="Apply").click()

        table = authenticated_page.locator("table")

        verify_search_transferring_body_header_row(table)
        verify_search_data_rows(table)

    def test_search_transferring_body_end_to_end(
        self, authenticated_page: Page
    ):
        """
        Given a user on the search page
        When they interact with the search form and submit a query
        Then the table should contain the expected headers and entries.
        """
        authenticated_page.goto(
            f"{self.route_url}/{self.transferring_body_id}?query="
        )
        authenticated_page.fill("#searchInput", "dtp")
        authenticated_page.get_by_role("button").get_by_text("Search").click()

        expect(
            authenticated_page.locator("text=Search for digital records")
        ).to_be_visible()
        expect(authenticated_page.locator("#searchInput")).to_have_value("dtp")

        table = authenticated_page.locator("table")

        verify_search_transferring_body_header_row(table)
        verify_search_data_rows(table)

    def test_search_transferring_body_pagination_available(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/{self.transferring_body_id}?query="
        )
        authenticated_page.fill("#searchInput", "dtp")
        authenticated_page.get_by_role("button").get_by_text("Search").click()
        assert (
            authenticated_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )

    def test_search_transferring_body_pagination_check_only_one_page_returned(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/{self.transferring_body_id}?query="
        )
        authenticated_page.fill("#searchInput", "dtp")
        authenticated_page.get_by_role("button").get_by_text("Search").click()

        pagination_element = authenticated_page.query_selector(
            "nav.govuk-pagination"
        )
        assert not pagination_element

    def test_search_transferring_body_pagination_get_first_page(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/{self.transferring_body_id}?query="
        )
        authenticated_page.fill("#searchInput", "dtp")
        authenticated_page.get_by_role("button").get_by_text("Search").click()

        assert (
            authenticated_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        url = "/search?page=1&query=testing+a"
        assert (
            authenticated_page.locator(
                ".govuk-pagination__link"
            ).first.get_attribute("href")
            == url
        )
        links = authenticated_page.locator(
            ".govuk-pagination__link-title"
        ).all()
        assert links[0].inner_text() == "Nextpage"
        expect(authenticated_page.get_by_text("Records found 5"))
        rows = authenticated_page.locator(".govuk-table__row").all()
        assert len(rows) == 6  # including header row

    def test_search_transferring_body_pagination_get_previous_page(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/{self.transferring_body_id}?query="
        )
        authenticated_page.fill("#searchInput", "dtp")
        authenticated_page.get_by_role("button").get_by_text("Search").click()

        page_links = authenticated_page.locator(".govuk-pagination__link").all()
        authenticated_page.get_by_role("link").get_by_text(
            page_links[1].inner_text()
        ).click()
        assert (
            authenticated_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        links = authenticated_page.locator(
            ".govuk-pagination__link-title"
        ).all()
        assert links[0].inner_text() == "Previouspage"

    def test_search_transferring_body_pagination_get_next_page(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/{self.transferring_body_id}?query="
        )
        authenticated_page.fill("#searchInput", "dtp")
        authenticated_page.get_by_role("button").get_by_text("Search").click()

        assert (
            authenticated_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        url = "/search?page=1&query=testing+a"
        assert (
            authenticated_page.locator(
                ".govuk-pagination__link"
            ).first.get_attribute("href")
            == url
        )
        authenticated_page.get_by_role("link").get_by_text(" 2 ").click()
        links = authenticated_page.locator(
            ".govuk-pagination__link-title"
        ).all()
        assert links[0].inner_text() == "Previouspage"
        if len(links) > 1:
            assert links[1].inner_text() == "Nextpage"

    def test_search_transferring_body_pagination_get_ellipses_page(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/{self.transferring_body_id}?query="
        )
        authenticated_page.fill("#searchInput", "dtp")
        authenticated_page.get_by_role("button").get_by_text("Search").click()

        assert (
            authenticated_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        page_links = authenticated_page.locator(".govuk-pagination__link").all()
        last_page = page_links[len(page_links) - 1].inner_text()
        assert page_links[0].inner_text() == "1"
        assert page_links[1].inner_text() == "2"
        assert page_links[3].inner_text() == last_page
        ellipsis_link = authenticated_page.locator(
            ".govuk-pagination__item--ellipses"
        ).all()
        assert ellipsis_link[0].inner_text() == "…"
        links = authenticated_page.locator(
            ".govuk-pagination__link-title"
        ).all()
        assert links[0].inner_text() == "Nextpage"

    def test_search_transferring_body_pagination_click_previous_link(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/{self.transferring_body_id}?query="
        )
        authenticated_page.fill("#searchInput", "dtp")
        authenticated_page.get_by_role("button").get_by_text("Search").click()

        assert (
            authenticated_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )

        authenticated_page.get_by_role("link").get_by_text(" 2 ").click()

        links = authenticated_page.locator(
            ".govuk-pagination__link-title"
        ).all()
        assert links[0].inner_text() == "Previouspage"

        url = "/search?page=1&query=testing+a"
        authenticated_page.expect_response(url)

    def test_search_transferring_body_pagination_click_next_link(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/{self.transferring_body_id}?query="
        )
        authenticated_page.fill("#searchInput", "dtp")
        authenticated_page.get_by_role("button").get_by_text("Search").click()

        assert (
            authenticated_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )

        authenticated_page.get_by_role("link").get_by_text(" 1 ").click()

        links = authenticated_page.locator(
            ".govuk-pagination__link-title"
        ).all()
        assert links[0].inner_text() == "Nextpage"

        url = "/search?page=2&query=testing+a"
        authenticated_page.expect_response(url)

    def test_search_transferring_body_pagination_get_last_page(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/{self.transferring_body_id}?query="
        )
        authenticated_page.fill("#searchInput", "dtp")
        authenticated_page.get_by_role("button").get_by_text("Search").click()

        assert (
            authenticated_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        page_links = authenticated_page.locator(".govuk-pagination__link").all()
        last_page = page_links[len(page_links) - 1].inner_text()
        authenticated_page.get_by_role("link").get_by_text(last_page).click()
        links = authenticated_page.locator(
            ".govuk-pagination__link-title"
        ).all()
        assert links[0].inner_text() == "Previouspage"
