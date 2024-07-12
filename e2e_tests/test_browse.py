from playwright.sync_api import Page


def verify_browse_all_header_row(header_rows):
    assert header_rows == [
        "Transferring body",
        "Series reference",
        "Last transfer date",
        "Record total",
        "Consignments within series",
    ]


class TestBrowse:
    @property
    def route_url(self):
        return "/browse"

    def test_browse_with_filter_with_no_results_found(
        self, aau_user_page: Page
    ):
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

    def test_browse_with_filter_sort_and_choose_transferring_body(
        self, aau_user_page: Page, utils
    ):
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.get_by_label("Sort by").select_option(
            "transferring_body-desc"
        )
        aau_user_page.get_by_role("button", name="Apply", exact=True).click()

        aau_user_page.locator("#transferring_body_filter").fill(
            "Mock 1 Department"
        )
        aau_user_page.locator("#date_from_day").fill("1")
        aau_user_page.locator("#date_from_month").fill("1")
        aau_user_page.locator("#date_from_year").fill("2024")
        aau_user_page.get_by_role("button", name="Apply filters").click()

        header_rows = utils.get_desktop_page_table_headers(aau_user_page)
        rows = utils.get_desktop_page_table_rows(aau_user_page)

        expected_rows = [
            ["Mock 1 Department", "MOCK1 123", "05/03/2024", "83", "11"]
        ]

        verify_browse_all_header_row(header_rows)
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
