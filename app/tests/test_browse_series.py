from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html


def verify_series_view_header_row(data):
    """
    this function check header row column values against expected row
    :param data: response data
    """
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")

    expected_row = (
        [
            "Transferring body",
            "Series",
            "Consignment transferred",
            "Records in consignment",
            "Consignment reference",
        ],
    )
    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_row[0]


def verify_data_rows(data, expected_rows):
    """
    this function check data rows for data table compared with expected rows
    :param data: response data
    :param expected_rows: expected rows to be compared
    """
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    rows = table.find_all("td")

    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "

    assert [row_data] == expected_rows[0]


class TestSeries:
    @property
    def route_url(self):
        return "/browse"

    def test_browse_series_without_filter(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a series id
        Then they should see results based on series filter on browse page content.
        """
        series_id = browse_files[0].consignment.series.SeriesId

        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        response = client.get(f"{self.route_url}?series_id={series_id}")

        assert response.status_code == 200
        assert b"You are viewing" in response.data
        assert b"Records found 2" in response.data

        expected_rows = [
            [
                "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
            ],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_with_date_range_filter_and_consignment_reference_sorting_oldest_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a series id
        and provide a date range with date from and date to value as filter in text input field
        and sorting by consignment reference in ascending order
        Then they should see results based on series and
        matches to date last transferred between date from and date to filter value
        and sorted by consignment reference in alphabetic order (oldest first)
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        date_from_day = "01"
        date_from_month = "01"
        date_from_year = "2023"
        date_to_day = "27"
        date_to_month = "02"
        date_to_year = "2023"

        response = client.get(
            f"{self.route_url}?series_id={series_id}&sort=consignment_reference-asc"
            + "&date_from_day="
            + date_from_day
            + "&date_from_month="
            + date_from_month
            + "&date_from_year="
            + date_from_year
            + "&date_to_day="
            + date_to_day
            + "&date_to_month="
            + date_to_month
            + "&date_to_year="
            + date_to_year
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1', "
                "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"
            ],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_with_date_range_filter_and_records_held_in_consignment_sorting_most_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a series id
        and provide a date range with date from and date to value as filter in text input field
        and sorting by records held in consignment in ascending order
        Then they should see results based on series and
        matches to date last transferred between date from and date to filter value
        and sorted by records held in consignment in reverse numeric order (most first)
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        date_from_day = "01"
        date_from_month = "01"
        date_from_year = "2023"
        date_to_day = "27"
        date_to_month = "02"
        date_to_year = "2023"

        response = client.get(
            f"{self.route_url}?series_id={series_id}&sort=records_held-desc"
            + "&date_from_day="
            + date_from_day
            + "&date_from_month="
            + date_from_month
            + "&date_from_year="
            + date_from_year
            + "&date_to_day="
            + date_to_day
            + "&date_to_month="
            + date_to_month
            + "&date_to_year="
            + date_to_year
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
            ],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_breadcrumb(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a series id
        Then they should see results based on series filter on browse page content.
        And breadcrumb should show 'Everything' > transferring body name > series name
        """
        series_id = browse_files[0].consignment.series.SeriesId

        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        response = client.get(f"{self.route_url}?series_id={series_id}")

        assert response.status_code == 200
        assert b"You are viewing" in response.data
        assert b"Records found 2" in response.data

        html = response.data.decode()

        expected_breadcrumbs_html = f"""
        <div class="govuk-breadcrumbs">
            <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                    <a class="govuk-breadcrumbs__link--record" href="{self.route_url}">Everything</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <a class="govuk-breadcrumbs__link--record--transferring-body"
                        href="{self.route_url}?transferring_body_id={browse_files[0].consignment.series.body.BodyId}">{browse_files[0].consignment.series.body.Name}</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">{browse_files[0].consignment.series.Name}</span>
                </li>
            </ol>
        </div>
        """

        assert_contains_html(
            expected_breadcrumbs_html,
            html,
            "div",
            {"class": "govuk-breadcrumbs"},
        )

    def test_browse_series_with_date_from_filter(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a series id
        and provide a date range with only date from value as filter in text input field
        Then they should see results based on series and
        matches to date last transferred greater than or equal to date from filter value
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        day = "01"
        month = "02"
        year = "2023"

        response = client.get(
            f"{self.route_url}?series_id={series_id}&date_from_day="
            + day
            + "&date_from_month="
            + month
            + "&date_from_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_with_date_to_filter(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a series id
        and provide a date range with only date to value as filter in text input field
        Then they should see results based on series and
        matches to date last transferred less than or equal to date to filter value
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        day = "31"
        month = "01"
        year = "2023"

        response = client.get(
            f"{self.route_url}?series_id={series_id}&date_to_day="
            + day
            + "&date_to_month="
            + month
            + "&date_to_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_with_date_from_and_date_to_filter(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a series id
        and provide a date range with date from and date to value as filter in text input field
        Then they should see results based on series and
        matches to date last transferred between date from and date to filter value
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        date_from_day = "01"
        date_from_month = "01"
        date_from_year = "2023"
        date_to_day = "27"
        date_to_month = "02"
        date_to_year = "2023"

        response = client.get(
            f"{self.route_url}?series_id={series_id}&date_from_day="
            + date_from_day
            + "&date_from_month="
            + date_from_month
            + "&date_from_year="
            + date_from_year
            + "&date_to_day="
            + date_to_day
            + "&date_to_month="
            + date_to_month
            + "&date_to_year="
            + date_to_year
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
            ],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_with_date_consignment_transferred_sorting_oldest_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with a series id
        and select sorting option as date consignment transferred ascending
        Then they should see first five records sorted in oldest date first order of date consignment transferred
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        response = client.get(
            f"{self.route_url}?series_id={series_id}&sort=last_record_transferred-asc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1', "
                "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"
            ],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_with_date_consignment_transferred_sorting_most_recent_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with a series id
        and select sorting option as date consignment transferred descending
        Then they should see records sorted in most recent date first order of date consignment transferred
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        response = client.get(
            f"{self.route_url}?series_id={series_id}&sort=last_record_transferred-desc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
            ],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_with_consignment_reference_sorting_most_recent_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with a series id
        and select sorting option as consignment reference descending
        Then they should see records sorted by consignment reference in reverse alphabetic order most recent first
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        response = client.get(
            f"{self.route_url}?series_id={series_id}&sort=consignment_reference-desc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
            ],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_with_consignment_reference_sorting_oldest_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with a series id
        and select sorting option as consignment reference ascending
        Then they should see records sorted by consignment reference in alphabetic order oldest first
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        response = client.get(
            f"{self.route_url}?series_id={series_id}&sort=consignment_reference-asc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1', "
                "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"
            ],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_with_records_held_in_consignment_sorting_least_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with a series id
        and select sorting option as records held in consignment ascending
        Then they should see records sorted by least records held first in consignment
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        response = client.get(
            f"{self.route_url}?series_id={series_id}&sort=records_held-asc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1', "
                "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"
            ],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_with_records_held_in_consignment_sorting_most_first(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with a series id
        and select sorting option as records held in consignment descending
        Then they should see records sorted by most records held first in consignment
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        response = client.get(
            f"{self.route_url}?series_id={series_id}&sort=records_held-desc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
            ],
        ]

        verify_series_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_series_with_filter_no_results(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with a series id
        and use date from filter with date value
        Then if database does not have records and no results found returned
        they should see empty header row on browse transferring body page content.
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        response = client.get(
            f"{self.route_url}?series_id={series_id}&date_from_day=01&date_from_month=01&date_from_year=2024"
        )

        assert response.status_code == 200

        verify_series_view_header_row(response.data)
