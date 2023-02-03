import logging
from typing import Iterator

import requests
from django.contrib.auth.models import Group, User
from keycloak import KeycloakOpenID
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from app.models import ProxyUser
from project import settings
from project.settings import KEYCLOACK_REALM_BASE_URI

logger = logging.getLogger(__name__)


class AYRAuthenticationBackend(OIDCAuthenticationBackend):
    def __init__(self, *args, **kwargs):
        """Initialize settings."""
        super().__init__(*args, **kwargs)
        self.UserModel = ProxyUser

    def create_user(self, claims: dict) -> User:
        logger.info("creating user")
        user = super(AYRAuthenticationBackend, self).create_user(claims)
        # add user to groups
        for group in self.iter_group_objects(claims):
            group.user_set.add(user)
        return user

    def update_user(self, user: User, claims: dict) -> User:
        group_names = list(self.iter_resource_names(claims))
        # ensure user belongs to all the groups they are supposed to
        for group_name in group_names:
            if not user.groups.filter(name=group_name).exists():
                group = Group.objects.get(name=group_name)
                group.user_set.add(user)
        # ensure user doesn't belong to more groups than they should
        for user_group in user.groups.all():
            if user_group.name not in group_names:
                user_group.user_set.remove(user)
        return user

    def get_userinfo(self, access_token, id_token, payload):
        """Return user details dictionary. The id_token and payload are not used in
        the default implementation, but may be used when overriding this method"""

        user_response = requests.get(
            self.OIDC_OP_USER_ENDPOINT,
            headers={"Authorization": "Bearer {0}".format(access_token)},
            verify=self.get_settings("OIDC_VERIFY_SSL", True),
            timeout=self.get_settings("OIDC_TIMEOUT", None),
            proxies=self.get_settings("OIDC_PROXY", None),
        )
        user_response.raise_for_status()
        user_info = user_response.json()
        # this is a workaround for a bug with Keycloack API that doesn't return roles from info endpoint
        uma_permissions = self.get_uma_permissions(access_token)
        user_info["permissions"] = uma_permissions
        return user_info

    def get_uma_permissions(self, access_token):
        keycloak_openid = KeycloakOpenID(
            server_url=settings.KEYCLOACK_BASE_URI,
            client_id=settings.OIDC_RP_CLIENT_ID,
            realm_name=settings.KEYCLOACK_REALM_NAME,
            client_secret_key=settings.OIDC_RP_CLIENT_SECRET,
        )
        return keycloak_openid.uma_permissions(access_token)

    def verify_claims(self, claims):
        """Verify the provided claims to decide if authentication should be allowed."""

        # Verify claims required by default configuration
        logger.info("Verify claims")
        scopes = self.get_settings("OIDC_RP_SCOPES", "openid email")

        if "email" in scopes.split():
            return "email" in claims

        return True

    def iter_resource_names(self, claims: dict) -> Iterator[Group]:
        """Get all the resources the user has permission on from claims"""
        permissions = claims.get("permissions", list())
        for permission in permissions:
            if permission["rsname"].lower().startswith("department"):
                rsname = permission["rsname"].replace("_resources", "")
                yield rsname

    def iter_group_objects(self, claims: dict) -> Iterator[Group]:
        """Get or create a group for each group name from claims"""
        for group_name in self.iter_resource_names(claims):
            obj, created = Group.objects.get_or_create(name=group_name)
            yield obj


def provider_logout(request):
    return f"{KEYCLOACK_REALM_BASE_URI}/protocol/openid-connect/logout"
