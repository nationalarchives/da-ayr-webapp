import os
from typing import List


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
