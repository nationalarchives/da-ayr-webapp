"""
Feature: Browse to record
"""

import re

from playwright.sync_api import Page, expect


def test_browse_to_record(aau_user_page: Page):
    """
    Scenario: Navigate through browse sections to reach a record

    Given the user is on the browse page
    When the user clicks on the first link in the first cell
    Then the URL should match the pattern "/browse/transferring_body/.*"
    When the user clicks on the first link in the second cell
    Then the URL should match the pattern "/browse/series/.*"
    When the user clicks on the first link in the fifth cell
    Then the URL should match the pattern "/browse/consignment/.*"
    When the user clicks on the first link in the second cell
    Then the URL should match the pattern "/record/.*"
    """
    aau_user_page.goto("/browse")

    aau_user_page.get_by_role("cell").first.get_by_role("link").first.click()
    expect(aau_user_page).to_have_url(
        re.compile(r"\/browse\/transferring_body\/.*")
    )

    aau_user_page.get_by_role("cell").nth(1).get_by_role("link").first.click()
    expect(aau_user_page).to_have_url(re.compile(r"\/browse\/series\/.*"))

    aau_user_page.get_by_role("cell").nth(4).get_by_role("link").first.click()
    expect(aau_user_page).to_have_url(re.compile(r"\/browse\/consignment\/.*"))

    aau_user_page.get_by_role("cell").nth(1).get_by_role("link").first.click()
    expect(aau_user_page).to_have_url(re.compile(r"\/record\/.*"))
