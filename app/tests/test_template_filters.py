from app.template_filters import format_datetime


class TestFormatDateTime:
    def test_non_string_returns_dash(self):
        assert format_datetime(None) == "-"

    def test_invalid_date_string_returns_dash(self):
        assert format_datetime("2019-11-23T14:19:57FOO") == "-"

    def test_valid_date_string_returns_formatted_date_string(self):
        assert format_datetime("2019-11-23T14:19:57") == "23/11/2019"
