import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="module")
def browser_context():
    with sync_playwright() as p:
        playwright = p
        browser = playwright.chromium.launch(headless=False)

        context = browser.new_context(
            ignore_https_errors=True,
            # java_script_enabled=False
        )

        yield context

        context.close()
        browser.close()


@pytest.fixture
def page(browser_context):
    return browser_context.new_page()


def test_sorting_dropdown(page):
    page.goto("/browse")
    page.select_option("#sort", "published")


def test_has_title(page):
    page.goto("/browse")
    print(page.title)
    assert page.title() == "Browse – AYR - Access Your Records – GOV.UK"


def test_pagination(page):
    page.goto("/browse")
    page.click(".govuk-pagination__next")


def test_page_loading(page):
    page.goto("/browse")
    page.wait_for_selector(".govuk-heading-l")
