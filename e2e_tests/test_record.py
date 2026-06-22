"""
Feature: Record page functionality
"""

from playwright.sync_api import Page, expect


class TestRecord:
    @property
    def route_url(self):
        return "/record"

    def test_record_404_for_no_access(self, standard_user_page: Page):
        """
        Scenario: Accessing a record page without permission results in 404

        Given a standard user with ID of a record in a different transferring body
        When the user navigates to the record page with this ID
        Then the page should display "Page not found"
        """
        record_id = "7ce919c0-9f2b-4133-b41f-f85bdecc6a52"

        standard_user_page.goto(f"{self.route_url}/{record_id}")
        assert standard_user_page.inner_html("text='Page not found'")

    def test_record_aau_users_with_perms_can_see_download_button(
        self, aau_user_page_with_download: Page
    ):
        """
        Scenario: Seeing download button on record page

        Given the user navigates to the record page with ID "100251bb-5b93-48a9-953f-ad5bd9abfbdc"
        When the aau user has the correct group to be able to download
        Then the download button is visible
        """
        record_id = "100251bb-5b93-48a9-953f-ad5bd9abfbdc"
        aau_user_page_with_download.goto(f"{self.route_url}/{record_id}")

        button = aau_user_page_with_download.get_by_role(
            "button", name="Download record"
        )

        expect(button).to_be_visible()

    def test_record_aau_users_without_perms_cant_see_download_button(
        self, aau_user_page: Page
    ):
        """
        Scenario: Seeing download button on record page

        Given the user navigates to the record page with ID "100251bb-5b93-48a9-953f-ad5bd9abfbdc"
        When the aau user does not have the group to be able to download
        Then the download button is NOT visible
        """
        record_id = "100251bb-5b93-48a9-953f-ad5bd9abfbdc"
        aau_user_page.goto(f"{self.route_url}/{record_id}")

        button = aau_user_page.get_by_role("link", name="Download record")

        expect(button).to_be_hidden()

    def test_record_download_record(
        self, standard_user_page_with_download: Page
    ):
        """
        Scenario: Downloading a record

        Given the user navigates to the record page with ID "100251bb-5b93-48a9-953f-ad5bd9abfbdc"
        When the user clicks the "Download record" button
        Then the file "file-a2.txt" should be downloaded
        """
        record_id = "100251bb-5b93-48a9-953f-ad5bd9abfbdc"
        standard_user_page_with_download.goto(f"{self.route_url}/{record_id}")

        with (
            standard_user_page_with_download.expect_download() as download_record
        ):
            standard_user_page_with_download.get_by_role(
                "button", name="Download record"
            ).click()
        download = download_record.value
        assert "file-a2.txt" == download.suggested_filename
