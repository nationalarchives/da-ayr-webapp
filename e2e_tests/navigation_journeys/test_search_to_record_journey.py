"""
Feature: Search to record
"""

import re

from playwright.sync_api import Page, expect


def test_search_results_to_record(aau_user_page: Page):
    """
    Scenario: Navigate from search to a record

    Given the user is on the browse page
    When the user fills the search box with "a"
    And the user clicks the "Search" button
    Then the URL should match the canonical search results route
    When the user clicks on the first record link
    Then the URL should match the pattern "/record/.*"
    """
    aau_user_page.goto("/browse")

    aau_user_page.get_by_role("textbox").first.fill("a")
    aau_user_page.get_by_role("button", name="Search").click()
    expect(aau_user_page).to_have_url(
        re.compile(r".*/search/results.*query=a.*")
    )

    aau_user_page.wait_for_selector("#tbl_result")
    aau_user_page.locator("a.browse-records__file-link").first.click()
    expect(aau_user_page).to_have_url(re.compile(r"\/record\/.*"))
