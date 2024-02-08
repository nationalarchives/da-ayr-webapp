from unittest.mock import patch

from flask import url_for


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_sign_out(mock_keycloak, client, mock_standard_user):
    """
    Given a session with `refresh_token` set, and a mocked KeycloakOpenID instance,
    When a request with this session is made to the 'main.sign_out' route,
    Then the response should redirect to the 'main.signed_out' route,
        and the KeycloakOpenID 'logout' method should be called with the refresh token
        and the session should be cleared
    """
    mock_standard_user(client)

    response = client.get(url_for("main.sign_out"))

    assert response.status_code == 302
    assert response.headers["Location"] == url_for("main.signed_out")

    mock_keycloak.return_value.logout.assert_called_once_with(
        "valid_refresh_token"
    )

    with client.session_transaction() as cleared_session:
        assert cleared_session == {}
