from flask.testing import FlaskClient

from app.main.authorize.ayr_user import AYRUser
from app.main.util.recently_viewed_records import (
    MAX_RECENTLY_VIEWED_RECORDS,
    get_recently_viewed_records,
    record_recently_viewed,
)
from app.tests.factories import BodyFactory


def _file_metadata(file_id, transferring_body="Body A", series="Series A"):
    return {
        "file_id": file_id,
        "file_name": f"file-{file_id}.pdf",
        "transferring_body": transferring_body,
        "series": series,
    }


class TestRecordRecentlyViewed:
    def test_adds_new_entry_to_front_of_empty_session(self):
        session = {}

        record_recently_viewed(session, _file_metadata("file-1"))

        assert [
            item["file_id"] for item in session["recently_viewed_records"]
        ] == ["file-1"]

    def test_moves_existing_entry_to_front_without_duplicating(self):
        session = {}
        record_recently_viewed(session, _file_metadata("file-1"))
        record_recently_viewed(session, _file_metadata("file-2"))
        record_recently_viewed(session, _file_metadata("file-1"))

        file_ids = [
            item["file_id"] for item in session["recently_viewed_records"]
        ]

        assert file_ids == ["file-1", "file-2"]

    def test_caps_list_at_max_recently_viewed_records(self):
        session = {}

        for i in range(MAX_RECENTLY_VIEWED_RECORDS + 2):
            record_recently_viewed(session, _file_metadata(f"file-{i}"))

        assert (
            len(session["recently_viewed_records"])
            == MAX_RECENTLY_VIEWED_RECORDS
        )
        # most recently viewed record should be first
        assert session["recently_viewed_records"][0]["file_id"] == (
            f"file-{MAX_RECENTLY_VIEWED_RECORDS + 1}"
        )


class TestGetRecentlyViewedRecords:
    def test_returns_empty_list_when_session_has_no_history(self):
        ayr_user = AYRUser(["/ayr_user_type/view_all"])

        assert get_recently_viewed_records({}, ayr_user) == []

    def test_all_access_user_sees_records_from_any_transferring_body(self):
        session = {}
        record_recently_viewed(session, _file_metadata("file-1", "Body A"))
        record_recently_viewed(session, _file_metadata("file-2", "Body B"))
        ayr_user = AYRUser(["/ayr_user_type/view_all"])

        result = get_recently_viewed_records(session, ayr_user)

        assert [item["file_id"] for item in result] == ["file-2", "file-1"]

    def test_standard_user_only_sees_records_from_their_transferring_body(
        self, client: FlaskClient
    ):
        BodyFactory(Name="Body A")
        session = {}
        record_recently_viewed(session, _file_metadata("file-1", "Body A"))
        record_recently_viewed(session, _file_metadata("file-2", "Body B"))
        ayr_user = AYRUser(
            ["/ayr_user_type/view_dept", "/transferring_body_user/Body A"]
        )

        result = get_recently_viewed_records(session, ayr_user)

        assert [item["file_id"] for item in result] == ["file-1"]

    def test_standard_user_without_a_transferring_body_sees_no_records(
        self, client: FlaskClient
    ):
        session = {}
        record_recently_viewed(session, _file_metadata("file-1", "Body A"))
        ayr_user = AYRUser(["/ayr_user_type/view_dept"])

        assert get_recently_viewed_records(session, ayr_user) == []
