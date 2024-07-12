from playwright.sync_api import Page


def verify_header_row(header_rows):
    assert header_rows == [
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

    def test_browse_series_filter_functionality_with_date_filter(
        self, standard_user_page: Page, utils
    ):
        standard_user_page.goto(f"{self.route_url}/{self.series_id}")
        standard_user_page.locator("#date_from_day").fill("1")
        standard_user_page.locator("#date_from_month").fill("11")
        standard_user_page.locator("#date_from_year").fill("2023")
        standard_user_page.get_by_role("button", name="Apply filters").click()

        standard_user_page.get_by_label("Sort by").select_option(
            "records_held-desc"
        )
        standard_user_page.get_by_role(
            "button", name="Apply", exact=True
        ).click()

        header_rows = utils.get_desktop_page_table_headers(standard_user_page)
        rows = utils.get_desktop_page_table_rows(standard_user_page)

        expected_rows = [
            ["Testing A", "TSTA 1", "30/11/2023", "9", "TDR-2023-GXFH"]
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

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
