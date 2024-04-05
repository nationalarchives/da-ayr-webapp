import os

import pytest
from playwright.sync_api import Page, Playwright


@pytest.fixture(params=["firefox", "chromium", "webkit"])
def aau_user_page(
    request, playwright: Playwright, browser_context_args
) -> Page:
    browser_type = request.param
    if browser_type == "firefox":
        browser = playwright.firefox
    elif browser_type == "chromium":
        browser = playwright.chromium
    elif browser_type == "webkit":
        browser = playwright.webkit
    else:
        raise ValueError(f"Unsupported browser type: {browser_type}")

    browser_instance = browser.launch()

    context = browser_instance.new_context(**browser_context_args)
    page = context.new_page()
    page.goto("/sign-in")
    page.get_by_label("Email address").fill(
        os.environ.get("AYR_AAU_USER_USERNAME")
    )
    page.get_by_label("Password").fill(os.environ.get("AYR_AAU_USER_PASSWORD"))
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url("/browse")
    yield page

    context.close()
    browser_instance.close()


@pytest.fixture(params=["firefox", "chromium", "webkit"])
def standard_user_page(
    request, playwright: Playwright, browser_context_args
) -> Page:
    browser_type = request.param
    if browser_type == "firefox":
        browser = playwright.firefox
    elif browser_type == "chromium":
        browser = playwright.chromium
    elif browser_type == "webkit":
        browser = playwright.webkit
    else:
        raise ValueError(f"Unsupported browser type: {browser_type}")

    browser_instance = browser.launch()

    context = browser_instance.new_context(**browser_context_args)
    page = context.new_page()
    page.goto("/sign-in")
    page.get_by_label("Email address").fill(
        os.environ.get("AYR_STANDARD_USER_USERNAME")
    )
    page.get_by_label("Password").fill(
        os.environ.get("AYR_STANDARD_USER_PASSWORD")
    )
    page.get_by_role("button", name="Sign in").click()
    yield page

    context.close()
    browser_instance.close()


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


@pytest.fixture()
def page(request, page) -> Page:
    page.context.set_default_timeout(5000)
    if "test_css_" not in request.node.name and callable(request.node.obj):

        def route_intercept(route):
            if route.request.resource_type == "stylesheet":
                return route.abort()
            return route.continue_()

        page.route("**/*", route_intercept)
    return page


# @pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
# def test_example(aau_user_page, browser_name):
#     # Use aau_user_page fixture to login
#     # Use browser_name parameter to select the browser
#     assert aau_user_page.title() == "Expected Title"
