from playwright.sync_api import Page


def verify_header_row(header_rows):
    assert header_rows[0] == [
        "Transferring body",
        "Series",
        "Last consignment transferred",
        "Records held in series",
        "Consignments within series",
    ]


def verify_browse_all_header_row(header_rows):
    assert header_rows == [
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

    def test_browse_no_results_found(self, aau_user_page: Page):
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

    def test_browse_filter_functionality_with_query_string_parameters(
        self, aau_user_page: Page
    ):
        aau_user_page.goto(
            f"{self.route_url}?transferring_body_filter=all&series_filter=&date_from_day"
            "01=&date_from_month=07&date_from_year=2023&date_to_day=31&date_to_month=02&date_to_year=2024"
        )

        header_rows = aau_user_page.locator(
            "thead.govuk-table__head th[class*=browse__all__desktop__header]"
        ).evaluate_all("""els => els.map(e => e.textContent.trim())""")

        rows = aau_user_page.locator(
            ".govuk-table__row.browse__table__all_desktop__row"
        ).evaluate_all(
            """els => els.map(el =>
              [...el.querySelectorAll('td.browse__table__all_desktop')].map(e => e.textContent.trim())
            )"""
        )

        expected_rows = [
            ["Mock 1 Department", "MOCK1 123", "05/03/2024", "83", "11"],
            ["Testing A", "TSTA 1", "25/01/2024", "63", "5"],
        ]

        verify_browse_all_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_sort_functionality_by_transferring_body_descending(
        self, aau_user_page: Page
    ):
        aau_user_page.get_by_label("Sort by").select_option(
            "transferring_body-desc"
        )
        aau_user_page.get_by_role("button", name="Apply", exact=True).click()

        header_rows = aau_user_page.locator(
            "thead.govuk-table__head th[class*=browse__all__desktop__header]"
        ).evaluate_all("""els => els.map(e => e.textContent.trim())""")

        rows = aau_user_page.locator(
            ".govuk-table__row.browse__table__all_desktop__row"
        ).evaluate_all(
            """els => els.map(el =>
              [...el.querySelectorAll('td.browse__table__all_desktop')].map(e => e.textContent.trim())
            )"""
        )

        expected_rows = [
            ["Testing A", "TSTA 1", "25/01/2024", "63", "5"],
            ["Mock 1 Department", "MOCK1 123", "05/03/2024", "83", "11"],
        ]

        verify_browse_all_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_filter_functionality_with_transferring_body_filter(
        self, aau_user_page: Page
    ):
        aau_user_page.locator("#transferring_body_filter").select_option(
            "Mock 1 Department"
        )
        aau_user_page.get_by_role("button", name="Apply filters").click()
        aau_user_page.get_by_role("button", name="Apply", exact=True).click()

        header_rows = aau_user_page.locator(
            "thead.govuk-table__head th[class*=browse__all__desktop__header]"
        ).evaluate_all("""els => els.map(e => e.textContent.trim())""")

        rows = aau_user_page.locator(
            ".govuk-table__row.browse__table__all_desktop__row"
        ).evaluate_all(
            """els => els.map(el =>
              [...el.querySelectorAll('td.browse__table__all_desktop')].map(e => e.textContent.trim())
            )"""
        )

        expected_rows = [
            ["Mock 1 Department", "MOCK1 123", "05/03/2024", "83", "11"]
        ]

        verify_browse_all_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_filter_functionality_with_series_filter_wildcard_character(
        self, aau_user_page: Page
    ):
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.locator("#series_filter").fill("1")
        aau_user_page.get_by_role("button", name="Apply filters").click()

        header_rows = aau_user_page.locator(
            "thead.govuk-table__head th[class*=browse__all__desktop__header]"
        ).evaluate_all("""els => els.map(e => e.textContent.trim())""")

        rows = aau_user_page.locator(
            ".govuk-table__row.browse__table__all_desktop__row"
        ).evaluate_all(
            """els => els.map(el =>
              [...el.querySelectorAll('td.browse__table__all_desktop')].map(e => e.textContent.trim())
            )"""
        )

        expected_rows = [
            ["Mock 1 Department", "MOCK1 123", "05/03/2024", "83", "11"],
            ["Testing A", "TSTA 1", "25/01/2024", "63", "5"],
        ]

        verify_browse_all_header_row(header_rows)
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
            "thead.govuk-table__head th[class*=browse__all__desktop__header]"
        ).evaluate_all("""els => els.map(e => e.textContent.trim())""")

        rows = aau_user_page.locator(
            ".govuk-table__row.browse__table__all_desktop__row"
        ).evaluate_all(
            """els => els.map(el =>
              [...el.querySelectorAll('td.browse__table__all_desktop')].map(e => e.textContent.trim())
            )"""
        )

        expected_rows = [
            ["Mock 1 Department", "MOCK1 123", "05/03/2024", "83", "11"],
            ["Testing A", "TSTA 1", "25/01/2024", "63", "5"],
        ]

        verify_browse_all_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_date_filter_validation_date_from(self, aau_user_page: Page):
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.locator("#date_from_day").fill("1")
        aau_user_page.locator("#date_from_month").fill("12")
        aau_user_page.locator("#date_from_year").fill("2024")
        aau_user_page.get_by_role("button", name="Apply filters").click()

        assert aau_user_page.get_by_text(
            "‘Date from’ must be in the past"
        ).is_visible()

    def test_browse_date_filter_validation_to_date(self, aau_user_page: Page):
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.locator("#date_to_day").fill("31")
        aau_user_page.locator("#date_to_month").fill("12")
        aau_user_page.locator("#date_to_year").fill("2024")
        aau_user_page.get_by_role("button", name="Apply filters").click()

        assert aau_user_page.get_by_text(
            "‘Date to’ must be in the past"
        ).is_visible()

    def test_browse_date_filter_validation_date_from_and_to_date(
        self, aau_user_page: Page
    ):
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.locator("#date_from_day").fill("1")
        aau_user_page.locator("#date_from_month").fill("1")
        aau_user_page.locator("#date_from_year").fill("2023")
        aau_user_page.locator("#date_to_day").fill("31")
        aau_user_page.locator("#date_to_month").fill("12")
        aau_user_page.locator("#date_to_year").fill("2022")
        aau_user_page.get_by_role("button", name="Apply filters").click()

        assert aau_user_page.get_by_text(
            "‘Date from’ must be the same as or before ‘31/12/2022’"
        ).is_visible()

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
