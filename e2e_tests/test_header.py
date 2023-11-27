import pytest
from playwright.sync_api import Page, expect

# Define header link and URL

header_link = [
    (
        "The National Archives",
        "https://www.nationalarchives.gov.uk/",
    ),
]


@pytest.fixture
def setup_page(page: Page):
    page.goto("/")
    yield page


@pytest.mark.parametrize("link_text, expected_url", header_link)
def test_header_link(setup_page, link_text, expected_url):
    # locate and click footer link as user would
    setup_page.click(f'text="{link_text}"')

    # Wait for navigation and check URL is correct
    setup_page.wait_for_url(expected_url, timeout=5000)

    # Assertions

    # Check if the text of the link is contained within URL
    expect(setup_page).to_have_url(expected_url)
