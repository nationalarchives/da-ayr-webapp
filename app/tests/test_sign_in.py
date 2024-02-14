from unittest.mock import patch


@patch("app.main.routes.get_keycloak_instance_from_flask_config")
def test_sign_in(mock_keycloak, client):
    mock_keycloak.return_value.auth_url.return_value = "keycloak_auth_url"

    response = client.get("/sign-in")

    assert response.status_code == 302
    assert response.headers["Location"] == "keycloak_auth_url"

    mock_keycloak.return_value.auth_url.assert_called_once_with(
        redirect_uri="http://localhost/callback",
        scope="group_mapper_client_scope",
    )
