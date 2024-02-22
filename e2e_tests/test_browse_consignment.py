from playwright.sync_api import Page


class TestBrowseConsignment:
    @property
    def route_url(self):
        return "/browse/consignment"

    def test_browse_consignment_filter_functionality_with_query_string_parameters(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/99dc7ced-1683-4421-b9d5-eb90e9d9bd51?sort=closure_type-asc&date_from_day"
            "=01&date_from_month=03&date_from_year=2023&date_to_day=&date_to_month=&date_to_year="
        )

        table = authenticated_page.locator("#tbl_result").first
        headers = table.locator("thead th").all_text_contents()
        rows = table.locator("tbody tr")
        cols = rows.first.locator("td")

        assert headers == [
            "Record date",
            "Filename",
            "Status",
            "Record opening date",
        ]

        assert rows.count() == 1

        assert cols.nth(0).inner_text() == "28/07/2023"
        assert cols.nth(1).inner_text() == "testfile1"
        assert cols.nth(2).inner_text() == "Open"
        assert cols.nth(3).inner_text() == "-"

    def test_browse_consignment_sort_and_filter_functionality(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/99dc7ced-1683-4421-b9d5-eb90e9d9bd51"
        )
        authenticated_page.get_by_label("Day").first.fill("01")
        authenticated_page.get_by_label("Month").first.fill("07")
        authenticated_page.get_by_label("Year").first.fill("2023")
        authenticated_page.get_by_role("button", name="Apply filters").click()
        authenticated_page.get_by_label("Sort by").select_option(
            "closure_type-asc"
        )
        authenticated_page.get_by_role("button", name="Apply filters").click()

        table = authenticated_page.locator("#tbl_result").first
        headers = table.locator("thead th").all_text_contents()
        rows = table.locator("tbody tr")
        cols = rows.first.locator("td")

        assert headers == [
            "Record date",
            "Filename",
            "Status",
            "Record opening date",
        ]

        assert rows.count() == 1

        assert cols.nth(0).inner_text() == "28/07/2023"
        assert cols.nth(1).inner_text() == "testfile1"
        assert cols.nth(2).inner_text() == "Open"
        assert cols.nth(3).inner_text() == "-"

    def test_browse_consignment_clear_filter_functionality(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/99dc7ced-1683-4421-b9d5-eb90e9d9bd51"
        )
        authenticated_page.get_by_label("Sort by").select_option(
            "file_name-asc"
        )
        authenticated_page.get_by_role(
            "button", name="Apply", exact=True
        ).first.click()
        authenticated_page.get_by_label("Day").first.fill("01")
        authenticated_page.get_by_role("button", name="Apply filters").click()
        authenticated_page.get_by_role("link", name="Clear filters").click()

        assert authenticated_page.inner_text("#date_from_day") == ""
        assert authenticated_page.inner_text("#date_from_month") == ""
        assert authenticated_page.inner_text("#date_from_year") == ""
        assert authenticated_page.inner_text("#date_to_day") == ""
        assert authenticated_page.inner_text("#date_to_month") == ""
        assert authenticated_page.inner_text("#date_to_year") == ""
        assert (
            authenticated_page.get_by_label("", exact=True)
            .nth(1)
            .evaluate("el => el.options[el.selectedIndex].text")
            == "Records filename (A to Z)"
        )
