from datetime import date, datetime

import pytest
from flask.testing import FlaskClient

from app.main.util.date_validator import (
    generate_date_values,
    generate_default_date_values,
    get_date,
    validate_date_range,
    validate_dates,
)

db_date_format = "%Y-%m-%d"
python_date_format = "%d/%m/%Y"


def default_start_date():
    return date(2023, 1, 1)


def current_date():
    return datetime.strptime(str(date.today()), db_date_format).strftime(
        python_date_format
    )


class TestDateValidator:
    @property
    def route_url(self):
        return "/browse"

    def test_logs_message_and_returns_none_date_when_invalid_from_date(
        self, app, caplog
    ):
        """
        Given an invalid date_from value
        When validate_date_range function is called
        Then it returns an empty date range and logs error messages
        """
        dt_range = {"date_from": "junk"}
        results = validate_date_range(date_range=dt_range)
        assert (
            "Invalid [date from] value being passed in date range"
            in caplog.text
        )
        assert results == {"date_from": None, "date_to": None}

    def test_logs_message_and_returns_none_date_when_invalid_to_date(
        self, app, caplog
    ):
        """
        Given an invalid date_to value
        When validate_date_range function is called
        Then it returns an empty date range and logs error messages
        """
        dt_range = {"date_to": "junk"}
        results = validate_date_range(date_range=dt_range)
        assert (
            "Invalid [date to] value being passed in date range" in caplog.text
        )
        assert results == {"date_from": None, "date_to": None}

    def test_logs_messages_and_returns_none_dates_when_invalid_dates(
        self, app, caplog
    ):
        """
        Given an invalid date_from and date_to values
        When validate_date_range function is called
        Then it returns an empty date range and logs error messages
        """
        dt_range = {"date_from": "junk", "date_to": "junk"}
        results = validate_date_range(date_range=dt_range)
        assert (
            "Invalid [date from] value being passed in date range"
            in caplog.text
        )
        assert (
            "Invalid [date to] value being passed in date range" in caplog.text
        )
        assert results == {"date_from": None, "date_to": None}

    def test_get_date_without_leading_zeros_day_and_month(self):
        """
        Given date values without leading zeros
        When get_date function is called
        Then it returns a list with day and month with leading zeros to reach 2 characters length
        and year with trailing zeros to reach 4 characters length
        """

        values = get_date("1", "1", "2000", 0)
        assert values[0] == "01"
        assert values[1] == "01"
        assert values[2] == "2000"

    def test_get_date_with_leading_zeros_day_and_month(self):
        """
        Given date values with leading zeros
        When get_date function is called
        Then it returns a list with day and month with leading zeros to reach 2 characters length
        and year with trailing zeros to reach 4 characters length
        """
        values = get_date("01", "01", "2000", 0)
        assert values[0] == "01"
        assert values[1] == "01"
        assert values[2] == "2000"

    def test_get_date_with_two_digit_year(self):
        """
        Given date values with 2 characters as year
        When get_date function is called
        Then it returns a list with day and month with leading zeros to reach 2 characters length
        and year with trailing zeros to reach 4 characters length
        """
        values = get_date("01", "01", "20", 0)
        assert values[0] == "01"
        assert values[1] == "01"
        assert values[2] == "2000"

    def test_generate_date_values_with_date_from_values(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given request arguments for date from filters
        When generate_date_values function called
        Then it returns a dictionary object with 6 values
        with valid date from values get assigned to 1 to 3 items and 4 to 6 get assigned as zero value
        """

        mock_all_access_user(client)
        query = "date_from_day=01&date_from_month=08&date_from_year=2023&date_to_day=&date_to_month=&date_to_year="
        response = client.get(f"{self.route_url}?{query}")
        assert response.status_code == 200

        values = generate_date_values(response.request.args)

        assert values == {
            "1": "01",
            "2": "08",
            "3": "2023",
            "4": "00",
            "5": "00",
            "6": "0000",
        }

    def test_generate_date_values_with_date_to_values(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given request arguments for date to filters
        When generate_date_values function called
        Then it returns a dictionary object with 6 values
        with valid date to values get assigned to 4 to 6 items and 1 to 3 get assigned as zero value
        """
        mock_all_access_user(client)
        query = "date_from_day=&date_from_month=&date_from_year=&date_to_day=31&date_to_month=08&date_to_year=2023"

        response = client.get(f"{self.route_url}?{query}")

        assert response.status_code == 200

        values = generate_date_values(response.request.args)

        assert values == {
            "1": "00",
            "2": "00",
            "3": "0000",
            "4": "31",
            "5": "08",
            "6": "2023",
        }

    def test_generate_date_values_with_date_from_and_date_to_values(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given request arguments for date from and date to filters
        When generate_date_values function called
        Then it returns a dictionary object with 6 values
        with valid date from values get assigned to 1 to 3 items and date to values get assigned to 4 to 6 items
        """
        mock_all_access_user(client)
        param1 = "date_from_day=01&date_from_month=08&date_from_year=2023"
        param2 = "date_to_day=27&date_to_month=02&date_to_year=2023"
        query = param1 + "&" + param2

        response = client.get(f"{self.route_url}?{query}")

        assert response.status_code == 200

        values = generate_date_values(response.request.args)

        assert values == {
            "1": "01",
            "2": "08",
            "3": "2023",
            "4": "27",
            "5": "02",
            "6": "2023",
        }

    @pytest.mark.parametrize(
        "query_params, expected_results",
        [
            (
                "date_from_day=&date_from_month=10&date_from_year=2023",
                {"date_from": "01/10/2023", "date_to": current_date()},
            ),
            (
                "date_from_day=&date_from_month=02&date_from_year=2020",
                {"date_from": "01/02/2020", "date_to": current_date()},
            ),
            (
                "date_from_day=&date_from_month=&date_from_year=2023",
                {"date_from": "01/01/2023", "date_to": "31/12/2023"},
            ),
            (
                "date_from_day=&date_from_month=&date_from_year=2024",
                {"date_from": "01/01/2024", "date_to": current_date()},
            ),
            (
                "date_from_day=&date_from_month=03&date_from_year=2024",
                {"date_from": "01/03/2024", "date_to": current_date()},
            ),
            (
                "date_from_day=01&date_from_month=10&date_from_year=2023",
                {"date_from": "01/10/2023", "date_to": current_date()},
            ),
            (
                "date_to_day=&date_to_month=03&date_to_year=2023",
                {
                    "date_from": default_start_date().strftime(
                        python_date_format
                    ),
                    "date_to": "31/03/2023",
                },
            ),
            (
                "date_to_day=&date_to_month=02&date_to_year=2024",
                {
                    "date_from": default_start_date().strftime(
                        python_date_format
                    ),
                    "date_to": "29/02/2024",
                },
            ),
            (
                "date_to_day=&date_to_month=&date_to_year=2023",
                {
                    "date_from": default_start_date().strftime(
                        python_date_format
                    ),
                    "date_to": "31/12/2023",
                },
            ),
            (
                "date_to_day=31&date_to_month=03&date_to_year=2023",
                {
                    "date_from": default_start_date().strftime(
                        python_date_format
                    ),
                    "date_to": "31/03/2023",
                },
            ),
            (
                "date_from_day=&date_from_month=&date_from_year=2023&"
                "date_to_day=&date_to_month=&date_to_year=2023",
                {"date_from": "01/01/2023", "date_to": "31/12/2023"},
            ),
            (
                "date_from_day=01&date_from_month=08&date_from_year=2023&"
                "date_to_day=31&date_to_month=10&date_to_year=2023",
                {"date_from": "01/08/2023", "date_to": "31/10/2023"},
            ),
            (
                "date_from_day=&date_from_month=&date_from_year=&"
                "date_to_day=&date_to_month=&date_to_year=",
                {"date_from": "##/##/####", "date_to": "##/##/####"},
            ),
        ],
    )
    def test_generate_default_date_values_full_test(
        self,
        client: FlaskClient,
        mock_all_access_user,
        query_params,
        expected_results,
    ):
        """
        Given on different request arguments for date filters
        When generate_default_date_values function called
        Then it returns a dictionary object with 6 values
        with valid date from values get assigned to 1 to 3 items and date to values get assigned to 4 to 6 items
        """
        mock_all_access_user(client)
        response = client.get(f"{self.route_url}?{query_params}")
        assert response.status_code == 200
        values = generate_default_date_values(
            response.request.args, start_date=default_start_date()
        )
        assert values == expected_results

    @pytest.mark.parametrize(
        "query_params, expected_results",
        [
            (
                "date_from_day=01&date_from_month=&date_from_year=",
                {"date_from": "‘Date from’ must include a month"},
            ),
            (
                "date_from_day=01&date_from_month=02&date_from_year=",
                {"date_from": "‘Date from’ must include a year"},
            ),
            (
                "date_from_day=01&date_from_month=14&date_from_year=2023",
                {"date_from": "‘Date from’ must be a real date"},
            ),
            (
                "date_from_day=32&date_from_month=01&date_from_year=2023",
                {"date_from": "‘Date from’ must be a real date"},
            ),
            (
                "date_from_day=29&date_from_month=02&date_from_year=2023",
                {"date_from": "‘Date from’ must be a real date"},
            ),
            (
                "date_from_day=1x&date_from_month=14&date_from_year=2023",
                {"date_from": "‘Date from’ must be a real date"},
            ),
            (
                "date_from_day=01&date_from_month=1x&date_from_year=2023",
                {"date_from": "‘Date from’ must be a real date"},
            ),
            (
                "date_from_day=01&date_from_month=12&date_from_year=20xy",
                {"date_from": "‘Date from’ must be a real date"},
            ),
            (
                "date_from_day=31&date_from_month=12&date_from_year=2024",
                {"date_from": "‘Date from’ must be in the past"},
            ),
            (
                "date_to_day=31&date_to_month=&date_to_year=",
                {"date_to": "‘Date to’ must include a month"},
            ),
            (
                "date_to_day=31&date_to_month=12&date_to_year=",
                {"date_to": "‘Date to’ must include a year"},
            ),
            (
                "date_to_day=32&date_to_month=02&date_to_year=2023",
                {"date_to": "‘Date to’ must be a real date"},
            ),
            (
                "date_to_day=01&date_to_month=14&date_to_year=2023",
                {"date_to": "‘Date to’ must be a real date"},
            ),
            (
                "date_to_day=29&date_to_month=02&date_to_year=2023",
                {"date_to": "‘Date to’ must be a real date"},
            ),
            (
                "date_to_day=2x&date_to_month=02&date_to_year=2023",
                {"date_to": "‘Date to’ must be a real date"},
            ),
            (
                "date_to_day=29&date_to_month=2x&date_to_year=2023",
                {"date_to": "‘Date to’ must be a real date"},
            ),
            (
                "date_to_day=29&date_to_month=02&date_to_year=20xy",
                {"date_to": "‘Date to’ must be a real date"},
            ),
            (
                "date_to_day=31&date_to_month=12&date_to_year=2024",
                {"date_to": "‘Date to’ must be in the past"},
            ),
            (
                (
                    "date_from_day=1x&date_from_month=08&date_from_year=2023&"
                    "date_to_day=01&date_to_month=2x&date_to_year=2022"
                ),
                {
                    "date_from": "‘Date from’ must be a real date",
                    "date_to": "‘Date to’ must be a real date",
                },
            ),
            (
                (
                    "date_from_day=01&date_from_month=08&date_from_year=2023&"
                    "date_to_day=01&date_to_month=12&date_to_year=2022"
                ),
                {
                    "date_from": "‘Date from’ must be the same as or before ‘01/12/2022’"
                },
            ),
        ],
    )
    def test_validate_dates_full_test(
        self,
        client: FlaskClient,
        mock_all_access_user,
        query_params,
        expected_results,
    ):
        """
        Given on different request arguments for date filters
        When validate_dates function called
        Then if date is not a valid date
        it returns various errors based on the data filter values
        """
        mock_all_access_user(client)
        response = client.get(f"{self.route_url}?{query_params}")
        assert response.status_code == 200
        errors = validate_dates(
            response.request.args, validate_future_date=True
        )
        assert errors == expected_results
