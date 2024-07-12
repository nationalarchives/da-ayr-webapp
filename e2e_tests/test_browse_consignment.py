from playwright.sync_api import Page


def verify_header_row(header_rows):
    assert header_rows == [
        "Date of record",
        "File name",
        "Status",
        "Record opening date",
    ]


class TestBrowseConsignment:
    @property
    def route_url(self):
        return "/browse/consignment"

    @property
    def consignment_id(self):
        return "016031db-1398-4fe4-b743-630aa82ea32a"

    def test_browse_consignment_404_for_no_access(
        self, standard_user_page: Page
    ):
        consignment_id = "2fd4e03e-5913-4c04-b4f2-5a823fafd430"

        standard_user_page.goto(f"{self.route_url}/{consignment_id}")

        assert standard_user_page.inner_html("text='Page not found'")

    def test_browse_consignment_sort_functionality_by_record_status_descending(
        self, standard_user_page: Page, utils
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")
        standard_user_page.get_by_label("Sort by").select_option(
            "closure_type-asc"
        )
        standard_user_page.locator("label").filter(
            has_text="Date of record"
        ).click()
        standard_user_page.locator("#date_from_day").fill("01")
        standard_user_page.locator("#date_from_month").fill("01")
        standard_user_page.locator("#date_from_year").fill("2022")
        standard_user_page.get_by_role(
            "button", name="Apply", exact=True
        ).click()

        header_rows = utils.get_desktop_page_table_headers(standard_user_page)
        rows = utils.get_desktop_page_table_rows(standard_user_page)

        expected_rows = [
            ["22/11/2023", "closed_file_R - Copy.pdf", "Open", "–"],
            ["22/11/2023", "closed_file_R.pdf", "Open", "–"],
            ["22/11/2023", "closed_file.txt", "Open", "–"],
            ["22/11/2023", "file-a1,.txt", "Open", "–"],
            ["22/11/2023", "file-a1.txt", "Open", "–"],
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_consignment_clear_filter_functionality(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")
        standard_user_page.get_by_label("Sort by").select_option(
            "file_name-asc"
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
            == "File name (A to Z)"
        )
