from unittest.mock import patch

from flask import url_for


@patch("app.main.routes.keycloak.KeycloakOpenID")
def test_logout(mock_keycloak_openid, client):
    """
    Given a session with `refresh_token` set, and a mocked KeycloakOpenID instance,
    When a request with this session is made to the 'main.logout' route,
    Then the response should redirect to the 'main.signed_out' route,
        and the KeycloakOpenID 'logout' method should be called with the refresh token
        and the session should be cleared
    """
    with client.session_transaction() as session:
        session["refresh_token"] = "mock_refresh_token"

    response = client.get(url_for("main.logout"))

    assert response.status_code == 302
    assert response.headers["Location"] == url_for("main.signed_out")

    mock_keycloak_openid.return_value.logout.assert_called_once_with(
        "mock_refresh_token"
    )

    with client.session_transaction() as cleared_session:
        assert cleared_session == {}
