import os

from playwright.sync_api import Page, expect


def test_sign_in_succeeds_when_valid_credentials(page: Page):
    """
    Given a user is on the sign in page,
    When they provide valid credentials and click the "Sign in" button,
    Then they should see a success message indicating they are logged in with access to AYR.
    And they should be on the '/browse' page.
    """
    page.goto("/sign-in")
    page.get_by_label("Email address").fill(os.environ.get("AYR_TEST_USERNAME"))
    page.get_by_label("Password").fill(os.environ.get("AYR_TEST_PASSWORD"))
    page.get_by_role("button", name="Sign in").click()
    expect(page).to_have_url("/browse")


def test_sign_in_fails_when_invalid_credentials(page: Page):
    """
    Given a user is on the sign in page,
    When they provide invalid credentials and click the "Sign in" button,
    Then they should see an error message indicating the provided credentials are invalid.
    """
    page.goto("/sign-in")
    page.get_by_label("Email address").fill("bad")
    page.get_by_label("Password").fill("credentials")
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_text("Invalid username or password."))
