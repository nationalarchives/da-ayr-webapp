import pytest
from playwright.sync_api import Page

from .utils.assertions import assert_matches_snapshot


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
            "/browse/series/93ed0101-2318-45ab-8730-c681958ded7e",
            "browse_series.png",
            {"width": 1280, "height": 4000},
        ),
        (
            "/browse/consignment/2fd4e03e-5913-4c04-b4f2-5a823fafd430",
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
            "/record/123e4567-e89b-12d3-a456-426614174000",
            "record.png",
            {"width": 1280, "height": 4000},
        ),
    ],
)
def test_css_no_visual_regression(
    url, screenshot_file, viewport, aau_user_page: Page, browser_name
):
    """
    Given a page in the AYR webapp
    When an authenticated user navigates to it
    Then it should look as expected on a desktop viewport

    If any of these tests break due to intended changes to the design of the page,
    run pytest with `--update-snapshots --headed` flags to update the stored screenshot
    """

    aau_user_page.set_viewport_size(viewport)
    aau_user_page.goto(url, wait_until="networkidle")
    aau_user_page.wait_for_load_state("domcontentloaded")
    snapshot = aau_user_page.screenshot(full_page=True, type="png")
    assert_matches_snapshot(
        snapshot,
        device="desktop",
        page_name=f"{browser_name}-{screenshot_file}",
    )


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
            "/browse/series/93ed0101-2318-45ab-8730-c681958ded7e",
            "browse_series_mobile.png",
            {"width": 390, "height": 5000},
        ),
        (
            "/browse/consignment/2fd4e03e-5913-4c04-b4f2-5a823fafd430",
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
            "/record/123e4567-e89b-12d3-a456-426614174000",
            "record_mobile.png",
            {"width": 390, "height": 5000},
        ),
    ],
)
def test_css_no_visual_regression_mobile(
    url, screenshot_file, viewport, aau_user_page: Page, browser_name
):
    """
    Given a page in the AYR webapp
    When an authenticated user navigates to it
    Then it should look as expected on a mobile viewport

    If any of these tests break due to intended changes to the design of the page,
    run pytest with `--update-snapshots --headed` flags to update the stored screenshot
    """
    aau_user_page.set_viewport_size(viewport)
    aau_user_page.goto(url, wait_until="networkidle")
    aau_user_page.wait_for_load_state("domcontentloaded")
    snapshot = aau_user_page.screenshot(full_page=True, type="png")
    assert_matches_snapshot(
        snapshot, device="mobile", page_name=f"{browser_name}-{screenshot_file}"
    )
