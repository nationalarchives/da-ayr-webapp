import re
from unittest.mock import patch

from flask import render_template, url_for


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_sign_out(mock_keycloak, app, client, mock_standard_user):
    """
    Given a session with `refresh_token` set, and a mocked KeycloakOpenID instance,
    When a request with this session is made to the 'main.sign_out' route,
    Then the response should redirect to the 'main.signed_out' route,
        and the KeycloakOpenID 'logout' method should be called with the refresh token
        and the session should be cleared
    """
    mock_standard_user(client)

    @app.route("/sign-out-test-form")
    def sign_out_test_form():
        return render_template("base.html", authenticated_view=True)

    form_page = client.get("/sign-out-test-form")
    csrf_token = re.search(
        r'name="csrf_token" value="([^"]+)"',
        form_page.get_data(as_text=True),
    ).group(1)

    response = client.post(
        url_for("main.sign_out"), data={"csrf_token": csrf_token}
    )

    assert response.status_code == 302
    assert response.headers["Location"] == url_for("main.signed_out")

    mock_keycloak.return_value.logout.assert_called_once_with(
        "valid_refresh_token"
    )

    with client.session_transaction() as cleared_session:
        assert cleared_session == {}


def test_sign_out_requires_csrf_token(client, mock_standard_user):
    mock_standard_user(client)

    response = client.post(url_for("main.sign_out"))

    assert response.status_code == 400


def test_sign_out_rejects_get(client, mock_standard_user):
    mock_standard_user(client)

    response = client.get(url_for("main.sign_out"))

    assert response.status_code == 405
