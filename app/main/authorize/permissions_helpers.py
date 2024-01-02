from typing import List

from flask import abort, session
from sqlalchemy import exc

from app.main.authorize.keycloak_manager import (
    get_user_groups,
    get_user_transferring_body_keycloak_groups,
)
from app.main.db.models import Body, db


def validate_body_user_groups_or_404(
    transferring_body_name: str,
):
    """
    Validates whether the user in the current flask session has access to a specific
    transferring body based on their user groups.

    Args:
        transferring_body_name (str): The name of the transferring body to check access for.

    Raises:
        werkzeug.exceptions.NotFound: If the user does not have access to the specified transferring body.
    """
    groups = get_user_groups(session.get("access_token"))
    user_accessible_transferring_bodies = (
        get_user_accessible_transferring_bodies(groups)
    )

    if "/ayr_user_type/view_all" not in groups and (
        not user_accessible_transferring_bodies
        or (transferring_body_name not in user_accessible_transferring_bodies)
    ):
        abort(404)


def get_user_accessible_transferring_bodies(groups: List[str]) -> List[str]:
    user_transferring_bodies = get_user_transferring_body_keycloak_groups(
        groups
    )

    if not user_transferring_bodies:
        return []

    try:
        query = db.session.query(Body.Name)
        bodies = db.session.execute(query)
    except exc.SQLAlchemyError as e:
        print("Failed to return results from database with error : " + str(e))
        return []

    user_accessible_transferring_bodies = []

    for body in bodies:
        body_name = body.Name
        if _body_in_users_groups(body_name, user_transferring_bodies):
            user_accessible_transferring_bodies.append(body_name)

    return user_accessible_transferring_bodies


def _body_in_users_groups(body, user_transferring_body_keycloak_groups):
    for user_group in user_transferring_body_keycloak_groups:
        if (
            user_group.strip().replace(" ", "").lower()
            == body.strip().replace(" ", "").lower()
        ):
            return True

    return False
