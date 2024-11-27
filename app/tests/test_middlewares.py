from unittest.mock import MagicMock, patch

import pytest

from app.main.middlewares.log_page_view import log_page_view


@pytest.mark.parametrize(
    "user_id, method, expected_user_id",
    [
        ("12345", "GET", "12345"),
        (None, "POST", "anonymous"),
    ],
)
@patch("app.main.middlewares.log_page_view.session")
@patch("app.main.middlewares.log_page_view.current_app")
def test_log_page_view(
    mock_current_app, mock_session, app, user_id, method, expected_user_id
):
    """
    Test that the log page view middleware calls the current_app.audit_logger with correct values
    """
    mock_session.get.return_value = user_id
    mock_current_app.audit_logger.info = MagicMock()
    view_name = "/log_page_view"

    @app.route(view_name)
    @log_page_view
    def protected_view():
        return "Foobar"

    with app.test_client() as client:
        response = client.get(view_name)

    assert response == "Foobar"
    mock_current_app.audit_logger.info.assert_called_once_with({})
