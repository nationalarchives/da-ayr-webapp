import uuid

import keycloak


def keycloak_admin(realm_name, client_id, client_secret, server_url):
    keycloak_openid = keycloak.KeycloakOpenID(
        server_url=server_url,
        client_id=client_id,
        realm_name=realm_name,
        client_secret_key=client_secret,
    )
    token = keycloak_openid.token(grant_type="client_credentials")
    keycload_admin = keycloak.KeycloakAdmin(
        server_url=server_url,
        realm_name=realm_name,
        token=token,
    )
    return keycload_admin


def create_keycloak_user(keycloak_admin, groups, user_type):
    user_email = f"{uuid.uuid4().hex}{user_type}@test.com"
    user_pass = uuid.uuid4().hex
    user_first_name = "Test"
    user_last_name = "Name"
    user_id = keycloak_admin.create_user(
        {
            "firstName": user_first_name,
            "lastName": user_last_name,
            "username": user_email,
            "email": user_email,
            "enabled": True,
            "groups": groups,
            "credentials": [{"value": user_pass, "type": "password"}],
        }
    )
    return user_id, user_email, user_pass


def create_aau_keycloak_user(keycloak_admin):
    user_groups = ["/ayr_user_type/view_all"]
    user_type = "aau"
    user_id, user_email, user_pass = create_keycloak_user(
        keycloak_admin, user_groups, user_type
    )
    return user_id, user_email, user_pass


def create_standard_keycloak_user(keycloak_admin):
    user_groups = [
        "/ayr_user_type/view_dept",
        "/transferring_body_user/Testing A",
    ]
    user_type = "standard"
    user_id, user_email, user_pass = create_keycloak_user(
        keycloak_admin, user_groups, user_type
    )
    return user_id, user_email, user_pass


def delete_keycloak_user(keycloak_admin, user_id):
    return keycloak_admin.delete(user_id=user_id)
