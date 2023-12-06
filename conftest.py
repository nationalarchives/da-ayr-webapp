import pytest


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
