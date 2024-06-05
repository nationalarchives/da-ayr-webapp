from playwright.sync_api import Page


def verify_header_row(header_rows):
    assert header_rows[0] == [
        "Transferring body",
        "Series reference",
        "Last transfer date",
        "Record total",
        "Consignment reference",
    ]


class TestBrowseSeries:
    @property
    def route_url(self):
        return "/browse/series"

    @property
    def series_id(self):
        return "1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7"

    def test_browse_series_404_for_no_access(self, standard_user_page: Page):
        series_id = "8bd7ad22-90d1-4c7f-ae00-645dfd1987cc"

        standard_user_page.goto(f"{self.route_url}/{series_id}")

        assert standard_user_page.inner_html("text='Page not found'")
        assert standard_user_page.inner_html(
            "text='If you typed the web address, check it is correct.'"
        )
        assert standard_user_page.inner_html(
            "text='If you pasted the web address, check you copied the entire address.'"
        )

    def test_browse_series_no_results_found(self, standard_user_page: Page):
        standard_user_page.goto(f"{self.route_url}/{self.series_id}")

        standard_user_page.locator("#date_to_day").fill("1")
        standard_user_page.locator("#date_to_month").fill("1")
        standard_user_page.locator("#date_to_year").fill("2022")

        standard_user_page.get_by_role("button", name="Apply filters").click()

        assert standard_user_page.inner_html("text='No results found'")
        assert standard_user_page.inner_html("text='Help with your search'")
        assert standard_user_page.inner_html(
            "text='Try changing or removing one or more applied filters.'"
        )
        assert standard_user_page.inner_html(
            "text='Alternatively, use the breadcrumbs to navigate back to the browse view.'"
        )

    def test_browse_series_breadcrumb(self, standard_user_page: Page):
        standard_user_page.goto(f"{self.route_url}/{self.series_id}")

        assert standard_user_page.inner_html("text='You are viewing'")
        assert standard_user_page.inner_html("text='All available records'")
        assert standard_user_page.inner_html("text='Testing A'")
        assert standard_user_page.inner_html("text='TSTA 1'")

    def test_browse_series_filter_functionality_with_query_string_parameters(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(
            f"{self.route_url}/{self.series_id}?sort=last_record_transferred-desc&date_from_day"
            "=01&date_from_month=01&date_from_year=2023&date_to_day=31&date_to_month=12&date_to_year=2023"
        )

        header_rows = standard_user_page.locator(
            "#tbl_result tr:visible"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('th.browse__series__desktop__header')].map(e => e.textContent.trim())
            )"""
        )
        rows = standard_user_page.locator(
            "#tbl_result tr.govuk-table__row-ref"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('td')].map(e => e.textContent.trim())
            )"""
        )

        expected_rows = [
            ["Testing A", "TSTA 1", "30/11/2023", "9", "TDR-2023-GXFH"],
            ["Testing A", "TSTA 1", "18/10/2023", "7", "TDR-2023-BV6"],
            ["Testing A", "TSTA 1", "09/08/2023", "15", "TDR-2023-TMT"],
            ["Testing A", "TSTA 1", "09/08/2023", "15", "TDR-2023-TH4"],
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_series_sort_functionality_by_records_held_in_consignment_descending(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.series_id}")
        standard_user_page.get_by_label("Sort by").select_option(
            "records_held-desc"
        )
        standard_user_page.get_by_role(
            "button", name="Apply", exact=True
        ).click()

        standard_user_page.wait_for_selector("#tbl_result")

        header_rows = standard_user_page.locator(
            "#tbl_result tr:visible"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('th.browse__series__desktop__header')].map(e => e.textContent.trim())
            )"""
        )
        rows = standard_user_page.locator(
            "#tbl_result tr.govuk-table__row-ref"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('td')].map(e => e.textContent.trim())
            )"""
        )

        expected_rows = [
            ["Testing A", "TSTA 1", "25/01/2024", "17", "TDR-2024-H5DN"],
            ["Testing A", "TSTA 1", "09/08/2023", "15", "TDR-2023-TMT"],
            ["Testing A", "TSTA 1", "09/08/2023", "15", "TDR-2023-TH4"],
            ["Testing A", "TSTA 1", "30/11/2023", "9", "TDR-2023-GXFH"],
            ["Testing A", "TSTA 1", "18/10/2023", "7", "TDR-2023-BV6"],
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_series_filter_functionality_with_date_filter(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.series_id}")
        standard_user_page.locator("#date_from_day").fill("1")
        standard_user_page.locator("#date_from_month").fill("1")
        standard_user_page.locator("#date_from_year").fill("2024")
        standard_user_page.get_by_role("button", name="Apply filters").click()

        standard_user_page.wait_for_selector("#tbl_result")

        header_rows = standard_user_page.locator(
            "#tbl_result tr:visible"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('th.browse__series__desktop__header')].map(e => e.textContent.trim())
            )"""
        )
        rows = standard_user_page.locator(
            "#tbl_result tr.govuk-table__row-ref"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('td')].map(e => e.textContent.trim())
            )"""
        )

        expected_rows = [
            ["Testing A", "TSTA 1", "25/01/2024", "17", "TDR-2024-H5DN"],
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_series_date_filter_validation_date_from(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.series_id}")
        standard_user_page.locator("#date_from_day").fill("1")
        standard_user_page.locator("#date_from_month").fill("12")
        standard_user_page.locator("#date_from_year").fill("2024")
        standard_user_page.get_by_role("button", name="Apply filters").click()

        standard_user_page.wait_for_selector(".govuk-error-message")

        assert standard_user_page.get_by_text(
            "‘Date from’ must be in the past"
        ).is_visible()

    def test_browse_series_date_filter_validation_to_date(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.series_id}")
        standard_user_page.locator("#date_to_day").fill("31")
        standard_user_page.locator("#date_to_month").fill("12")
        standard_user_page.locator("#date_to_year").fill("2024")
        standard_user_page.get_by_role("button", name="Apply filters").click()

        standard_user_page.wait_for_selector(".govuk-error-message")

        assert standard_user_page.get_by_text(
            "‘Date to’ must be in the past"
        ).is_visible()

    def test_browse_series_date_filter_validation_date_from_and_to_date(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.series_id}")
        standard_user_page.locator("#date_from_day").fill("1")
        standard_user_page.locator("#date_from_month").fill("1")
        standard_user_page.locator("#date_from_year").fill("2023")
        standard_user_page.locator("#date_to_day").fill("31")
        standard_user_page.locator("#date_to_month").fill("12")
        standard_user_page.locator("#date_to_year").fill("2022")
        standard_user_page.get_by_role("button", name="Apply filters").click()

        standard_user_page.wait_for_selector(".govuk-error-message")

        assert standard_user_page.get_by_text(
            "‘Date from’ must be the same as or before ‘31/12/2022’"
        ).is_visible()

    def test_browse_series_clear_filter_functionality(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.series_id}")
        standard_user_page.get_by_label("Sort by").select_option(
            "records_held-desc"
        )
        standard_user_page.get_by_role(
            "button", name="Apply", exact=True
        ).click()
        standard_user_page.get_by_role("link", name="Clear filters").click()

        assert standard_user_page.inner_text("#date_from_day") == ""
        assert standard_user_page.inner_text("#date_from_month") == ""
        assert standard_user_page.inner_text("#date_from_year") == ""
        assert standard_user_page.inner_text("#date_to_day") == ""
        assert standard_user_page.inner_text("#date_to_month") == ""
        assert standard_user_page.inner_text("#date_to_year") == ""
        assert (
            standard_user_page.get_by_label("Sort by", exact=True).evaluate(
                "el => el.options[el.selectedIndex].text"
            )
            == "Records total (most)"
        )
