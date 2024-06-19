import os

import pytest
from playwright.sync_api import Page

from e2e_tests.utils.user_management import (
    create_aau_keycloak_user as create_aau_keycloak_user_utils,
)
from e2e_tests.utils.user_management import (
    create_standard_keycloak_user as create_standard_keycloak_user_utils,
)
from e2e_tests.utils.user_management import (
    keycloak_admin as keycloak_admin_utils,
)


class Utils:
    @staticmethod
    def get_desktop_page_table_headers(page: Page):
        return page.locator(
            "th:not(.govuk-table--invisible-on-desktop)"
        ).evaluate_all("""els => els.map(e => e.innerText.trim())""")

    @staticmethod
    def get_desktop_page_table_rows(page: Page):
        return page.get_by_role("row").evaluate_all(
            """els => {
                    document.querySelectorAll('.govuk-table--invisible-on-desktop')
                        .forEach(el => el.remove())
                    return els.map(el =>
                        [...el.querySelectorAll('td')].map(e => e.innerText.trim())
                    ).filter(e => e.length > 0)
                }
            """
        )


@pytest.fixture
def utils():
    return Utils


@pytest.fixture
def page(page, request) -> Page:
    page.context.set_default_timeout(5000)
    if "test_css_" not in request.node.name and callable(request.node.obj):

        def route_intercept(route):
            if route.request.resource_type == "stylesheet":
                return route.abort()
            return route.continue_()

        page.route("**/*", route_intercept)

    return page


@pytest.fixture
def create_user_page(
    page, browser_name
) -> (
    Page
):  # FIXME: browser_name specified until https://github.com/microsoft/playwright-pytest/issues/172 fixed
    # so that multiple browser flags in cli are honoured
    def _create_user_page(username, password) -> Page:
        page.goto("/sign-in")
        page.get_by_label("Email address").fill(username)
        page.get_by_label("Password").fill(password)
        page.get_by_role("button", name="Sign in").click()
        return page

    return _create_user_page


@pytest.fixture(scope="session")
def keycloak_admin():
    realm_name = os.environ.get("KEYCLOAK_REALM_NAME")
    client_id = os.environ.get("KEYCLOAK_CLIENT_ID")
    client_secret = os.environ.get("KEYCLOAK_CLIENT_SECRET")
    server_url = os.environ.get("KEYCLOAK_BASE_URI")
    return keycloak_admin_utils(
        realm_name, client_id, client_secret, server_url
    )


@pytest.fixture(scope="session")
def create_aau_keycloak_user(keycloak_admin):
    user_id, user_email, user_pass = create_aau_keycloak_user_utils(
        keycloak_admin
    )
    yield user_email, user_pass
    keycloak_admin.delete_user(user_id=user_id)


@pytest.fixture(scope="session")
def create_standard_keycloak_user(keycloak_admin):
    user_id, user_email, user_pass = create_standard_keycloak_user_utils(
        keycloak_admin
    )
    yield user_email, user_pass
    keycloak_admin.delete_user(user_id=user_id)


@pytest.fixture
def aau_user_page(create_user_page, create_aau_keycloak_user) -> Page:
    username, password = create_aau_keycloak_user
    page = create_user_page(username, password)
    yield page
    page.goto("/sign-out")


@pytest.fixture
def standard_user_page(create_user_page, create_standard_keycloak_user) -> Page:
    username, password = create_standard_keycloak_user
    page = create_user_page(username, password)
    yield page
    page.goto("/sign-out")


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
        "user_agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "ignore_https_errors": True,
        "java_script_enabled": False,
    }
