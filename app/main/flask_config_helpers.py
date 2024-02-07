import keycloak
from flask import current_app


def get_keycloak_instance_from_flask_config():
    return keycloak.KeycloakOpenID(
        server_url=current_app.config["KEYCLOAK_BASE_URI"],
        client_id=current_app.config["KEYCLOAK_CLIENT_ID"],
        realm_name=current_app.config["KEYCLOAK_REALM_NAME"],
        client_secret_key=current_app.config["KEYCLOAK_CLIENT_SECRET"],
    )
