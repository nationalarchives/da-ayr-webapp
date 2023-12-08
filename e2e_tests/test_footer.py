import pytest
from playwright.sync_api import Page, expect

from e2e_tests.utils import block_css_decorator

# Define list of footer links and their expected URLS

footer_links = [
    (
        "Terms of use",
        "/terms-of-use",
        "Terms of use – AYR - Access Your Records – GOV.UK ",
    ),
    (
        "Privacy",
        "/privacy",
        "Privacy notice – AYR - Access Your Records – GOV.UK ",
    ),
    (
        "Cookies policy",
        "/cookies",
        "Cookies – AYR - Access Your Records – GOV.UK",
    ),
    (
        "Accessibility",
        "/accessibility",
        "Accessibility statement – AYR - Access Your Records – GOV.UK",
    ),
]


@pytest.fixture
def setup_page(page: Page):
    page.goto("/")
    return page


@pytest.mark.parametrize(
    "link_text, expected_url, expected_title", footer_links
)
def test_footer_links(setup_page, link_text, expected_url, expected_title):
    # locate and click footer link as user would

    setup_page.click(f'text="{link_text}"')

    # Wait for navigation and check URL is correct

    setup_page.wait_for_url(expected_url, timeout=5000)

    # Assertions

    # Check if the text of the link is contained within title of the page

    expect(setup_page).to_have_title(expected_title)
