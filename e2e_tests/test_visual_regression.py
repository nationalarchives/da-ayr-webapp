import pytest
from playwright.sync_api import Page


@pytest.mark.parametrize(
    "url,screenshot_file,viewport",
    [
        (
            "/how-to-use-this-service",
            "how_to_use_this_service.png",
            {"width": 1280, "height": 4000},
        ),
        ("/terms-of-use", "terms_of_use.png", {"width": 1280, "height": 4000}),
        ("/privacy", "privacy.png", {"width": 1280, "height": 4000}),
        ("/cookies", "cookies.png", {"width": 1280, "height": 4000}),
        (
            "/accessibility",
            "accessibility.png",
            {"width": 1280, "height": 4000},
        ),
        ("/signed-out", "signed_out.png", {"width": 1280, "height": 4000}),
        ("/", "start.png", {"width": 1280, "height": 4000}),
        ("/browse", "browse.png", {"width": 1280, "height": 4000}),
        (
            "/browse/transferring_body/8ccc8cd1-c0ee-431d-afad-70cf404ba337",
            "browse_transferring_body.png",
            {"width": 1280, "height": 4000},
        ),
        (
            "/browse/series/8bd7ad22-90d1-4c7f-ae00-645dfd1987cc",
            "browse_series.png",
            {"width": 1280, "height": 4000},
        ),
        (
            "/browse/consignment/a03363ac-7e7b-4b92-817e-72ba6423edd5",
            "browse_consignment.png",
            {"width": 1280, "height": 4000},
        ),
        (
            "/search_results_summary?query=a",
            "search_results_summary.png",
            {"width": 1280, "height": 4000},
        ),
        (
            "/search/transferring_body/8ccc8cd1-c0ee-431d-afad-70cf404ba337?query=a&sort=series-asc&search_filter=test",
            "search_transferring_body.png",
            {"width": 1280, "height": 4000},
        ),
        (
            "/record/41f94132-dbdf-43e4-a327-cc5bae432f98",
            "record.png",
            {"width": 1280, "height": 4000},
        ),
    ],
)
def test_css_no_visual_regression(
    url, screenshot_file, viewport, aau_user_page: Page, assert_snapshot
):
    """
    Given a page in the AYR webapp
    When an authenticated user navigates to it
    Then it should look as expected on a desktop viewport

    If any of these tests break due to intended changes to the design of the page,
    run pytest with `--update-snapshots --headed` flags to update the stored screenshot
    """
    aau_user_page.set_viewport_size(viewport)
    aau_user_page.goto(url)
    aau_user_page.wait_for_load_state("domcontentloaded")
    screenshot = aau_user_page.screenshot(full_page=True)
    assert_snapshot(screenshot, name=screenshot_file)


@pytest.mark.parametrize(
    "url,screenshot_file,viewport",
    [
        (
            "/how-to-use-this-service",
            "how_to_use_this_service_mobile.png",
            {"width": 390, "height": 5000},
        ),
        (
            "/terms-of-use",
            "terms_of_use_mobile.png",
            {"width": 390, "height": 5000},
        ),
        ("/privacy", "privacy_mobile.png", {"width": 390, "height": 5000}),
        ("/cookies", "cookies_mobile.png", {"width": 390, "height": 5000}),
        (
            "/accessibility",
            "accessibility_mobile.png",
            {"width": 390, "height": 5000},
        ),
        (
            "/signed-out",
            "signed_out_mobile.png",
            {"width": 390, "height": 5000},
        ),
        ("/", "start_mobile.png", {"width": 390, "height": 5000}),
        ("/browse", "browse_mobile.png", {"width": 390, "height": 5000}),
        (
            "/browse/transferring_body/8ccc8cd1-c0ee-431d-afad-70cf404ba337",
            "browse_transferring_body_mobile.png",
            {"width": 390, "height": 5000},
        ),
        (
            "/browse/series/8bd7ad22-90d1-4c7f-ae00-645dfd1987cc",
            "browse_series_mobile.png",
            {"width": 390, "height": 5000},
        ),
        (
            "/browse/consignment/a03363ac-7e7b-4b92-817e-72ba6423edd5",
            "browse_consignment_mobile.png",
            {"width": 390, "height": 5000},
        ),
        (
            "/search_results_summary?query=a",
            "search_results_summary_mobile.png",
            {"width": 390, "height": 5000},
        ),
        (
            "/search/transferring_body/8ccc8cd1-c0ee-431d-afad-70cf404ba337?query=a&sort=series-asc&search_filter=test",
            "search_transferring_body_mobile.png",
            {"width": 390, "height": 5000},
        ),
        (
            "/record/41f94132-dbdf-43e4-a327-cc5bae432f98",
            "record_mobile.png",
            {"width": 390, "height": 5000},
        ),
    ],
)
def test_css_no_visual_regression_mobile(
    url, screenshot_file, viewport, aau_user_page: Page, assert_snapshot
):
    """
    Given a page in the AYR webapp
    When an authenticated user navigates to it
    Then it should look as expected on a mobile viewport

    If any of these tests break due to intended changes to the design of the page,
    run pytest with `--update-snapshots --headed` flags to update the stored screenshot
    """
    aau_user_page.set_viewport_size(viewport)
    aau_user_page.goto(url)
    aau_user_page.wait_for_load_state("domcontentloaded")
    screenshot = aau_user_page.screenshot(full_page=True)
    assert_snapshot(screenshot, name=screenshot_file)
