from playwright.sync_api import Page


def verify_header_row(header_rows):
    assert header_rows[0] == [
        "Transferring body",
        "Series",
        "Last consignment transferred",
        "Records held in series",
        "Consignments within series",
    ]


class TestBrowse:
    @property
    def route_url(self):
        return "/browse"

    def test_has_title(self, aau_user_page: Page):
        aau_user_page.goto(f"{self.route_url}")

        assert (
            aau_user_page.title()
            == "Browse – AYR - Access Your Records – GOV.UK"
        )

    def test_browse_filter_functionality_with_query_string_parameters(
        self, aau_user_page: Page
    ):
        aau_user_page.goto(
            f"{self.route_url}?transferring_body_filter=all&series_filter=&date_from_day"
            "01=&date_from_month=07&date_from_year=2023&date_to_day=31&date_to_month=07&date_to_year=2023"
        )

        header_rows = aau_user_page.locator(
            "#tbl_result tr:visible"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('th')].map(e => e.textContent.trim())
            )"""
        )

        rows = aau_user_page.locator("#tbl_result tr:visible").evaluate_all(
            """els => els.slice(1).map(el =>
              [...el.querySelectorAll('td')].map(e => e.textContent.trim())
            )"""
        )

        assert len(rows) == 1

        expected_rows = [
            ["MOCK1 Department", "MOCK1 123", "28/07/2023", "1", "1"]
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_no_results_returned(self, aau_user_page: Page):
        aau_user_page.locator("#series_filter").click()
        aau_user_page.locator("#series_filter").fill("junk")
        aau_user_page.get_by_role("button", name="Apply filters").click()

        assert aau_user_page.inner_html("text='No results found'")
        assert aau_user_page.inner_html("text='Help with your search'")
        assert aau_user_page.inner_html(
            "text='Try changing or removing one or more applied filters.'"
        )
        assert aau_user_page.inner_html(
            "text='Alternatively, use the breadcrumbs to navigate back to the browse view.'"
        )

    def test_browse_breadcrumb(self, aau_user_page: Page):
        aau_user_page.goto(f"{self.route_url}")

        assert aau_user_page.inner_html("text='You are viewing'")
        assert aau_user_page.inner_html("text='Everything available to you'")

    def test_browse_sort_functionality_by_transferring_body_descending(
        self, aau_user_page: Page
    ):
        aau_user_page.get_by_label("Sort by").select_option(
            "transferring_body-desc"
        )
        aau_user_page.get_by_role("button", name="Apply", exact=True).click()

        header_rows = aau_user_page.locator(
            "#tbl_result tr:visible"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('th')].map(e => e.textContent.trim())
            )"""
        )

        rows = aau_user_page.locator("#tbl_result tr:visible").evaluate_all(
            """els => els.slice(1).map(el =>
              [...el.querySelectorAll('td')].map(e => e.textContent.trim())
            )"""
        )

        assert len(rows) == 2

        expected_rows = [
            ["Testing A", "TSTA 1", "25/01/2024", "73", "7"],
            ["MOCK1 Department", "MOCK1 123", "28/07/2023", "1", "1"],
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_filter_functionality_with_transferring_body_filter(
        self, aau_user_page: Page
    ):
        aau_user_page.locator("#transferring_body_filter").select_option(
            "MOCK1 Department"
        )
        aau_user_page.get_by_role("button", name="Apply filters").click()
        aau_user_page.get_by_label("Sort by").select_option(
            "last_record_transferred-desc"
        )
        aau_user_page.get_by_role("button", name="Apply", exact=True).click()

        header_rows = aau_user_page.locator(
            "#tbl_result tr:visible"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('th')].map(e => e.textContent.trim())
            )"""
        )

        rows = aau_user_page.locator("#tbl_result tr:visible").evaluate_all(
            """els => els.slice(1).map(el =>
              [...el.querySelectorAll('td')].map(e => e.textContent.trim())
            )"""
        )

        assert len(rows) == 1

        expected_rows = [
            ["MOCK1 Department", "MOCK1 123", "28/07/2023", "1", "1"]
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_filter_functionality_with_series_filter_wildcard_character(
        self, aau_user_page: Page
    ):
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.locator("#series_filter").fill("1")
        aau_user_page.get_by_role("button", name="Apply filters").click()

        header_rows = aau_user_page.locator(
            "#tbl_result tr:visible"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('th')].map(e => e.textContent.trim())
            )"""
        )

        rows = aau_user_page.locator("#tbl_result tr:visible").evaluate_all(
            """els => els.slice(1).map(el =>
              [...el.querySelectorAll('td')].map(e => e.textContent.trim())
            )"""
        )

        assert len(rows) == 2

        expected_rows = [
            ["MOCK1 Department", "MOCK1 123", "28/07/2023", "1", "1"],
            ["Testing A", "TSTA 1", "25/01/2024", "73", "7"],
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_filter_functionality_with_date_filter(
        self, aau_user_page: Page
    ):
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.locator("#date_from_day").fill("1")
        aau_user_page.locator("#date_from_month").fill("1")
        aau_user_page.locator("#date_from_year").fill("2024")
        aau_user_page.get_by_role("button", name="Apply filters").click()

        header_rows = aau_user_page.locator(
            "#tbl_result tr:visible"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('th')].map(e => e.textContent.trim())
            )"""
        )

        rows = aau_user_page.locator("#tbl_result tr:visible").evaluate_all(
            """els => els.slice(1).map(el =>
              [...el.querySelectorAll('td')].map(e => e.textContent.trim())
            )"""
        )

        assert len(rows) == 1

        expected_rows = [
            ["Testing A", "TSTA 1", "25/01/2024", "73", "7"],
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_clear_filter_functionality(self, aau_user_page: Page):
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.get_by_label("Sort by").select_option(
            "transferring_body-desc"
        )
        aau_user_page.get_by_role("button", name="Apply", exact=True).click()
        aau_user_page.get_by_role("link", name="Clear filters").click()
        assert aau_user_page.inner_text("#series_filter") == ""
        assert aau_user_page.inner_text("#date_from_day") == ""
        assert aau_user_page.inner_text("#date_from_month") == ""
        assert aau_user_page.inner_text("#date_from_year") == ""
        assert aau_user_page.inner_text("#date_to_day") == ""
        assert aau_user_page.inner_text("#date_to_month") == ""
        assert aau_user_page.inner_text("#date_to_year") == ""
        assert (
            aau_user_page.get_by_label("Sort by", exact=True).evaluate(
                "el => el.options[el.selectedIndex].text"
            )
            == "Transferring body (Z to A)"
        )
