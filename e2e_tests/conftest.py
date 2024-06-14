import os
import uuid

import keycloak
import pytest
from playwright.sync_api import Page


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


class KeycloakClient:
    def __init__(self, user_type):
        self.user_type = user_type
        self.user_email = f"{uuid.uuid4().hex}{user_type}@test.com"
        self.user_pass = uuid.uuid4().hex
        self.user_first_name = "Test"
        self.user_last_name = "Name"
        self.user_id = None

        self.realm_name = os.environ.get("KEYCLOAK_REALM_NAME")

        self.client_id = os.environ.get("KEYCLOAK_CLIENT_ID")
        self.client_secret = os.environ.get("KEYCLOAK_CLIENT_SECRET")

        self.server_url = os.environ.get("KEYCLOAK_BASE_URI")
        self.auth_url = f"{self.server_url}/realms/{self.realm_name}/protocol/openid-connect/token"
        self.users_url = (
            f"{self.server_url}admin/realms/{self.realm_name}/users"
        )

        self.keycloak_openid = keycloak.KeycloakOpenID(
            server_url=self.server_url,
            client_id=self.client_id,
            realm_name=self.realm_name,
            client_secret_key=self.client_secret,
        )

        self.token = self.keycloak_openid.token(grant_type="client_credentials")
        self.keycload_admin = keycloak.KeycloakAdmin(
            server_url=self.server_url,
            realm_name=self.realm_name,
            token=self.token,
        )

    def get_user_groups(self):
        if self.user_type == "all_access_user":
            return ["/ayr_user_type/view_all"]
        elif self.user_type == "standard_user":
            return [
                "/ayr_user_type/view_dept",
                "/transferring_body_user/Testing A",
            ]
        else:
            return []

    def create_user(self):
        groups = self.get_user_groups()
        user_id = self.keycload_admin.create_user(
            {
                "firstName": self.user_first_name,
                "lastName": self.user_last_name,
                "username": self.user_email,
                "email": self.user_email,
                "enabled": True,
                "groups": groups,
                "credentials": [{"value": self.user_pass, "type": "password"}],
            }
        )
        self.user_id = user_id
        return self.user_id

    def delete_user(self):
        if self.user_id is None:
            return
        return self.keycload_admin.delete_user(user_id=self.user_id)


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
def create_users():
    client_aau = KeycloakClient("all_access_user")
    client_standard = KeycloakClient("standard_user")

    client_aau.create_user()
    client_standard.create_user()

    yield {
        "aau": {
            "username": client_aau.user_email,
            "password": client_aau.user_pass,
        },
        "standard": {
            "username": client_standard.user_email,
            "password": client_standard.user_pass,
        },
    }

    client_aau.delete_user()
    client_standard.delete_user()


@pytest.fixture
def aau_user_page(create_user_page, create_users) -> Page:
    username = create_users["aau"]["username"]
    password = create_users["aau"]["password"]
    page = create_user_page(username, password)
    yield page
    page.goto("/sign-out")


@pytest.fixture
def standard_user_page(create_user_page, create_users) -> Page:
    username = create_users["standard"]["username"]
    password = create_users["standard"]["password"]
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
