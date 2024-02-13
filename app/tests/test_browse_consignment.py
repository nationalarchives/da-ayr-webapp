from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html


def verify_consignment_view_header_row(data):
    """
    this function check header row column values against expected row
    :param data: response data
    """
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    expected_row = (
        [
            "Last modified",
            "Filename",
            "Status",
            "Record opening date",
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


class TestConsignment:
    @property
    def route_url(self):
        return "/browse"

    def test_browse_consignment_without_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        Then they should see results based on consignment filter on browse page content
        sorted by record status closed first as default.
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(f"/browse?consignment_id={consignment_id}")

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        expected_rows = [
            [
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023', "
                "'20/05/2023', 'fifth_file.doc', 'Open', '-', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_breadcrumb(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        Then they should see results based on consignment filter on browse page content.
        And breadcrumb should show 'Everything' > transferring body name > series name > consignment reference
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(f"/browse?consignment_id={consignment_id}")

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        html = response.data.decode()
        consignment_reference = browse_consignment_files[
            0
        ].consignment.ConsignmentReference
        expected_breadcrumbs_html = f"""
        <div class="govuk-breadcrumbs">
            <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                    <a class="govuk-breadcrumbs__link--record" href="/browse">Everything</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <a class="govuk-breadcrumbs__link--record--transferring-body"
                        href="/browse?transferring_body_id={browse_consignment_files[0].consignment.series.body.BodyId}">{browse_consignment_files[0].consignment.series.body.Name}</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <a class="govuk-breadcrumbs__link--record--series"
                        href="/browse?series_id={browse_consignment_files[0].consignment.series.SeriesId}">{browse_consignment_files[0].consignment.series.Name}</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">{consignment_reference}</span>
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

    def test_browse_consignment_with_date_range_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and use date from and date to filter values
        Then they should see the results by date las modified between date from and date to value
        and sorted by record status ascending default
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        url = (
            f"/browse?consignment_id={consignment_id}"
            "&date_filter_field=date_last_modified"
            "&date_from_day=01"
            "&date_from_month=01"
            "&date_from_year=2020"
            "&date_to_day=10"
            "&date_to_month=03"
            "&date_to_year=2023"
        )

        response = client.get(url)

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        expected_rows = [
            [
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_date_from_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and use date from filter with value and date last modified field
        Then they should see the results by date last modified greater than or equal to date from value
        and sorted by record status ascending default
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        url = (
            f"/browse?consignment_id={consignment_id}"
            "&date_filter_field=date_last_modified"
            "&date_from_day=01"
            "&date_from_month=01"
            "&date_from_year=2020"
        )

        response = client.get(url)

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        expected_rows = [
            [
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023', "
                "'20/05/2023', 'fifth_file.doc', 'Open', '-', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_date_to_filter(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and use date to filter with value and date last modified field
        Then they should see the results by date last modified less than or equal to date from value
        and sorted by record status ascending default
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        url = (
            f"/browse?consignment_id={consignment_id}"
            "&date_filter_field=date_last_modified"
            "&date_to_day=10"
            "&date_to_month=03"
            "&date_to_year=2023"
        )

        response = client.get(url)

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        expected_rows = [
            [
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_sorting_record_status_a_to_z(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and select sorting option as record status ascending
        Then they should see records sorted by closure type in reverse alphabetic order (A to Z)
        on browse page content.
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(
            f"/browse?consignment_id={consignment_id}&sort=closure_type-asc"
        )
        assert response.status_code == 200
        assert b"You are viewing" in response.data
        expected_rows = [
            [
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023', "
                "'20/05/2023', 'fifth_file.doc', 'Open', '-', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-'"
            ],
        ]
        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_sorting_record_status_z_to_a(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and select sorting option as record status descending
        Then they should see records sorted by closure type in reverse alphabetic order (Z to A)
        on browse page content.
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(
            f"/browse?consignment_id={consignment_id}&sort=closure_type-desc"
        )
        assert response.status_code == 200
        assert b"You are viewing" in response.data
        expected_rows = [
            [
                "'20/05/2023', 'fifth_file.doc', 'Open', '-', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-', "
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023'"
            ],
        ]
        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_sorting_last_modified_most_recent_first(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and select sorting option as date last modified descending
        Then they should see records sorted by date last modified most recent first
        on browse page content.
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(
            f"/browse?consignment_id={consignment_id}&sort=date_last_modified-desc"
        )
        assert response.status_code == 200
        assert b"You are viewing" in response.data
        expected_rows = [
            [
                "'20/05/2023', 'fifth_file.doc', 'Open', '-', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023', "
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-'"
            ],
        ]
        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_sorting_last_modified_oldest_first(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and select sorting option as date last modified ascending
        Then they should see records sorted by date last modified oldest first
        on browse page content.
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(
            f"/browse?consignment_id={consignment_id}&sort=date_last_modified-asc"
        )
        assert response.status_code == 200
        assert b"You are viewing" in response.data
        expected_rows = [
            [
                "'15/01/2023', 'second_file.ppt', 'Open', '-', "
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'20/05/2023', 'fifth_file.doc', 'Open', '-'"
            ],
        ]
        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_sorting_filename_a_to_z(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and select sorting option as filename ascending
        Then they should see records sorted by filename in alphabetic order (A to Z)
        on browse page content.
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(
            f"/browse?consignment_id={consignment_id}&sort=file_name-asc"
        )
        assert response.status_code == 200
        assert b"You are viewing" in response.data
        expected_rows = [
            [
                "'20/05/2023', 'fifth_file.doc', 'Open', '-', "
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023'"
            ],
        ]
        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_sorting_filename_z_to_a(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and select sorting option as filename descending
        Then they should see records sorted by filename in alphabetic order (Z to A)
        on browse page content.
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(
            f"/browse?consignment_id={consignment_id}&sort=file_name-desc"
        )
        assert response.status_code == 200
        assert b"You are viewing" in response.data
        expected_rows = [
            [
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'20/05/2023', 'fifth_file.doc', 'Open', '-'"
            ],
        ]
        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_record_status_filter_and_sorting_record_status_z_to_a(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and use record status filter value 'all'
        and use sorting by record status filter descending
        Then they should see the results by record status filter 'all'
        and sorted by record status in reverse alphabetic order (Z to A)
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        # record status filter & open records first
        response = client.get(
            f"/browse?consignment_id={consignment_id}&sort=closure_type-desc&record_status=all"
        )

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        expected_rows = [
            [
                "'20/05/2023', 'fifth_file.doc', 'Open', '-', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-', "
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_date_range_filter_and_sorting_record_status_z_to_a(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and use date from and date to filter values
        and use sorting by record status filter descending
        Then they should see the results by date las modified between date from and date to value
        and sorted by record status in reverse alphabetic order (Z to A)
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        url = (
            f"/browse?consignment_id={consignment_id}"
            "&sort=closure_type-desc"
            "&record_status=all"
            "&date_filter_field=date_last_modified"
            "&date_from_day=01"
            "&date_from_month=01"
            "&date_from_year=2020"
            "&date_to_day=10"
            "&date_to_month=03"
            "&date_to_year=2023"
        )

        response = client.get(url)

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        expected_rows = [
            [
                "'15/01/2023', 'second_file.ppt', 'Open', '-', "
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_date_from_filter_and_sorting_record_status_z_to_a(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and use date from filter with value and date last modified field
        and use sorting by record status filter descending
        Then they should see the results by date last modified greater than or equal to date from value
        and sorted by record status in reverse alphabetic order (Z to A)
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        url = (
            f"/browse?consignment_id={consignment_id}"
            "&sort=closure_type-desc"
            "&record_status=all"
            "&date_filter_field=date_last_modified"
            "&date_from_day=01"
            "&date_from_month=01"
            "&date_from_year=2020"
        )

        response = client.get(url)

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        expected_rows = [
            [
                "'20/05/2023', 'fifth_file.doc', 'Open', '-', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-', "
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_with_date_to_filter_and_sorting_record_status_z_to_a(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and use date to filter with value and date last modified field
        and use sorting by record status filter descending
        Then they should see the results by date last modified less than or equal to date from value
        and sorted by record status in reverse alphabetic order (Z to A)
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        url = (
            f"/browse?consignment_id={consignment_id}"
            "&sort=closure_type-desc"
            "&record_status=all"
            "&date_filter_field=date_last_modified"
            "&date_to_day=10"
            "&date_to_month=03"
            "&date_to_year=2023"
        )

        response = client.get(url)

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        expected_rows = [
            [
                "'15/01/2023', 'second_file.ppt', 'Open', '-', "
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_filter_with_no_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and use date last modified filter with value
        Then if database does not have records and no results found returned
        they should see empty header row on browse transferring body page content.
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(
            f"/browse?consignment_id={consignment_id}"
            "&sort=closure_type-desc"
            "&record_status=all"
            "&date_filter_field=date_last_modified"
            "&date_from_day=01"
            "&date_from_month=05"
            "&date_from_year=2024"
        )

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        verify_consignment_view_header_row(response.data)

    def test_browse_consignment_filter_opening_date_from(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and use opening date filter
        Then they should see a selection of available record data that
        matches the expected data sorted by opening date
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(
            f"/browse?consignment_id={consignment_id}"
            "&sort=opening_date-asc"
            "&record_status=all"
            "&date_filter_field=opening_date"
            "&date_from_day=01"
            "&date_from_month=01"
            "&date_from_year=2023"
        )

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        expected_rows = [
            [
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_filter_opening_date_to(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and use opening date filter
        Then they should see a selection of available record data that
        matches the expected data sorted by opening date
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(
            f"/browse?consignment_id={consignment_id}"
            "&sort=opening_date-asc"
            "&record_status=all"
            "&date_filter_field=opening_date"
            "&date_to_day=03"
            "&date_to_month=04"
            "&date_to_year=2023"
        )

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        expected_rows = [
            [
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_filter_opening_date(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        and use opening date filter
        Then they should see a selection of available record data that
        matches the expected data
        """
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(
            f"/browse?consignment_id={consignment_id}"
            "&sort=closure_type-desc"
            "&record_status=all"
            "&date_filter_field=opening_date"
            "&date_from_day=10"
            "&date_from_month=03"
            "&date_from_year=2023"
            "&date_to_day=20"
            "&date_to_month=10"
            "&date_to_year=2023"
        )

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        expected_rows = [
            [
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)
