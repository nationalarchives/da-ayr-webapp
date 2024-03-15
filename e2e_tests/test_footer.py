import pytest
from playwright.sync_api import Page, expect

service_name = "AYR - Access Your Records – GOV.UK"
# Define list of footer links and their expected URLS

footer_links = [
    (
        "How to use this service",
        "/how-to-use-this-service",
        f"How to use this service – {service_name}",
    ),
    (
        "Terms of use",
        "/terms-of-use",
        f"Terms of use – {service_name}",
    ),
    (
        "Privacy",
        "/privacy",
        f"Privacy – {service_name}",
    ),
    (
        "Cookies policy",
        "/cookies",
        f"Cookies – {service_name}",
    ),
    (
        "Accessibility",
        "/accessibility",
        f"Accessibility – {service_name}",
    ),
]


@pytest.fixture
def setup_page(page: Page):
    page.goto("/")
    yield page


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
