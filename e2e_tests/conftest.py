import os
import uuid

import keycloak
import pytest
from playwright.sync_api import Page


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "health_check: Health check tests for monitoring"
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

    def get_desktop_page_transferring_body_table_headers(page: Page):
        return page.locator(
            "th:not(.govuk-table--invisible-on-desktop)"
        ).evaluate_all(
            """
            els => els
                .map(e => e.innerText.trim())
                .filter(text => text === 'Found within' || text === 'Search results')
        """
        )

    def get_desktop_page_transferring_body_inner_table_headers(page: Page):
        return page.locator(
            "th:not(.govuk-table--invisible-on-desktop)"
        ).evaluate_all(
            """
            els => els
                .map(e => e.innerText.trim())
                .filter(text => text !== 'Found within' && text !== 'Search results')
        """
        )

    def get_desktop_page_table_metadata(page: Page):
        return page.locator("tbody tbody").evaluate_all(
            """rows => rows.map(row =>
        Array.from(row.querySelectorAll('.govuk-table__cell')).map(cell => cell.innerText.trim())
    )"""
        )


@pytest.fixture
def utils():
    return Utils


@pytest.fixture
def page(page, request) -> Page:
    page.context.set_default_timeout(15000)
    if "test_css_" not in request.node.name and callable(request.node.obj):

        def route_intercept(route):
            if route.request.resource_type == "stylesheet":
                return route.abort()
            return route.continue_()

        page.route("**/*", route_intercept)

    return page


@pytest.fixture
def create_user_page(
    page,
) -> (
    Page
):  # FIXME: browser_name specified until https://github.com/microsoft/playwright-pytest/issues/172 fixed
    # so that multiple browser flags in cli are honoured
    def _create_user_page(username, password) -> Page:
        page.goto("/sign-in")
        if page.locator("label:has-text('Email address')").count() > 0:
            page.get_by_label("Email address").first.fill(username)
        elif page.locator("label:has-text('Email')").count() > 0:
            page.get_by_label("Email").first.fill(username)
        else:
            page.get_by_label("Username or email").first.fill(username)
        page.get_by_role("textbox", name="Password").fill(password)
        page.get_by_role("button", name="Sign in").click()
        return page

    return _create_user_page


@pytest.fixture(scope="session")
def keycloak_admin():
    realm_name = os.environ.get("KEYCLOAK_REALM_NAME")
    client_id = os.environ.get("KEYCLOAK_CLIENT_ID")
    client_secret = os.environ.get("KEYCLOAK_CLIENT_SECRET")
    server_url = os.environ.get("KEYCLOAK_BASE_URI")

    keycloak_openid = keycloak.KeycloakOpenID(
        server_url=server_url,
        client_id=client_id,
        realm_name=realm_name,
        client_secret_key=client_secret,
        verify=False,
    )

    token = keycloak_openid.token(grant_type="client_credentials")
    keycloak_admin = keycloak.KeycloakAdmin(
        server_url=server_url,
        realm_name=realm_name,
        token=token,
    )
    return keycloak_admin


@pytest.fixture(scope="session")
def create_keycloak_user(keycloak_admin):
    def _create_keycloak_user(groups, user_type):
        user_email = f"{uuid.uuid4().hex}{user_type}@test.com"
        user_pass = uuid.uuid4().hex
        user_first_name = "Test"
        user_last_name = "Name"
        user_id = keycloak_admin.create_user(
            {
                "firstName": user_first_name,
                "lastName": user_last_name,
                "username": user_email,
                "email": user_email,
                "enabled": True,
                "groups": groups,
                "credentials": [{"value": user_pass, "type": "password"}],
            }
        )
        return user_id, user_email, user_pass

    return _create_keycloak_user


@pytest.fixture(scope="session")
def create_aau_keycloak_user(keycloak_admin, create_keycloak_user):
    user_groups = ["/ayr_user_type/view_all"]
    user_type = "aau"
    user_id, user_email, user_pass = create_keycloak_user(
        user_groups, user_type
    )

    yield user_email, user_pass

    keycloak_admin.delete_user(user_id=user_id)


@pytest.fixture(scope="session")
def create_standard_keycloak_user(keycloak_admin, create_keycloak_user):
    user_groups = [
        "/ayr_user_type/view_dept",
        "/transferring_body_user/Testing A",
    ]
    user_type = "standard"
    user_id, user_email, user_pass = create_keycloak_user(
        user_groups, user_type
    )

    yield user_email, user_pass

    keycloak_admin.delete_user(user_id=user_id)


@pytest.fixture(scope="session")
def create_aau_keycloak_user_with_download(
    keycloak_admin, create_keycloak_user
):
    user_groups = ["/ayr_user_type/view_all", "/ayr_user_type/download"]
    user_type = "aau"
    user_id, user_email, user_pass = create_keycloak_user(
        user_groups, user_type
    )

    yield user_email, user_pass

    keycloak_admin.delete_user(user_id=user_id)


@pytest.fixture(scope="session")
def create_standard_keycloak_user_with_download(
    keycloak_admin, create_keycloak_user
):
    user_groups = [
        "/ayr_user_type/view_dept",
        "/ayr_user_type/download",
        "/transferring_body_user/Testing A",
    ]
    user_type = "standard"
    user_id, user_email, user_pass = create_keycloak_user(
        user_groups, user_type
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


@pytest.fixture
def aau_user_page_with_download(
    create_user_page, create_aau_keycloak_user_with_download
) -> Page:
    username, password = create_aau_keycloak_user_with_download
    page = create_user_page(username, password)
    yield page
    page.goto("/sign-out")


@pytest.fixture
def standard_user_page_with_download(
    create_user_page, create_standard_keycloak_user_with_download
) -> Page:
    username, password = create_standard_keycloak_user_with_download
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
