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


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Fixture for configuring Playwright browser context arguments.
    This fixture is used to customize browser context arguments for Playwright
    browser instances. It sets the 'ignore_https_errors' option to True, which
    allows ignoring HTTPS errors, To disable JS set 'java_script_enabled' to False, which
    disables JavaScript in the browser context.
    Parameters:
        browser_context_args (dict): The default browser context arguments.
    Returns:
        dict: Updated browser context arguments with customized settings.
    """
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "java_script_enabled": False,
    }


@pytest.fixture(autouse=True)
def apply_block_css_decorator(request, page):
    if "test_css_" not in request.node.name and callable(request.node.obj):
        request.node.obj = block_css_decorator(request.node.obj)(page)
