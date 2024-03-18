from playwright.sync_api import Page


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

        table = aau_user_page.locator("#tbl_result").first
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

    def test_browse_sort_and_filter_functionality(self, aau_user_page: Page):
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.get_by_label("", exact=True).nth(1).select_option(
            "MOCK1 Department"
        )
        aau_user_page.get_by_role("button", name="Apply filters").click()
        aau_user_page.get_by_label("Sort by").select_option(
            "last_record_transferred-desc"
        )
        aau_user_page.get_by_role("button", name="Apply filters").click()

        table = aau_user_page.locator("#tbl_result").first
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

    def test_browse_sort_and_filter_functionality_with_series_filter_wildcard_character(
        self, aau_user_page: Page
    ):
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.get_by_label("", exact=True).nth(2).fill("1")
        aau_user_page.get_by_role("button", name="Apply filters").click()

        table = aau_user_page.locator("#tbl_result").first
        headers = table.locator("thead th").all_text_contents()
        rows = table.locator("tbody tr")
        cols = rows.nth(0).locator("td")

        assert headers == [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ]

        assert rows.count() == 2

        assert cols.nth(0).inner_text() == "MOCK1 Department"
        assert cols.nth(1).inner_text() == "MOCK1 123"
        assert cols.nth(2).inner_text() == "28/07/2023"
        assert cols.nth(3).inner_text() == "1"
        assert cols.nth(4).inner_text() == "1"

        cols = rows.nth(1).locator("td")

        assert cols.nth(0).inner_text() == "Testing A"
        assert cols.nth(1).inner_text() == "TSTA 1"
        assert cols.nth(2).inner_text() == "25/01/2024"
        assert cols.nth(3).inner_text() == "73"
        assert cols.nth(4).inner_text() == "7"

    def test_browse_clear_filter_functionality(self, aau_user_page: Page):
        aau_user_page.goto(f"{self.route_url}")
        aau_user_page.get_by_label("Sort by").select_option(
            "transferring_body-desc"
        )
        aau_user_page.get_by_role(
            "button", name="Apply", exact=True
        ).first.click()
        aau_user_page.get_by_label("", exact=True).nth(1).select_option(
            "Testing A"
        )
        aau_user_page.get_by_role("button", name="Apply filters").click()
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
