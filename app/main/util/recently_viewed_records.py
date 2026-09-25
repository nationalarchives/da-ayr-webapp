"""Track the records a user has recently opened so they can jump back to them."""

MAX_RECENTLY_VIEWED_RECORDS = 5
SESSION_KEY = "recently_viewed_records"


def record_recently_viewed(session, file_metadata: dict) -> None:
    """
    Add a record to the front of the user's recently viewed list in their session.

    Any existing entry for the same record is removed first so it is moved to
    the front rather than duplicated, and the list is capped at
    MAX_RECENTLY_VIEWED_RECORDS entries.
    """
    entry = {
        "file_id": str(file_metadata["file_id"]),
        "file_name": file_metadata.get("file_name"),
        "transferring_body": file_metadata.get("transferring_body"),
        "series": file_metadata.get("series"),
    }

    existing = [
        item
        for item in session.get(SESSION_KEY, [])
        if item.get("file_id") != entry["file_id"]
    ]

    session[SESSION_KEY] = [entry, *existing][:MAX_RECENTLY_VIEWED_RECORDS]


def get_recently_viewed_records(session, ayr_user) -> list:
    """
    Return the user's recently viewed records that they still have permission to access.

    Permissions can change between visits, so each stored entry is re-checked
    against the user's current access rather than trusting what was true when
    it was originally viewed.
    """
    recently_viewed = session.get(SESSION_KEY, [])

    if ayr_user.is_all_access_user:
        return recently_viewed

    if not ayr_user.is_standard_user or ayr_user.transferring_body is None:
        return []

    accessible_body_name = ayr_user.transferring_body.Name

    return [
        item
        for item in recently_viewed
        if item.get("transferring_body") == accessible_body_name
    ]
