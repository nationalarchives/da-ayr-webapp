import re

from playwright.sync_api import Page, expect


def test_search_to_record(aau_user_page: Page):
    """
    Given a user on the search transferring body page
    When they interact with the search form and submit a query with multiple search terms
    Then the table should contain the expected headers and entries.
    """
    aau_user_page.goto("/browse")

    aau_user_page.get_by_role("textbox").first.fill("a")
    aau_user_page.get_by_role("button", name="Search").click()
    expect(aau_user_page).to_have_url("search_results_summary?query=a")

    aau_user_page.get_by_role("cell").first.get_by_role("link").first.click()
    expect(aau_user_page).to_have_url(
        re.compile(r"\/search\/transferring_body\/.*")
    )

    aau_user_page.get_by_role("cell").nth(2).get_by_role("link").first.click()
    expect(aau_user_page).to_have_url(re.compile(r"\/record\/.*"))
