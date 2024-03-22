import pytest
from playwright.sync_api import Page


@pytest.mark.parametrize(
    "url,screenshot_file",
    [
        ("/how-to-use-this-service", "how_to_use_this_service.png"),
        ("/terms-of-use", "terms_of_use.png"),
        ("/privacy", "privacy.png"),
        ("/cookies", "cookies.png"),
        ("/accessibility", "accessibility.png"),
        ("/signed-out", "signed_out.png"),
        ("/", "start.png"),
        ("/browse", "browse.png"),
        (
            "/browse/transferring_body/8ccc8cd1-c0ee-431d-afad-70cf404ba337",
            "browse_transferring_body.png",
        ),
        (
            "/browse/series/8bd7ad22-90d1-4c7f-ae00-645dfd1987cc",
            "browse_series.png",
        ),
        (
            "/browse/consignment/a03363ac-7e7b-4b92-817e-72ba6423edd5",
            "browse_consignment.png",
        ),
        ("/search_results_summary?query=a", "search_results_summary.png"),
        (
            "/search/transferring_body/8ccc8cd1-c0ee-431d-afad-70cf404ba337?query=a&sort=series-asc&search_filter=test",
            "search_transferring_body.png",
        ),
        ("/record/41f94132-dbdf-43e4-a327-cc5bae432f98", "record.png"),
    ],
)
def test_css_no_visual_regression(
    url, screenshot_file, aau_user_page: Page, assert_snapshot
):
    """
    Given a page in the AYR webapp
    When an authenticated user navigates to it
    Then it should look as expected

    If any of these tests break due to intended changes to the design of the page,
    run pytest with `--update-snapshots --headed` flags to update the stored screenshot
    """
    aau_user_page.goto(url)
    aau_user_page.wait_for_load_state("domcontentloaded")
    screenshot = aau_user_page.screenshot(full_page=True)
    assert_snapshot(screenshot, screenshot_file)
