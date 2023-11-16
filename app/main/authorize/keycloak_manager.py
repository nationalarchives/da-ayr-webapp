import os

import keycloak
from flask import current_app, session


def decode_token(access_token):
    keycloak_openid = keycloak.KeycloakOpenID(
        server_url=current_app.config["KEYCLOAK_BASE_URI"],
        client_id=current_app.config["KEYCLOAK_CLIENT_ID"],
        realm_name=current_app.config["KEYCLOAK_REALM_NAME"],
        client_secret_key=current_app.config["KEYCLOAK_CLIENT_SECRET"],
    )

    decoded_token = keycloak_openid.introspect(access_token)

    return decoded_token


def get_user_transferring_body_groups():
    """
    function that returns list of transferring body group names based on assignment of user group in keycloak for a user

    User has user group assigned in keycloak, keycloak user groups are linked to transferring bodies
    Based on active access token of user, user groups are extracted and list of user groups details retrieved

    Returns:
        List[str]: return list of transferring bodies
    """

    access_token = session.get("access_token")
    if not access_token:
        return []
    decoded_token = decode_token(access_token)
    if not decoded_token["active"]:
        return []

    groups = decoded_token["groups"]
    users_transferring_bodies = []
    for group in groups:
        if not group.startswith("/transferring_body_user/"):
            continue
        split_str = os.path.split(group)

        if len(split_str) == 1:
            continue

        transferring_body = split_str[1].strip()
        users_transferring_bodies.append(transferring_body)
    return users_transferring_bodies
