from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html


def verify_transferring_body_view_header_row(data):
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
            "Last record transferred",
            "Records held",
            "Consignments within series",
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


class TestBrowseTransferringBody:
    @property
    def route_url(self):
        return "/browse"

    def test_browse_transferring_body_without_filter(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        Then they should see results based on transferring body filter on browse page content.
        """
        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}"
        )

        assert response.status_code == 200
        assert b"You are viewing" in response.data
        assert b"Records found 3" in response.data

        expected_rows = [
            [
                "'first_body', 'first_series', '14/10/2023', '1', '1', "
                "'first_body', 'second_series', '30/03/2023', '2', '1', "
                "'first_body', 'third_series', '07/07/2023', '3', '1'"
            ],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_date_from_and_date_to_filter_and_records_held_in_series_sorting_most_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and provide a date range with date from and date to value as filter in text input field
        and sort by records held in series descending order
        Then they should see results based on transferring body and
        matches to date last transferred between date from and date to filter value
        and sorted by records held in series descending order (most first)
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        date_from_day = "01"
        date_from_month = "01"
        date_from_year = "2023"
        date_to_day = "31"
        date_to_month = "12"
        date_to_year = "2023"
        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&sort=records_held-desc"
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
                "'first_body', 'third_series', '07/07/2023', '3', '1', "
                "'first_body', 'second_series', '30/03/2023', '2', '1', "
                "'first_body', 'first_series', '14/10/2023', '1', '1'"
            ],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_date_range_filter_and_date_consignment_transferred_sorting_most_recent_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and provide a date range with date from and date to value as filter in text input field
        and sort by date consignment transferred in descending order
        Then they should see results based on transferring body and
        matches to date last transferred between date from and date to filter value
        and sorted by date consignment transferred descending order (most recent first)
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        date_from_day = "01"
        date_from_month = "01"
        date_from_year = "2023"
        date_to_day = "31"
        date_to_month = "12"
        date_to_year = "2023"
        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&sort=last_record_transferred-desc"
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
                "'first_body', 'first_series', '14/10/2023', '1', '1', "
                "'first_body', 'third_series', '07/07/2023', '3', '1', "
                "'first_body', 'second_series', '30/03/2023', '2', '1'"
            ],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_breadcrumb(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a transferring body id
        Then they should see results based on transferring body filter on browse page content.
        And breadcrumb should show 'Everything' > transferring body name
        """
        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}"
        )

        assert response.status_code == 200
        assert b"You are viewing" in response.data
        assert b"Records found 3" in response.data

        html = response.data.decode()

        expected_breadcrumbs_html = f"""
        <div class="govuk-breadcrumbs">
            <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record" href="{self.route_url}">Everything</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">
                {browse_transferring_body_files[0].consignment.series.body.Name}</span>
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

    def test_browse_transferring_body_with_series_filter(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and provide a series value as filter in text input field
        Then they should see results based on transferring body and matches to series name
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        series = "second"

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&series_filter="
            + series
        )

        assert response.status_code == 200

        expected_rows = [
            ["'first_body', 'second_series', '30/03/2023', '2', '1'"],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_date_from_filter(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and provide a date range with only date from value as filter in text input field
        Then they should see results based on transferring body and
        matches to date last transferred greater than or equal to date from filter value
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        day = "01"
        month = "10"
        year = "2023"

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&date_from_day="
            + day
            + "&date_from_month="
            + month
            + "&date_from_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'first_body', 'first_series', '14/10/2023', '1', '1'"],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_date_to_filter(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and provide a date range with only date to value as filter in text input field
        Then they should see results based on transferring body and
        matches to date last transferred less than or equal to date to filter value
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        day = "31"
        month = "03"
        year = "2023"

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&date_to_day="
            + day
            + "&date_to_month="
            + month
            + "&date_to_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'first_body', 'second_series', '30/03/2023', '2', '1'"],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_date_from_and_date_to_filter(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and provide a date range with date from and date to value as filter in text input field
        Then they should see results based on transferring body and
        matches to date last transferred between date from and date to filter value
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        date_from_day = "01"
        date_from_month = "07"
        date_from_year = "2023"
        date_to_day = "31"
        date_to_month = "10"
        date_to_year = "2023"
        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&date_from_day="
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
                "'first_body', 'first_series', '14/10/2023', '1', '1', "
                "'first_body', 'third_series', '07/07/2023', '3', '1'"
            ],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_series_and_date_from_filter(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and provide a series value as filter in text input field
        and provide a date range with only date from value as filter in text input field
        Then they should see results based on transferring body and series name and
        matches to date last transferred greater than or equal to date from filter value
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId
        series = "first"
        day = "01"
        month = "10"
        year = "2023"

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&series_filter={series}&date_from_day="
            + day
            + "&date_from_month="
            + month
            + "&date_from_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'first_body', 'first_series', '14/10/2023', '1', '1'"],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_series_and_date_to_filter(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and provide a series value as filter in text input field
        and provide a date range with only date to value as filter in text input field
        Then they should see results based on transferring body and series name and
        matches to date last transferred less than or equal to date to filter value
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId
        series = "second"
        day = "31"
        month = "03"
        year = "2023"

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&series_filter={series}&date_to_day="
            + day
            + "&date_to_month="
            + month
            + "&date_to_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'first_body', 'second_series', '30/03/2023', '2', '1'"],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_series_and_date_from_and_date_to_filter(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and provide a series value as filter in text input field
        and provide a date range with date from and date to value as filter in text input field
        Then they should see results based on transferring body and series name and
        matches to date last transferred between date from and date to filter value
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId
        series = "first"
        date_from_day = "01"
        date_from_month = "07"
        date_from_year = "2023"
        date_to_day = "31"
        date_to_month = "10"
        date_to_year = "2023"
        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&series_filter={series}&date_from_day="
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
            ["'first_body', 'first_series', '14/10/2023', '1', '1'"],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_series_sorting_a_to_z(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and select sorting option as series ascending (A to Z)
        Then they should see results based on transferring body
        sorted in alphabetic order of series (A to Z)
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&sort=series-asc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '14/10/2023', '1', '1', "
                "'first_body', 'second_series', '30/03/2023', '2', '1', "
                "'first_body', 'third_series', '07/07/2023', '3', '1'"
            ],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_series_sorting_z_to_a(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and select sorting option as series descending (Z to A)
        Then they should see results based on transferring body
        sorted in reverse alphabetic order of series (Z to A)
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&sort=series-desc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'third_series', '07/07/2023', '3', '1', "
                "'first_body', 'second_series', '30/03/2023', '2', '1', "
                "'first_body', 'first_series', '14/10/2023', '1', '1'"
            ],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_date_consignment_transferred_sorting_oldest_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and select sorting option as date consignment transferred ascending
        Then they should see results based on transferring body
        sorted in oldest date first order of date consignment transferred
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&sort=last_record_transferred-asc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'second_series', '30/03/2023', '2', '1', "
                "'first_body', 'third_series', '07/07/2023', '3', '1', "
                "'first_body', 'first_series', '14/10/2023', '1', '1'"
            ],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_date_consignment_transferred_sorting_most_recent_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and select sorting option as date consignment transferred descending
        Then they should see results based on transferring body
        sorted in most recent date first order of date consignment transferred
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&sort=last_record_transferred-desc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '14/10/2023', '1', '1', "
                "'first_body', 'third_series', '07/07/2023', '3', '1', "
                "'first_body', 'second_series', '30/03/2023', '2', '1'"
            ],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_records_held_in_series_sorting_most_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and select sorting option as records held in series (most first)
        Then they should see results based on transferring body
        sorted in most number of records held in consignment
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&sort=records_held-desc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'third_series', '07/07/2023', '3', '1', "
                "'first_body', 'second_series', '30/03/2023', '2', '1', "
                "'first_body', 'first_series', '14/10/2023', '1', '1'"
            ],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_records_held_in_series_sorting_least_first(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and select sorting option as records held in series (least first)
        Then they should see results based on transferring body
        sorted in the least number of records held in consignment
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&sort=records_held-asc"
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '14/10/2023', '1', '1', "
                "'first_body', 'second_series', '30/03/2023', '2', '1', "
                "'first_body', 'third_series', '07/07/2023', '3', '1'"
            ],
        ]

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_transferring_body_with_filter_no_results(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and use series_filter with value
        Then if database does not have records and no results found returned
        they should see empty header row on browse transferring body page content.
        """
        transferring_body_id = browse_transferring_body_files[
            0
        ].consignment.series.body.BodyId

        mock_standard_user(
            client,
            browse_transferring_body_files[0].consignment.series.body.Name,
        )

        series = "junk"
        response = client.get(
            f"{self.route_url}?transferring_body_id={transferring_body_id}&series_filter="
            + series
        )

        assert response.status_code == 200
        assert b"You are viewing" in response.data
        assert b"Records found 0" in response.data

        verify_transferring_body_view_header_row(response.data)
