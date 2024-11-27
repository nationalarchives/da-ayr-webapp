import json
from unittest.mock import MagicMock

import pytest
from flask import current_app
from flask.testing import FlaskClient

from app.main.middlewares.log_page_view import log_page_view


@pytest.mark.parametrize(
    "route_path, method, user_id_in_session, route_function, expected_response, expected_log_data",
    [
        (
            "/test_route",
            "GET",
            "test_user",
            lambda: "Test Response",
            b"Test Response",
            {
                "event": "page_view",
                "user_id": "test_user",
                "route": "/test_route",
                "method": "GET",
            },
        ),
        (
            "/anonymous_route",
            "GET",
            None,
            lambda: "Anonymous Response",
            b"Anonymous Response",
            {
                "event": "page_view",
                "user_id": "anonymous",
                "route": "/anonymous_route",
                "method": "GET",
            },
        ),
        (
            "/post_route",
            "POST",
            "test_user",
            lambda: "Post Response",
            b"Post Response",
            {
                "event": "page_view",
                "user_id": "test_user",
                "route": "/post_route",
                "method": "POST",
            },
        ),
    ],
)
def test_log_page_view(
    app,
    client: FlaskClient,
    route_path,
    method,
    user_id_in_session,
    route_function,
    expected_response,
    expected_log_data,
):
    mock_logger = MagicMock()

    @app.route(route_path, methods=[method])
    @log_page_view
    def dynamic_route():
        return route_function()

    with app.app_context():
        current_app.audit_logger = mock_logger

    if user_id_in_session is not None:
        with client.session_transaction() as session:
            session["user_id"] = user_id_in_session

    response = client.open(route_path, method=method)

    assert response.status_code == 200
    assert response.data == expected_response

    mock_logger.info.assert_called_once_with(json.dumps(expected_log_data))
