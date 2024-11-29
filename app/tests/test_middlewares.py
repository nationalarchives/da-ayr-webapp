import pytest
from flask.testing import FlaskClient
from moto import mock_aws

from app.main.middlewares.log_page_view import log_page_view


@pytest.mark.parametrize(
    "route_path, method, session_object, route_function, expected_response, expected_log",
    [
        (
            "/test_route",
            "GET",
            {"user_id": "test_user"},
            lambda: "Test Response",
            b"Test Response",
            '{"event": "page_view", "user_id": "test_user", "route": "/test_route", "method": "GET"}',
        ),
        (
            "/anonymous_route",
            "GET",
            {},
            lambda: "Anonymous Response",
            b"Anonymous Response",
            '{"event": "page_view", "user_id": "anonymous", "route": "/anonymous_route", "method": "GET"}',
        ),
        (
            "/post_route",
            "POST",
            {"user_id": "test_user"},
            lambda: "Post Response",
            b"Post Response",
            '{"event": "page_view", "user_id": "test_user", "route": "/post_route", "method": "POST"}',
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

    assert caplog.records[0].levelname == "INFO"
    assert caplog.records[0].message == expected_log
