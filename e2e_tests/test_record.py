from playwright.sync_api import Page


class TestRecord:
    @property
    def route_url(self):
        return "/record"

    def test_record_404_for_no_access(self, standard_user_page: Page):
        record_id = "7ce919c0-9f2b-4133-b41f-f85bdecc6a52"

        standard_user_page.goto(f"{self.route_url}/{record_id}")
        assert standard_user_page.inner_html("text='Page not found'")
        assert standard_user_page.inner_html(
            "text='If you typed the web address, check it is correct.'"
        )
        assert standard_user_page.inner_html(
            "text='If you pasted the web address, check you copied the entire address.'"
        )

    def test_record_metadata_with_open_record_status(
        self, standard_user_page: Page
    ):
        record_id = "100251bb-5b93-48a9-953f-ad5bd9abfbdc"

        standard_user_page.goto(f"{self.route_url}/{record_id}")
        expected_fields = [
            "File name",
            "Description",
            "Citeable reference",
            "Status",
            "Date of record",
            "Transferring body",
            "Series reference",
            "Consignment reference",
            "File reference",
            "Former reference",
            "Translated file name",
            "Held by",
            "Legal status",
            "Rights copyright",
            "Language",
        ]
        for field in expected_fields:
            assert standard_user_page.get_by_text(
                field, exact=True
            ).is_visible()

    def test_record_metadata_with_closed_record_status(
        self, standard_user_page: Page
    ):
        record_id = "405ea5a6-b71d-4ecd-be3c-43062af8e1e6"

        standard_user_page.goto(f"{self.route_url}/{record_id}")
        expected_fields = [
            "File name",
            "Alternative file name",
            "Description",
            "Citeable reference",
            "Alternative description",
            "Status",
            "Closure start date",
            "Closure period",
            "Date of record",
            "FOI exemption code(s)",
            "Transferring body",
            "Series reference",
            "Consignment reference",
            "File reference",
            "Former reference",
            "Translated file name",
            "Held by",
            "Legal status",
            "Rights copyright",
            "Language",
        ]

        for field in expected_fields:
            assert standard_user_page.get_by_text(
                field, exact=True
            ).is_visible()

    def test_record_download_record(self, standard_user_page: Page):
        record_id = "100251bb-5b93-48a9-953f-ad5bd9abfbdc"
        standard_user_page.goto(f"{self.route_url}/{record_id}")

        with standard_user_page.expect_download() as download_record:
            standard_user_page.get_by_text("Download record").click()
        download = download_record.value
        assert "TSTA 1_ZD5B3S.doc" == download.suggested_filename
