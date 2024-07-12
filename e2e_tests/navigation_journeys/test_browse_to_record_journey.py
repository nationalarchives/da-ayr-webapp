import re

from playwright.sync_api import Page, expect


def test_browse_to_record(aau_user_page: Page):
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
