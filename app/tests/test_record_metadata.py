# import re
# from playwright.sync_api import Page, expect


# def test_page_title_and_header(page: Page):
#     page.goto("/record")
#     expect(page).to_have_title(
#         re.compile("Record – AYR - Access Your Records – GOV.UK")
#     )
#     expect(page.get_by_text("Record metadata")).to_be_visible()


# def test_back_link(page: Page):
#     page.goto("/record")
#     page.get_by_role("link", name="Back", exact=True).click()
#     page.wait_for_url("/")
#     page.close()
