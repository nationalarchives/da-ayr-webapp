from flask import abort, session

from app.main.authorize.ayr_user import AYRUser


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
    ayr_user = AYRUser.from_access_token(session.get("access_token"))

    if ayr_user.is_superuser:
        return

    if transferring_body_name not in ayr_user.transferring_bodies:
        abort(404)
