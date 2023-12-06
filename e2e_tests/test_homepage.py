import re

from playwright.sync_api import Page, expect

from e2e_tests.utils import block_css_decorator


@block_css_decorator
def test_has_title(page: Page):
    page.goto("/")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("AYR - Access Your Records – GOV.UK"))
