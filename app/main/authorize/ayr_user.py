from typing import List

import sqlalchemy
from sqlalchemy import func

from app.main.authorize.keycloak_manager import (
    get_user_groups,
    get_user_transferring_body_keycloak_groups,
)
from app.main.db.models import Body


class AYRUser:
    def __init__(self, groups: List[str]) -> None:
        self.groups = groups

    @staticmethod
    def from_access_token(access_token):
        return AYRUser(get_user_groups(access_token))

    @property
    def can_access_ayr(self):
        return self.is_superuser or self.is_standard_user

    @property
    def is_superuser(self) -> bool:
        return "/ayr_user_type/view_all" in self.groups

    @property
    def is_standard_user(self) -> bool:
        return "/ayr_user_type/view_dept" in self.groups

    @property
    def transferring_body(self) -> Body | None:
        transferring_body_names = get_user_transferring_body_keycloak_groups(
            self.groups
        )

        if not transferring_body_names:
            return None

        transferring_body_name = transferring_body_names[0]

        try:
            body = Body.query.filter(
                Body.Name == transferring_body_name
            ).one_or_none()
        except sqlalchemy.orm.exc.MultipleResultsFound:
            return None
        return body

    @property
    def transferring_bodies(self) -> {}:
        transferring_body_names = get_user_transferring_body_keycloak_groups(
            self.groups
        )

        if not transferring_body_names:
            return None

        try:
            bodies = []
            for body in transferring_body_names:
                body_found = Body.query.filter(
                    func.lower(Body.Name) == body.lower()
                ).one_or_none()
                if body_found:
                    bodies.append(body_found)
        except sqlalchemy.orm.exc.MultipleResultsFound:
            return None
        return bodies
