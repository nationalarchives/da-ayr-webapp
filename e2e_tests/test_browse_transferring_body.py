from playwright.sync_api import Page


class TestBrowseTransferringBody:
    @property
    def route_url(self):
        return "/browse/transferring_body"

    def test_browse_transferring_body_filter_functionality_with_query_string_parameters(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/6b63aa4d-7838-4010-b6f8-66fb3c07823d?series_filter=&date_from_day"
            "01=&date_from_month=07&date_from_year=2023&date_to_day=31&date_to_month=07&date_to_year=2023"
        )

        table = authenticated_page.locator("#tbl_result").first
        headers = table.locator("thead th").all_text_contents()
        rows = table.locator("tbody tr")
        cols = rows.first.locator("td")

        assert headers == [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ]

        assert rows.count() == 1

        assert cols.nth(0).inner_text() == "MOCK1 Department"
        assert cols.nth(1).inner_text() == "MOCK1 123"
        assert cols.nth(2).inner_text() == "28/07/2023"
        assert cols.nth(3).inner_text() == "1"
        assert cols.nth(4).inner_text() == "1"

    def test_browse_transferring_body_sort_and_filter_functionality(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/6b63aa4d-7838-4010-b6f8-66fb3c07823d"
        )
        authenticated_page.get_by_label("", exact=True).nth(1).fill("mock")
        authenticated_page.get_by_role("button", name="Apply filters").click()
        authenticated_page.get_by_label("Sort by").select_option(
            "last_record_transferred-desc"
        )
        authenticated_page.get_by_role("button", name="Apply filters").click()

        table = authenticated_page.locator("#tbl_result").first
        headers = table.locator("thead th").all_text_contents()
        rows = table.locator("tbody tr")
        cols = rows.first.locator("td")

        assert headers == [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ]

        assert rows.count() == 1

        assert cols.nth(0).inner_text() == "MOCK1 Department"
        assert cols.nth(1).inner_text() == "MOCK1 123"
        assert cols.nth(2).inner_text() == "28/07/2023"
        assert cols.nth(3).inner_text() == "1"
        assert cols.nth(4).inner_text() == "1"

    def test_browse_transferring_body_clear_filter_functionality(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/6b63aa4d-7838-4010-b6f8-66fb3c07823d"
        )
        authenticated_page.get_by_label("Sort by").select_option("series-desc")
        authenticated_page.get_by_role(
            "button", name="Apply", exact=True
        ).first.click()
        authenticated_page.get_by_label("", exact=True).nth(1).fill("mock")
        authenticated_page.get_by_role("button", name="Apply filters").click()
        authenticated_page.get_by_role("link", name="Clear filters").click()

        assert authenticated_page.inner_text("#series_filter") == ""
        assert authenticated_page.inner_text("#date_from_day") == ""
        assert authenticated_page.inner_text("#date_from_month") == ""
        assert authenticated_page.inner_text("#date_from_year") == ""
        assert authenticated_page.inner_text("#date_to_day") == ""
        assert authenticated_page.inner_text("#date_to_month") == ""
        assert authenticated_page.inner_text("#date_to_year") == ""
        assert (
            authenticated_page.get_by_label("Sort by", exact=True).evaluate(
                "el => el.options[el.selectedIndex].text"
            )
            == "Series (Z to A)"
        )
