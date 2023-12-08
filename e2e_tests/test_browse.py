import os

from playwright.sync_api import Page

username = os.getenv("AYR_TEST_USERNAME")
password = os.getenv("AYR_TEST_PASSWORD")


def test_has_title(page: Page):
    page.goto("/browse")
    page.get_by_label("Email address").click()
    page.get_by_label("Email address").fill(username)
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in").click()
    assert page.title() == "Browse – AYR - Access Your Records – GOV.UK"


def test_sort_dropdown(page: Page):
    page.goto("/browse")
    page.get_by_label("Email address").click()
    page.get_by_label("Email address").fill(username)
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in").click()
    page.get_by_label("", exact=True).click()
    page.get_by_role("button", name="Search").click()
    page.select_option("#sort", "body-a")
    page.select_option("#sort", "body-b")
    page.select_option("#sort", "series-a")
    page.select_option("#sort", "series-b")
    page.select_option("#sort", "date-first")
    page.select_option("#sort", "date-last")


def test_page_loading(page: Page):
    page.goto("/browse")
    page.get_by_label("Email address").click()
    page.get_by_label("Email address").fill(username)
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_selector(".govuk-heading-l")


def test_filter_functionality(page: Page):
    page.goto("/browse")
    page.get_by_label("Email address").click()
    page.get_by_label("Email address").fill(username)
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in").click()
    page.select_option(
        ".filters-form__transferring-body--select", "Arts Council England"
    )

    records = page.query_selector_all(".govuk-summary-list__value a")
    for record in records:
        assert record


def test_pagination(page: Page):
    page.goto("/browse")
    page.get_by_label("Email address").click()
    page.get_by_label("Email address").fill(username)
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in").click()
    page.click(".govuk-pagination__next")
