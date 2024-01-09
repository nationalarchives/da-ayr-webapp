from playwright.sync_api import Page


def test_can_download_file_by_clicking_button(authenticated_page: Page):
    authenticated_page.goto("/record/d806615f-c37e-48e5-a2f5-2281846cf1a3")
    with authenticated_page.expect_download() as download_record:
        authenticated_page.get_by_text("Download record").click()
    download = download_record.value
    assert "testfile1" == download.suggested_filename
