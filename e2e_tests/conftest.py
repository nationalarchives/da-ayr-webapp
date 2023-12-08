import os

import pytest

from e2e_tests.utils import block_css_decorator


@pytest.fixture()
def authenticated_page(page):
    page.goto("/sign-in")
    page.get_by_label("Email address").fill(os.environ.get("AYR_TEST_USERNAME"))
    page.get_by_label("Password").fill(os.environ.get("AYR_TEST_PASSWORD"))
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url("/poc-search-view")
    return page


@pytest.fixture(autouse=True)
def apply_block_css_decorator(request, page):
    if "test_css_" not in request.node.name and callable(request.node.obj):
        request.node.obj = block_css_decorator(request.node.obj)(page)
