import os
from typing import Dict, List

import keycloak
from flask import current_app


def get_user_transferring_body_keycloak_groups(groups: List[str]) -> List[str]:
    """
    Returns a list of transferring body group names based on a list of keycloak
    user group names

    Returns:
        List[str]: return list of transferring bodies
    """
    users_transferring_bodies = []
    for group in groups:
        if not group.startswith("/transferring_body_user/"):
            continue
        split_str = os.path.split(group)

        transferring_body = split_str[1].strip()
        if len(transferring_body) > 0:
            users_transferring_bodies.append(transferring_body)
    return users_transferring_bodies


def get_user_groups(access_token: str) -> List[str]:
    if not access_token:
        return []

    decoded_token = _decode_token(access_token)

    if not decoded_token["active"]:
        return []

    return decoded_token["groups"]


def _decode_token(access_token: str) -> Dict[str, str]:
    keycloak_openid = keycloak.KeycloakOpenID(
        server_url=current_app.config["KEYCLOAK_BASE_URI"],
        client_id=current_app.config["KEYCLOAK_CLIENT_ID"],
        realm_name=current_app.config["KEYCLOAK_REALM_NAME"],
        client_secret_key=current_app.config["KEYCLOAK_CLIENT_SECRET"],
    )

    decoded_token = keycloak_openid.introspect(access_token)

    return decoded_token
