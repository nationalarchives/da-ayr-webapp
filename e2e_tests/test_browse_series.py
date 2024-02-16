from playwright.sync_api import Page


class TestBrowseSeries:
    @property
    def route_url(self):
        return "/browse/series"

    def test_browse_series_filter_functionality_with_query_string_parameters(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/c28cc3ab-c12a-4f06-82e1-18648c82a17f?sort=last_record_transferred-desc&date_from_day"
            "=01&date_from_month=03&date_from_year=2023&date_to_day=&date_to_month=&date_to_year="
        )

        table = authenticated_page.locator("#tbl_result").first
        headers = table.locator("thead th").all_text_contents()
        rows = table.locator("tbody tr")
        cols = rows.first.locator("td")

        assert headers == [
            "Transferring body",
            "Series",
            "Consignment transferred",
            "Records in consignment",
            "Consignment reference",
        ]

        assert rows.count() == 1

        assert cols.nth(0).inner_text() == "MOCK1 Department"
        assert cols.nth(1).inner_text() == "MOCK1 123"
        assert cols.nth(2).inner_text() == "28/07/2023"
        assert cols.nth(3).inner_text() == "1"
        assert cols.nth(4).inner_text() == "TDR-2023-MNJ"

    def test_browse_series_sort_and_filter_functionality(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/c28cc3ab-c12a-4f06-82e1-18648c82a17f"
        )
        authenticated_page.get_by_label("Day").first.fill("01")
        authenticated_page.get_by_label("Month").first.fill("03")
        authenticated_page.get_by_label("Year").first.fill("2023")
        authenticated_page.get_by_role("button", name="Apply filters").click()
        authenticated_page.get_by_label("Sort by").select_option(
            "last_record_transferred-asc"
        )
        authenticated_page.get_by_role("button", name="Apply filters").click()

        table = authenticated_page.locator("#tbl_result").first
        headers = table.locator("thead th").all_text_contents()
        rows = table.locator("tbody tr")
        cols = rows.first.locator("td")

        assert headers == [
            "Transferring body",
            "Series",
            "Consignment transferred",
            "Records in consignment",
            "Consignment reference",
        ]

        assert rows.count() == 1

        assert cols.nth(0).inner_text() == "MOCK1 Department"
        assert cols.nth(1).inner_text() == "MOCK1 123"
        assert cols.nth(2).inner_text() == "28/07/2023"
        assert cols.nth(3).inner_text() == "1"
        assert cols.nth(4).inner_text() == "TDR-2023-MNJ"

    def test_browse_series_clear_filter_functionality(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            f"{self.route_url}/c28cc3ab-c12a-4f06-82e1-18648c82a17f"
        )
        authenticated_page.get_by_label("Sort by").select_option(
            "records_held-desc"
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
            == "Records held in consignment (most first)"
        )
