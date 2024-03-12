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
                        "date_from": ["`Date from` must include a year"],
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
                        "date_from": ["`Date from` must include a year"],
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
                        "date_from": ["`Date from` must include a valid month"],
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
                        "date_from": ["`Date from` must be a real date"],
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
                        "date_from": ["`Date from` must be a real date"],
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
                        "date_from": ["`Date from` must include a valid month"],
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
                        "date_from": ["`Date from` must include a valid month"],
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
                        "date_from": ["`Date from` must include a year"],
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
                        "date_from": ["`Date from` must be in the past"],
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
                        "date_to": ["`Date to` must include a year"],
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
                        "date_to": ["`Date to` must include a year"],
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
                        "date_to": ["`Date to` must be a real date"],
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
                        "date_to": ["`Date to` must include a valid month"],
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
                        "date_to": ["`Date to` must be a real date"],
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
                        "date_to": ["`Date to` must be a real date"],
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
                        "date_to": ["`Date to` must include a valid month"],
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
                        "date_to": ["`Date to` must include a year"],
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
                        "date_to": ["`Date to` must be in the past"],
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
                        "date_from": ["`Date from` must be a real date"],
                        "date_to": ["`Date to` must include a valid month"],
                    },
                ),
            ),
            (
                {
                    "date_from_day": "01",
                    "date_from_month": "08",
                    "date_from_year": "2023",
                    "date_to_day": "01",
                    "date_to_month": "12",
                    "date_to_year": "2022",
                },
                (
                    1,
                    8,
                    2023,
                    1,
                    12,
                    2022,
                    {
                        "date_from": [
                            "`Date from` must be the same as or before ‘01/12/2022’"
                        ],
                        "date_to": [],
                    },
                ),
            ),
        ],
    )
    def test_validate_dates_full_test(
        self,
        request_args,
        expected_results,
    ):
        """
        Given on different request arguments for date filters
        When validate_dates function called
        Then if date is not a valid date
        it returns various errors based on the data filter values
        """
        assert validate_dates(request_args) == expected_results
