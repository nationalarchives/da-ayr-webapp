from flask import abort, session

from app.main.authorize.keycloak_manager import get_user_groups
from app.main.db.queries import get_user_accessible_transferring_bodies


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
