import re

from playwright.sync_api import Page


class TestRecord:
    @property
    def route_url(self):
        return "/record"

    @property
    def record_id(self):
        return "5e1dd9f7-f688-4cfd-8487-5acdb4bf09de"

    def test_record_has_title(self, standard_user_page: Page):
        standard_user_page.goto(f"{self.route_url}/{self.record_id}")

        assert (
            standard_user_page.title()
            == "Record – AYR - Access Your Records – GOV.UK"
        )

    def test_record_404_for_no_access(self, standard_user_page: Page):
        transferring_body_id = "6b63aa4d-7838-4010-b6f8-66fb3c07823d"

        standard_user_page.goto(f"{self.route_url}/{transferring_body_id}")
        assert standard_user_page.inner_html("text='Page not found'")
        assert standard_user_page.inner_html(
            "text='If you typed the web address, check it is correct.'"
        )
        assert standard_user_page.inner_html(
            "text='If you pasted the web address, check you copied the entire address.'"
        )

    def test_record_breadcrumb(self, standard_user_page: Page):
        standard_user_page.goto(f"{self.route_url}/{self.record_id}")

        assert standard_user_page.inner_html("text='You are viewing'")
        assert standard_user_page.inner_html("text='Everything'")
        assert standard_user_page.inner_html("text='Testing A'")
        assert standard_user_page.inner_html("text='TSTA 1'")
        assert standard_user_page.inner_html("text='TDR-2023-TMT'")
        assert standard_user_page.inner_html("text='delivery-form-digital.doc'")

    def test_record_metadata_with_open_record_status(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.record_id}")

        # Verify if the expected metadata is visible on the record page
        assert standard_user_page.get_by_role(
            "heading", name="Record details"
        ).is_visible()
        assert standard_user_page.get_by_text(
            "File name", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Description", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text("Status", exact=True).is_visible()
        assert standard_user_page.get_by_text(
            "Date of record", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Transferring body", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text("Series", exact=True).is_visible()
        assert standard_user_page.get_by_text(
            "Consignment reference", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "File reference", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Former reference", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Translated file name", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Held by", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Legal status", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Rights copyright", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Language", exact=True
        ).is_visible()

        # verify record arrangement
        assert standard_user_page.get_by_role(
            "heading", name="Record arrangement"
        ).is_visible()
        assert standard_user_page.get_by_text("data", exact=True).is_visible()
        assert standard_user_page.get_by_text(
            "content", exact=True
        ).is_visible()
        assert (
            standard_user_page.locator("li")
            .filter(has_text=re.compile(r"^delivery-form-digital\.doc$"))
            .is_visible()
        )

    def test_record_metadata_with_closed_record_status(
        self, standard_user_page: Page
    ):
        record_id = "5f38fb25-794e-4542-88df-88d8eca3bd95"
        standard_user_page.goto(f"{self.route_url}/{record_id}")

        # Verify if the expected metadata is visible on the record page
        assert standard_user_page.get_by_role(
            "heading", name="Record details"
        ).is_visible()
        assert standard_user_page.get_by_text(
            "File name", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Alternative file name", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Description", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Alternative description", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text("Status", exact=True).is_visible()
        assert standard_user_page.get_by_text(
            "Record opening date 26/12/2121"
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Closure start date", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Closure period", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Date of record", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "FOI exemption code(s)", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Transferring body", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text("Series", exact=True).is_visible()
        assert standard_user_page.get_by_text(
            "Consignment reference", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "File reference", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Former reference", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Translated file name", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Held by", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Legal status", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Rights copyright", exact=True
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Language", exact=True
        ).is_visible()

        # verify record arrangement
        assert standard_user_page.get_by_role(
            "heading", name="Record arrangement"
        ).is_visible()
        assert standard_user_page.get_by_text("data", exact=True).is_visible()
        assert standard_user_page.get_by_text("data", exact=True).is_visible()
        assert standard_user_page.get_by_text(
            "Emergency Response Team", exact=True
        ).is_visible()
        assert (
            standard_user_page.locator("li")
            .filter(
                has_text=re.compile(
                    r"^Emergency Contact Details Paul Young\.docx$"
                )
            )
            .is_visible()
        )

    def test_record_download_record_with_file_name(
        self, standard_user_page: Page
    ):
        standard_user_page.goto(f"{self.route_url}/{self.record_id}")
        assert standard_user_page.get_by_role(
            "heading", name="Rights to access"
        ).is_visible()
        assert standard_user_page.get_by_role(
            "link", name="Download record"
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Refer to Terms of use."
        ).is_visible()

        with standard_user_page.expect_download() as download_record:
            standard_user_page.get_by_text("Download record").click()
        download = download_record.value
        assert "delivery-form-digital.doc" == download.suggested_filename

    def test_record_download_record_with_citeable_reference(
        self, standard_user_page: Page
    ):
        record_id = "c63b7ce7-5fc7-4be8-84e7-f04bc84e3688"
        standard_user_page.goto(f"{self.route_url}/{record_id}")
        assert standard_user_page.get_by_role(
            "heading", name="Rights to access"
        ).is_visible()
        assert standard_user_page.get_by_role(
            "link", name="Download record"
        ).is_visible()
        assert standard_user_page.get_by_text(
            "Refer to Terms of use."
        ).is_visible()

        with standard_user_page.expect_download() as download_record:
            standard_user_page.get_by_text("Download record").click()
        download = download_record.value
        assert "TSTA 1_NBRPR" == download.suggested_filename
