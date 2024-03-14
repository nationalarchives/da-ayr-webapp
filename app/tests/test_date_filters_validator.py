from datetime import date

import pytest

from app.main.util.date_filters_validator import validate_date_filters


class TestDateFiltersValidator:
    @pytest.mark.parametrize(
        "request_args, expected_results",
        [
            (
                {
                    "date_from_day": "01",
                    "date_from_month": "08",
                    "date_from_year": "2023",
                    "date_to_day": "31",
                    "date_to_month": "08",
                    "date_to_year": "2023",
                },
                (
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                    date(2023, 8, 1),
                    date(2023, 8, 31),
                    {
                        "from_day": "01",
                        "from_month": "08",
                        "from_year": "2023",
                        "to_day": 31,
                        "to_month": "08",
                        "to_year": "2023",
                    },
                ),
            ),
            (
                {
                    "date_from_day": "29",
                    "date_from_month": "02",
                    "date_from_year": "2023",
                    "date_to_day": "",
                    "date_to_month": "",
                    "date_to_year": "",
                },
                (
                    {
                        "date_from": ["‘Date from’ must be a real date"],
                        "date_to": [],
                    },
                    None,
                    None,
                    {"from_day": 29, "from_month": "02", "from_year": "2023"},
                ),
            ),
            (
                {
                    "date_from_day": "",
                    "date_from_month": "",
                    "date_from_year": "2023",
                    "date_to_day": "",
                    "date_to_month": "",
                    "date_to_year": "",
                },
                (
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                    date(2023, 1, 1),
                    None,
                    {"from_day": "01", "from_month": "01", "from_year": "2023"},
                ),
            ),
            (
                {
                    "date_from_day": "6",
                    "date_from_month": "3",
                    "date_from_year": "2023",
                    "date_to_day": "",
                    "date_to_month": "",
                    "date_to_year": "",
                },
                (
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                    date(2023, 3, 6),
                    None,
                    {"from_day": "06", "from_month": "03", "from_year": "2023"},
                ),
            ),
            (
                {
                    "date_from_day": "",
                    "date_from_month": "",
                    "date_from_year": "",
                    "date_to_day": "",
                    "date_to_month": "02",
                    "date_to_year": "2023",
                },
                (
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                    None,
                    date(2023, 2, 28),
                    {"to_day": 28, "to_month": "02", "to_year": "2023"},
                ),
            ),
            (
                {
                    "date_from_day": "",
                    "date_from_month": "",
                    "date_from_year": "",
                    "date_to_day": "5",
                    "date_to_month": "2",
                    "date_to_year": "2023",
                },
                (
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                    None,
                    date(2023, 2, 5),
                    {"to_day": "05", "to_month": "02", "to_year": "2023"},
                ),
            ),
            (
                {
                    "date_from_day": "",
                    "date_from_month": "",
                    "date_from_year": "",
                    "date_to_day": "5",
                    "date_to_month": "2",
                    "date_to_year": "",
                },
                (
                    {
                        "date_from": [],
                        "date_to": ["‘Date to’ must include a year"],
                    },
                    None,
                    None,
                    {"to_day": "05", "to_month": "02", "to_year": 0},
                ),
            ),
            (
                {
                    "date_from_day": "",
                    "date_from_month": "",
                    "date_from_year": "",
                    "date_to_day": "29",
                    "date_to_month": "02",
                    "date_to_year": "2024",
                },
                (
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                    None,
                    date(2024, 2, 29),
                    {"to_day": 29, "to_month": "02", "to_year": "2024"},
                ),
            ),
        ],
    )
    def test_validate_date_filters_without_browse_consignment(
        self,
        request_args,
        expected_results,
    ):
        """
        Given on different request arguments for date filters
        When validate_date_filters function called without browse_consignment option
        Then it returns formatted date object if it is valid
        else it returns date validation errors
        """
        assert (
            validate_date_filters(request_args, browse_consignment=False)
            == expected_results
        )

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
                    {
                        "date_filter_field": "Select either ‘Date of record’ or ‘Record opening date’",
                    },
                    None,
                    None,
                    {},
                ),
            ),
            (
                {
                    "date_filter_field": "date_last_modified",
                    "date_from_day": "01",
                    "date_from_month": "08",
                    "date_from_year": "2023",
                    "date_to_day": "31",
                    "date_to_month": "08",
                    "date_to_year": "2023",
                },
                (
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                    date(2023, 8, 1),
                    date(2023, 8, 31),
                    {
                        "from_day": "01",
                        "from_month": "08",
                        "from_year": "2023",
                        "to_day": 31,
                        "to_month": "08",
                        "to_year": "2023",
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
                    {
                        "date_from": [],
                        "date_to": [],
                    },
                    date(2025, 8, 1),
                    date(2025, 12, 31),
                    {
                        "from_day": "01",
                        "from_month": "08",
                        "from_year": "2025",
                        "to_day": 31,
                        "to_month": 12,
                        "to_year": "2025",
                    },
                ),
            ),
        ],
    )
    def test_validate_date_filters_with_browse_consignment(
        self,
        request_args,
        expected_results,
    ):
        """
        Given on different request arguments for date filters
        When validate_date_filters function called with browse_consignment
        Then it returns formatted date if they are valid
        else it returns date validation errors
        """
        assert (
            validate_date_filters(request_args, browse_consignment=True)
            == expected_results
        )
