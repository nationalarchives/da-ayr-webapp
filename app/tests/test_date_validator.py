from datetime import date
from unittest.mock import patch

import pytest

from app.main.util.date_validator import validate_dates


class TestDateValidator:
    @pytest.mark.parametrize(
        "request_args, expected_results",
        [
            (
                {
                    "date_from_day": "01",
                    "date_from_month": "",
                    "date_from_year": "",
                },
                (
                    "01",
                    "",
                    "",
                    None,
                    None,
                    None,
                    {
                        "date_from": ["‘Date from’ must include a year"],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "01",
                    "date_from_month": "02",
                    "date_from_year": "",
                },
                (
                    "01",
                    "02",
                    "",
                    None,
                    None,
                    None,
                    {
                        "date_from": ["‘Date from’ must include a year"],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "01",
                    "date_from_month": "14",
                    "date_from_year": "2023",
                },
                (
                    "01",
                    14,
                    2023,
                    None,
                    None,
                    None,
                    {
                        "date_from": ["‘Date from’ must include a month"],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "32",
                    "date_from_month": "01",
                    "date_from_year": "2023",
                },
                (
                    32,
                    1,
                    2023,
                    None,
                    None,
                    None,
                    {
                        "date_from": ["‘Date from’ must be a real date"],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "29",
                    "date_from_month": "02",
                    "date_from_year": "2023",
                },
                (
                    29,
                    2,
                    2023,
                    None,
                    None,
                    None,
                    {
                        "date_from": ["‘Date from’ must be a real date"],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "1x",
                    "date_from_month": "14",
                    "date_from_year": "2023",
                },
                (
                    "1x",
                    14,
                    2023,
                    None,
                    None,
                    None,
                    {
                        "date_from": ["‘Date from’ must include a month"],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "01",
                    "date_from_month": "1x",
                    "date_from_year": "2023",
                },
                (
                    "01",
                    "1x",
                    2023,
                    None,
                    None,
                    None,
                    {
                        "date_from": ["‘Date from’ must include a month"],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "01",
                    "date_from_month": "12",
                    "date_from_year": "20xy",
                },
                (
                    "01",
                    "12",
                    "20xy",
                    None,
                    None,
                    None,
                    {
                        "date_from": ["‘Date from’ must include a year"],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "01",
                    "date_from_month": "",
                    "date_from_year": "2023",
                },
                (
                    "01",
                    "",
                    2023,
                    None,
                    None,
                    None,
                    {
                        "date_from": ["‘Date from’ must include a month"],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "",
                    "date_from_month": "",
                    "date_from_year": "20",
                },
                (
                    "",
                    "",
                    20,
                    None,
                    None,
                    None,
                    {
                        "date_from": ["‘Date from’ year must be in full"],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "31",
                    "date_from_month": "12",
                    "date_from_year": "2024",
                },
                (
                    31,
                    12,
                    2024,
                    None,
                    None,
                    None,
                    {
                        "date_from": ["‘Date from’ must be in the past"],
                        "date_to": [],
                    },
                ),
            ),
            (
                {"date_to_day": "31", "date_to_month": "", "date_to_year": ""},
                (
                    None,
                    None,
                    None,
                    "31",
                    "",
                    "",
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must include a year"],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "31",
                    "date_to_month": "12",
                    "date_to_year": "",
                },
                (
                    None,
                    None,
                    None,
                    "31",
                    "12",
                    "",
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must include a year"],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "32",
                    "date_to_month": "02",
                    "date_to_year": "2023",
                },
                (
                    None,
                    None,
                    None,
                    32,
                    2,
                    2023,
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must be a real date"],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "29",
                    "date_to_month": "02",
                    "date_to_year": "2023",
                },
                (
                    None,
                    None,
                    None,
                    29,
                    2,
                    2023,
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must be a real date"],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "29",
                    "date_to_month": "02",
                    "date_to_year": "1998",
                },
                (
                    None,
                    None,
                    None,
                    29,
                    2,
                    1998,
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must be a real date"],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "01",
                    "date_to_month": "14",
                    "date_to_year": "2023",
                },
                (
                    None,
                    None,
                    None,
                    "01",
                    14,
                    2023,
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must include a month"],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "29",
                    "date_to_month": "02",
                    "date_to_year": "2023",
                },
                (
                    None,
                    None,
                    None,
                    29,
                    2,
                    2023,
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must be a real date"],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "29",
                    "date_to_month": "02",
                    "date_to_year": "1923",
                },
                (
                    None,
                    None,
                    None,
                    29,
                    2,
                    1923,
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must be a real date"],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "2x",
                    "date_to_month": "02",
                    "date_to_year": "2023",
                },
                (
                    None,
                    None,
                    None,
                    "2x",
                    2,
                    2023,
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must be a real date"],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "29",
                    "date_to_month": "2x",
                    "date_to_year": "2023",
                },
                (
                    None,
                    None,
                    None,
                    "29",
                    "2x",
                    2023,
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must include a month"],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "29",
                    "date_to_month": "02",
                    "date_to_year": "20xy",
                },
                (
                    None,
                    None,
                    None,
                    "29",
                    "02",
                    "20xy",
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must include a year"],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "31",
                    "date_to_month": "12",
                    "date_to_year": "2024",
                },
                (
                    None,
                    None,
                    None,
                    31,
                    12,
                    2024,
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must be in the past"],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "1x",
                    "date_from_month": "08",
                    "date_from_year": "2023",
                    "date_to_day": "01",
                    "date_to_month": "2x",
                    "date_to_year": "2022",
                },
                (
                    "1x",
                    8,
                    2023,
                    "01",
                    "2x",
                    2022,
                    {
                        "date_from": ["‘Date from’ must be a real date"],
                        "date_to": ["‘Date to’ must include a month"],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "31",
                    "date_from_month": "12",
                    "date_from_year": "2022",
                    "date_to_day": "01",
                    "date_to_month": "12",
                    "date_to_year": "2022",
                },
                (
                    31,
                    12,
                    2022,
                    1,
                    12,
                    2022,
                    {
                        "date_from": [
                            "‘Date from’ must be the same as or before ‘01/12/2022’"
                        ],
                        "date_to": [],
                    },
                ),
            ),
        ],
    )
    @patch("app.main.util.date_validator.date")
    def test_validate_dates_full_test(
        self,
        mock_date,
        request_args,
        expected_results,
    ):
        """
        Given on different request arguments for date filters
        When validate_dates function called
        Then if date is not a valid date
        it returns various errors based on the data filter values
        """
        mock_date.today.return_value = date(2023, 1, 1)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        assert validate_dates(request_args) == expected_results

    @pytest.mark.parametrize(
        "request_args, expected_results",
        [
            (
                {
                    "date_from_day": "",
                    "date_from_month": "",
                    "date_from_year": "2023",
                },
                (
                    1,
                    1,
                    2023,
                    None,
                    None,
                    None,
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "",
                    "date_to_month": "",
                    "date_to_year": "2023",
                },
                (
                    None,
                    None,
                    None,
                    1,
                    1,
                    2023,
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "",
                    "date_to_month": "2",
                    "date_to_year": "2020",
                },
                (
                    None,
                    None,
                    None,
                    29,
                    2,
                    2020,
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "",
                    "date_from_month": "2",
                    "date_from_year": "2022",
                },
                (
                    1,
                    2,
                    2022,
                    None,
                    None,
                    None,
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "",
                    "date_to_month": "2",
                    "date_to_year": "2021",
                },
                (
                    None,
                    None,
                    None,
                    28,
                    2,
                    2021,
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_to_day": "",
                    "date_to_month": "",
                    "date_to_year": "2020",
                },
                (
                    None,
                    None,
                    None,
                    31,
                    12,
                    2020,
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                ),
            ),
        ],
    )
    @patch("app.main.util.date_validator.date")
    def test_validate_dates_return_complete_date_full_test(
        self,
        mock_date,
        request_args,
        expected_results,
    ):
        """
        Given on different request arguments for date filters
        When validate_dates function called
        Then specific date values i.e. month or year, month and year given
        it returns valid completed date for date filter values
        """
        mock_date.today.return_value = date(2023, 1, 1)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        assert validate_dates(request_args) == expected_results

    @pytest.mark.parametrize(
        "request_args, expected_results",
        [
            (
                {
                    "date_filter_field": "",
                    "date_from_day": "01",
                    "date_from_month": "08",
                    "date_from_year": "2023",
                    "date_to_day": "31",
                    "date_to_month": "08",
                    "date_to_year": "2023",
                },
                (
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    {
                        "date_filter_field": "Select either ‘Date of record’ or ‘Record opening date’",
                    },
                ),
            ),
            (
                {
                    "date_filter_field": "date_last_modified",
                    "date_from_day": "01",
                    "date_from_month": "08",
                    "date_from_year": "2022",
                    "date_to_day": "31",
                    "date_to_month": "08",
                    "date_to_year": "2022",
                },
                (
                    1,
                    8,
                    2022,
                    31,
                    8,
                    2022,
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                ),
            ),
            (
                {
                    "date_filter_field": "opening_date",
                    "date_from_day": "01",
                    "date_from_month": "08",
                    "date_from_year": "2025",
                    "date_to_day": "31",
                    "date_to_month": "12",
                    "date_to_year": "2025",
                },
                (
                    1,
                    8,
                    2025,
                    31,
                    12,
                    2025,
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                ),
            ),
        ],
    )
    @patch("app.main.util.date_validator.date")
    def test_validate_dates_with_browse_consignment(
        self,
        mock_date,
        request_args,
        expected_results,
    ):
        """
        Given on different request arguments for date filters
        When validate_dates function called with browse_consignment option
        Then it returns an error if no date filter field provided
        else it returns valid date filter values
        """
        mock_date.today.return_value = date(2023, 1, 1)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        assert (
            validate_dates(request_args, browse_consignment=True)
            == expected_results
        )
