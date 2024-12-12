import json

import pytest
from flask.testing import FlaskClient
from moto import mock_aws

from app.main.middlewares.log_page_view import log_page_view

HOST = "http://localhost"


@pytest.mark.parametrize(
    "route_path, method, session_object, route_function, expected_response, expected_log",
    [
        (
            "/test_route",
            "GET",
            {"user_id": "test_user"},
            lambda: "Test Response",
            b"Test Response",
            json.loads(
                """{"event": "api_request", "user_id": "test_user", "route": "http://localhost/test_route",
                "method": "GET"}"""
            ),
        ),
        (
            "/anonymous_route",
            "GET",
            {},
            lambda: "Anonymous Response",
            b"Anonymous Response",
            json.loads(
                """{"event": "api_request", "user_id": "anonymous", "route": "http://localhost/anonymous_route",
                "method": "GET"}"""
            ),
        ),
        (
            "/post_route",
            "POST",
            {"user_id": "test_user"},
            lambda: "Post Response",
            b"Post Response",
            json.loads(
                """{"event": "api_request", "user_id": "test_user", "route": "http://localhost/post_route",
                "method": "POST"}"""
            ),
        ),
    ],
)
@mock_aws
def test_log_page_view(
    app,
    client: FlaskClient,
    route_path,
    method,
    session_object,
    route_function,
    expected_response,
    expected_log,
    caplog,
):
    @app.route(route_path, methods=[method])
    @log_page_view
    def dynamic_route():
        return route_function()

    with client.session_transaction() as session:
        session.update(session_object)

    response = client.open(route_path, method=method)

    assert response.status_code == 200
    assert response.data == expected_response

    logged_message = json.loads(caplog.records[0].message)
    assert caplog.records[0].levelname == "INFO"
    assert logged_message == expected_log
