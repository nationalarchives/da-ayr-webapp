from unittest.mock import patch

from app.main.flask_config_helpers import (
    get_keycloak_instance_from_flask_config,
)


@patch("app.main.flask_config_helpers.keycloak.KeycloakOpenID")
def test_get_keycloak_instance_from_flask_config(mock_keycloak_open_id, app):
    mock_keycloak_open_id.return_value = "foo"

    assert get_keycloak_instance_from_flask_config() == "foo"

    mock_keycloak_open_id.assert_called_once_with(
        server_url=app.config["KEYCLOAK_BASE_URI"],
        client_id=app.config["KEYCLOAK_CLIENT_ID"],
        realm_name=app.config["KEYCLOAK_REALM_NAME"],
        client_secret_key=app.config["KEYCLOAK_CLIENT_SECRET"],
    )
