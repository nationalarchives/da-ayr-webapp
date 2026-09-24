import pytest

from app.main.util.closure_status import closure_types_for_record_status


class TestClosureTypesForRecordStatus:
    @pytest.mark.parametrize(
        "record_status, expected",
        [
            ("closed", ["Closed", "Retained for security"]),
            ("Closed", ["Closed", "Retained for security"]),
            ("CLOSED", ["Closed", "Retained for security"]),
            ("open", ["Open"]),
            ("Open", ["Open"]),
            ("", ["Open"]),
            (None, ["Open"]),
        ],
    )
    def test_closure_types_for_record_status(self, record_status, expected):
        """
        Given a record_status filter value
        When closure_types_for_record_status is called
        Then it returns the closure_type values that should match it,
        with 'closed' also matching records retained for security
        """
        assert closure_types_for_record_status(record_status) == expected
