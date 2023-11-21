import os

import pytest


@pytest.fixture()
def authenticated_page(page):
    page.goto("/sign-in")
    page.get_by_label("Email address").fill(os.environ.get("AYR_TEST_USERNAME"))
    page.get_by_label("Password").fill(os.environ.get("AYR_TEST_PASSWORD"))
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url("/poc-search-view")
    return page
