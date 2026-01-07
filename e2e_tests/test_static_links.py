import pytest
from playwright.sync_api import expect


@pytest.mark.health_check
@pytest.mark.parametrize(
    "link_text, expected_url",
    [
        (
            "The National Archives",
            "https://www.nationalarchives.gov.uk/",
        ),
    ],
)
def test_header_link(page, link_text, expected_url):
    """
    Given an unauthenticated user
    When they click a header link
    Then the user is redirected to the associated page
    """
    page.goto("/")
    page.click(f'text="{link_text}"')
    expect(page).to_have_url(expected_url)


@pytest.mark.health_check
@pytest.mark.parametrize(
    "link_text, expected_url",
    [
        (
            "How to use this service",
            "/how-to-use-this-service",
        ),
        (
            "Terms of use",
            "/terms-of-use",
        ),
        (
            "Privacy",
            "/privacy",
        ),
        (
            "Cookies",
            "/cookies",
        ),
        (
            "Accessibility",
            "/accessibility",
        ),
    ],
)
@pytest.mark.health_check
def test_footer_links(page, link_text, expected_url):
    """
    Given an unauthenticated user on the home page
    When they click a footer link
    Then the user is redirected to the associated page
    """
    page.goto("/")
    page.click(f'text="{link_text}"')
    expect(page).to_have_url(expected_url)
