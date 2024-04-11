from playwright.sync_api import Page


def verify_header_row(header_rows):
    assert header_rows[0] == [
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
        return "bf203811-357a-45a8-8b38-770d1580691c"

    def test_browse_consignment_404_for_no_access(
        self, standard_user_page: Page
    ):
        consignment_id = "2fd4e03e-5913-4c04-b4f2-5a823fafd430"

        standard_user_page.goto(f"{self.route_url}/{consignment_id}")

        assert standard_user_page.inner_html("text='Page not found'")
        assert standard_user_page.inner_html(
            "text='If you typed the web address, check it is correct.'"
        )
        assert standard_user_page.inner_html(
            "text='If you pasted the web address, check you copied the entire address.'"
        )

    def test_browse_consignment_no_results_found(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")

        standard_user_page.locator("label").filter(
            has_text="Date of record"
        ).click()
        standard_user_page.locator("#date_to_day").fill("31")
        standard_user_page.locator("#date_to_month").fill("7")
        standard_user_page.locator("#date_to_year").fill("2021")

        standard_user_page.get_by_role("button", name="Apply filters").click()

        assert standard_user_page.inner_html("text='No results found'")
        assert standard_user_page.inner_html("text='Help with your search'")
        assert standard_user_page.inner_html(
            "text='Try changing or removing one or more applied filters.'"
        )
        assert standard_user_page.inner_html(
            "text='Alternatively, use the breadcrumbs to navigate back to the browse view.'"
        )

    def test_browse_consignment_breadcrumb(self, standard_user_page: Page):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")

        assert standard_user_page.inner_html("text='You are viewing'")
        assert standard_user_page.inner_html("text='Everything'")
        assert standard_user_page.inner_html("text='Testing A'")
        assert standard_user_page.inner_html("text='TSTA 1'")
        assert standard_user_page.inner_html("text='TDR-2023-TMT'")

    def test_browse_consignment_no_pagination(self, standard_user_page: Page):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")

        standard_user_page.get_by_label("Closed only").check()

        standard_user_page.get_by_role("button", name="Apply filters").click()

        next_button = standard_user_page.locator(".govuk-pagination__next a")

        assert not standard_user_page.get_by_label("Page 1").is_visible()
        assert not standard_user_page.get_by_label("Page 2").is_visible()
        assert not next_button.is_visible()

    def test_browse_consignment_has_pagination_with_next_page(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")

        standard_user_page.get_by_role("button", name="Apply filters").click()

        standard_user_page.wait_for_selector(".govuk-pagination")
        next_button = standard_user_page.locator(".govuk-pagination__next a")
        assert next_button.is_visible()
        assert standard_user_page.get_by_label("Page 1").is_visible()
        assert standard_user_page.get_by_label("Page 2").is_visible()

    def test_browse_consignment_has_pagination_with_previous_and_next_page(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")

        standard_user_page.wait_for_selector(".govuk-pagination")

        previous_button = standard_user_page.locator(
            ".govuk-pagination__prev a"
        )
        next_button = standard_user_page.locator(".govuk-pagination__next a")
        next_button.click()

        standard_user_page.wait_for_selector(".govuk-pagination")

        assert previous_button.is_visible()
        assert next_button.is_visible()
        assert standard_user_page.get_by_label("Page 1").is_visible()
        assert standard_user_page.get_by_label("Page 2").is_visible()
        assert standard_user_page.get_by_label("Page 3").is_visible()

    def test_browse_consignment_filter_functionality_with_query_string_parameters(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(
            f"{self.route_url}/{self.consignment_id}?sort=date_last_modified-desc&record_status=all&"
            f"date_filter_field=date_last_modified&date_from_day=01&date_from_month=01&date_from_year=2022&"
            f"date_to_day=&date_to_month=&date_to_year="
        )

        header_rows = standard_user_page.locator("#tbl_result").evaluate_all(
            """els => els.slice(0).map(el => [...el.querySelectorAll('th')].map(e => e.textContent.trim()))"""
        )

        rows = standard_user_page.locator(
            "#tbl_result tr.browse__mobile-table__top-row"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('td')].map(e => e.textContent.trim())
            )"""
        )

        expected_rows = [
            ["03/08/2022", "delivery-form-digital.doc", "Open", "-"],
            ["03/08/2022", "Digital Transfer training email .msg", "Open", "-"],
            ["03/08/2022", "Draft DDRO 05.docx", "Open", "-"],
            [
                "03/08/2022",
                "DTP_ Digital Transfer process diagram UG.docx",
                "Open",
                "-",
            ],
            ["03/08/2022", "base_de_donnees.png", "Open", "-"],
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_consignment_sort_functionality_by_record_status_descending(
        self, standard_user_page: Page
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

        header_rows = standard_user_page.locator("#tbl_result").evaluate_all(
            """els => els.slice(0).map(el => [...el.querySelectorAll('th')].map(e => e.textContent.trim()))"""
        )

        rows = standard_user_page.locator(
            "#tbl_result tr.browse__mobile-table__top-row"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('td')].map(e => e.textContent.trim())
            )"""
        )

        expected_rows = [
            ["03/08/2022", "Presentation.pptx", "Closed", "04/08/2122"],
            [
                "03/08/2022",
                "Emergency Contact Details Paul Young.docx",
                "Closed",
                "26/12/2121",
            ],
            ["03/08/2022", "Digital Transfer training email .msg", "Open", "-"],
            [
                "03/08/2022",
                "DTP_ Digital Transfer process diagram UG.docx",
                "Open",
                "-",
            ],
            ["03/08/2022", "Draft DDRO 05.docx", "Open", "-"],
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_consignment_filter_functionality_with_record_opening_date_filter(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")
        standard_user_page.locator("label").filter(
            has_text="Record opening date"
        ).click()
        standard_user_page.locator("#date_from_day").fill("01")
        standard_user_page.locator("#date_from_month").fill("01")
        standard_user_page.locator("#date_from_year").fill("2019")
        standard_user_page.get_by_role(
            "button", name="Apply", exact=True
        ).click()

        header_rows = standard_user_page.locator("#tbl_result").evaluate_all(
            """els => els.slice(0).map(el => [...el.querySelectorAll('th')].map(e => e.textContent.trim()))"""
        )

        rows = standard_user_page.locator(
            "#tbl_result tr.browse__mobile-table__top-row"
        ).evaluate_all(
            """els => els.slice(0).map(el =>
              [...el.querySelectorAll('td')].map(e => e.textContent.trim())
            )"""
        )

        expected_rows = [
            [
                "03/08/2022",
                "Emergency Contact Details Paul Young.docx",
                "Closed",
                "26/12/2121",
            ],
            ["03/08/2022", "Presentation.pptx", "Closed", "04/08/2122"],
        ]

        verify_header_row(header_rows)
        assert rows == expected_rows

    def test_browse_consignment_date_validation_with_record_status_selection_change(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")
        standard_user_page.get_by_text("Open only").click()
        standard_user_page.get_by_role(
            "button", name="Apply", exact=True
        ).click()

        assert not standard_user_page.get_by_text(
            "Select either ‘Date of record’ or ‘Record opening date’"
        ).is_visible()
        assert not standard_user_page.get_by_text(
            "Please enter value(s) in ‘Date from’ or ‘Date to’ field"
        ).is_visible()

    def test_browse_consignment_date_validation_with_empty_date_fields_and_date_filter_selected(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")
        standard_user_page.locator("label").filter(
            has_text="Date of record"
        ).click()
        standard_user_page.get_by_role(
            "button", name="Apply", exact=True
        ).click()

        standard_user_page.wait_for_selector(".govuk-error-message")

        assert standard_user_page.get_by_text(
            "Please enter value(s) in ‘Date from’ or ‘Date to’ field"
        ).is_visible()

    def test_browse_consignment_date_validation_with_date_fields_and_no_date_filter_selected(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")
        standard_user_page.locator("#date_from_day").fill("01")
        standard_user_page.locator("#date_from_month").fill("01")
        standard_user_page.locator("#date_from_year").fill("2019")
        standard_user_page.get_by_role(
            "button", name="Apply", exact=True
        ).click()

        standard_user_page.wait_for_selector(".govuk-error-message")

        assert standard_user_page.get_by_text(
            "Select either ‘Date of record’ or ‘Record opening date’"
        ).is_visible()

    def test_browse_consignment_date_filter_validation_date_from(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")
        standard_user_page.locator("label").filter(
            has_text="Date of record"
        ).click()
        standard_user_page.locator("#date_from_day").fill("1")
        standard_user_page.locator("#date_from_month").fill("12")
        standard_user_page.locator("#date_from_year").fill("2024")
        standard_user_page.get_by_role("button", name="Apply filters").click()

        standard_user_page.wait_for_selector(".govuk-error-message")

        assert standard_user_page.get_by_text(
            "‘Date from’ must be in the past"
        ).is_visible()

    def test_browse_consignment_date_filter_validation_to_date(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")
        standard_user_page.locator("label").filter(
            has_text="Date of record"
        ).click()
        standard_user_page.locator("#date_to_day").fill("31")
        standard_user_page.locator("#date_to_month").fill("12")
        standard_user_page.locator("#date_to_year").fill("2024")
        standard_user_page.get_by_role("button", name="Apply filters").click()

        standard_user_page.wait_for_selector(".govuk-error-message")

        assert standard_user_page.get_by_text(
            "‘Date to’ must be in the past"
        ).is_visible()

    def test_browse_consignment_date_filter_validation_date_from_and_to_date(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.consignment_id}")
        standard_user_page.locator("label").filter(
            has_text="Date of record"
        ).click()
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
