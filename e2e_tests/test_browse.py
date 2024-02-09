from playwright.sync_api import Page


def test_has_title(authenticated_page: Page):
    authenticated_page.goto("/browse")

    assert (
        authenticated_page.title()
        == "Browse – AYR - Access Your Records – GOV.UK"
    )


class TestBrowse:
    def test_browse_filter_functionality_with_query_string_parameters(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            "/browse?transferring_body_filter=all&series_filter=&date_from_day"
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

    def test_browse_sort_and_filter_functionality(
        self, authenticated_page: Page
    ):
        authenticated_page.goto("/browse")
        authenticated_page.get_by_label("", exact=True).nth(1).select_option(
            "MOCK1 Department"
        )
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

    def test_browse_sort_and_filter_functionality_with_series_filter_wildcard_character(
        self, authenticated_page: Page
    ):
        authenticated_page.goto("/browse")
        authenticated_page.get_by_label("", exact=True).nth(2).fill("1")
        authenticated_page.get_by_role("button", name="Apply filters").click()

        table = authenticated_page.locator("#tbl_result").first
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

    def test_browse_clear_filter_functionality(self, authenticated_page: Page):
        authenticated_page.goto("/browse")
        authenticated_page.get_by_label("Sort by").select_option(
            "transferring_body-desc"
        )
        authenticated_page.get_by_role(
            "button", name="Apply", exact=True
        ).first.click()
        authenticated_page.get_by_label("", exact=True).nth(1).select_option(
            "Testing A"
        )
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
            == "Transferring body (Z to A)"
        )


class TestBrowseTransferringBody:
    def test_browse_transferring_body_filter_functionality_with_query_string_parameters(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            "/browse?transferring_body_id=6b63aa4d-7838-4010-b6f8-66fb3c07823d&series_filter=&date_from_day"
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
            "/browse?transferring_body_id=6b63aa4d-7838-4010-b6f8-66fb3c07823d"
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
            "/browse?transferring_body_id=6b63aa4d-7838-4010-b6f8-66fb3c07823d"
        )
        authenticated_page.get_by_label("Sort by").select_option("series-desc")
        authenticated_page.get_by_role(
            "button", name="Apply", exact=True
        ).first.click()
        authenticated_page.get_by_label("", exact=True).nth(1).fill("mock")
        authenticated_page.get_by_role("button", name="Apply filters").click()
        authenticated_page.get_by_role("link", name="clear filters").click()

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


class TestBrowseSeries:
    def test_browse_series_filter_functionality_with_query_string_parameters(
        self, authenticated_page: Page
    ):
        authenticated_page.goto(
            "/browse?series_id=c28cc3ab-c12a-4f06-82e1-18648c82a17f&sort=last_record_transferred-desc&date_from_day"
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
            "/browse?series_id=c28cc3ab-c12a-4f06-82e1-18648c82a17f"
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
            "/browse?series_id=c28cc3ab-c12a-4f06-82e1-18648c82a17f"
        )
        authenticated_page.get_by_label("Sort by").select_option(
            "records_held-desc"
        )
        authenticated_page.get_by_role(
            "button", name="Apply", exact=True
        ).first.click()
        authenticated_page.get_by_label("Day").first.fill("01")
        authenticated_page.get_by_role("button", name="Apply filters").click()
        authenticated_page.get_by_role("link", name="clear filters").click()

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
