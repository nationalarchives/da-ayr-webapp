from bs4 import BeautifulSoup
from flask import url_for
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html
from app.tests.factories import BodyFactory


def verify_browse_view_header_row(data):
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
            "Closure start date",
            "Closure period",
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


def test_standard_user_redirected_to_browse_transferring_body_when_accessing_browse(
    client: FlaskClient, mock_standard_user
):
    """
    Given a standard user accessing the browse page
    When they make a GET request
    Then they should be redirected to the transferring_body browse page for
        the body they have access to
    """
    body = BodyFactory()
    mock_standard_user(client, body.Name)

    response = client.get("/browse")

    assert response.status_code == 302
    assert response.headers["Location"] == url_for(
        "main.browse", transferring_body_id=body.BodyId
    )


class TestBrowse:
    def test_browse_get_view(self, client: FlaskClient, mock_superuser):
        """
        Given a superuser accessing the browse page
        When they make a GET request
        Then they should see the browse page content.
        """
        mock_superuser(client)

        response = client.get("/browse")

        assert response.status_code == 200
        assert b"Search for digital records" in response.data
        assert b"You are viewing" in response.data
        assert b"Everything available to you" in response.data

    def test_browse_check_transferring_bodies_list_filled_for_super_user(
        self, client: FlaskClient, browse_files, mock_superuser
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request
        Then they should see the browse page content
        and transferring body dropdown will be filled with list of all transferring bodies available in database
        """
        mock_superuser(client)

        response = client.get("/browse")

        assert response.status_code == 200

        html = response.data.decode()

        expected_html = f"""
            <select class="govuk-select govuk-select__filters-form-transferring-body-select"
            id="transferring_body_filter" name="transferring_body_filter">
                <option value="all" selected>Choose one...</option>
                <option value="first_body">{browse_files[0].consignment.series.body.Name}</option>
                <option value="second_body">{browse_files[3].consignment.series.body.Name}</option>
                <option value="third_body">{browse_files[10].consignment.series.body.Name}</option>
                <option value="fourth_body">{browse_files[13].consignment.series.body.Name}</option>
                <option value="fifth_body">{browse_files[19].consignment.series.body.Name}</option>
                <option value="sixth_body">{browse_files[25].consignment.series.body.Name}</option>
            </select>
        """

        assert_contains_html(
            expected_html,
            html,
            "select",
            {
                "class": "govuk-select govuk-select__filters-form-transferring-body-select"
            },
        )

    def test_browse_submit_search_query(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a POST request
        Then they should see results in content.
        """
        mock_superuser(client)

        query = "test"
        response = client.post("/browse", data={"query": query})

        assert response.status_code == 200
        assert b"Search for digital records" in response.data
        assert b"Records found 6" in response.data

    def test_browse_get_without_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        Then they should see first five records on browse page content.
        """
        mock_superuser(client)

        response = client.get("/browse")

        assert response.status_code == 200

        expected_rows = [
            [
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                "'first_body', 'first_series', '07/02/2023', '3', '2', "
                "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                "'second_body', 'second_series', '26/04/2023', '7', '2', "
                "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_transferring_body_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and select transferring body as filter from dropdown list
        Then they should see first two records matches to transferring body name on browse page content.
        """
        mock_superuser(client)
        transferring_body = "fi"
        response = client.get(
            "/browse?transferring_body_filter=" + transferring_body
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                "'first_body', 'first_series', '07/02/2023', '3', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_series_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and provide a series value as filter in text input field
        Then they should see first two records matches to series name on browse page content.
        """
        mock_superuser(client)
        series = "fi"
        response = client.get("/browse?series_filter=" + series)

        assert response.status_code == 200

        expected_rows = [
            [
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                "'first_body', 'first_series', '07/02/2023', '3', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_date_from_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and provide a date range with only date from value as filter in text input field
        Then they should see two records matches to date last transferred
        greater than or equal to date from filter value
        on browse page content.
        """
        mock_superuser(client)
        day = "01"
        month = "09"
        year = "2023"
        response = client.get(
            "/browse?date_from_day="
            + day
            + "&date_from_month="
            + month
            + "&date_from_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_date_to_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and provide a date range with only date to value as filter in text input field
        Then they should see two records matches to date last transferred less than or equal to date to filter value
        on browse page content.
        """
        mock_superuser(client)
        day = "26"
        month = "04"
        year = "2023"
        response = client.get(
            "/browse?date_to_day="
            + day
            + "&date_to_month="
            + month
            + "&date_to_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '07/02/2023', '3', '2', "
                "'second_body', 'second_series', '26/04/2023', '7', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_date_from_and_date_to_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and provide a date range with date from and date to value as filter in text input field
        Then they should see three records matches to date last transferred between date from and date to filter value
        on browse page content.
        """
        mock_superuser(client)
        date_from_day = "01"
        date_from_month = "08"
        date_from_year = "2023"
        date_to_day = "31"
        date_to_month = "10"
        date_to_year = "2023"
        response = client.get(
            "/browse?date_from_day="
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
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_transferring_body_and_series_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and select transferring body as filter from dropdown list
        and provide a series value as filter in text input field
        Then they should see one record matches to transferring body name and series name on browse page content.
        """
        mock_superuser(client)
        transferring_body = "fif"
        series = "fi"
        response = client.get(
            "/browse?transferring_body_filter="
            + transferring_body
            + "&series_filter="
            + series
        )

        assert response.status_code == 200

        expected_rows = [
            ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_transferring_body_and_date_from_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and select transferring body as filter from dropdown list
        and provide a date range with only date from value as filter in text input field
        Then they should see one record matches to transferring body name
        and date last transferred greater than or equal to date from filter value
        on browse page content.
        """
        mock_superuser(client)
        transferring_body = "fifth"
        day = "01"
        month = "09"
        year = "2023"
        response = client.get(
            "/browse?transferring_body_filter="
            + transferring_body
            + "&date_from_day="
            + day
            + "&date_from_month="
            + month
            + "&date_from_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_transferring_body_and_date_to_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and select transferring body as filter from dropdown list
        and provide a date range with only date to value as filter in text input field
        Then they should see one record matches to transferring body name
        and date last transferred less than or equal to date to filter value
        on browse page content.
        """
        mock_superuser(client)
        transferring_body = "fifth"
        day = "21"
        month = "09"
        year = "2023"
        response = client.get(
            "/browse?transferring_body_filter="
            + transferring_body
            + "&date_to_day="
            + day
            + "&date_to_month="
            + month
            + "&date_to_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_transferring_body_and_date_from_and_date_to_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and select transferring body as filter from dropdown list
        and provide a date range with date from and date to value as filter in text input field
        Then they should see two records matches to transferring body name
        and date last transferred between date from and date to filter value
        on browse page content.
        """
        mock_superuser(client)
        transferring_body = "f"
        date_from_day = "01"
        date_from_month = "08"
        date_from_year = "2023"
        date_to_day = "31"
        date_to_month = "10"
        date_to_year = "2023"
        response = client.get(
            "/browse?transferring_body_filter="
            + transferring_body
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
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                "'fourth_body', 'fourth_series', '03/08/2023', '6', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_series_and_date_from_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and provide a series value as filter in text input field
        and provide a date range with only date from value as filter in text input field
        Then they should see one record matches to series name
        and date last transferred greater than or equal to date from filter value
        on browse page content.
        """
        mock_superuser(client)
        series = "fifth"
        day = "01"
        month = "09"
        year = "2023"
        response = client.get(
            "/browse?series_filter="
            + series
            + "&date_from_day="
            + day
            + "&date_from_month="
            + month
            + "&date_from_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_series_and_date_to_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and provide a series value as filter in text input field
        and provide a date range with only date to value as filter in text input field
        Then they should see one record matches to series name
        and date last transferred less than or equal to date to filter value
        on browse page content.
        """
        mock_superuser(client)
        series = "fifth"
        day = "21"
        month = "09"
        year = "2023"
        response = client.get(
            "/browse?series_filter="
            + series
            + "&date_to_day="
            + day
            + "&date_to_month="
            + month
            + "&date_to_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_series_and_date_from_and_date_to_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and provide a series value as filter in text input field
        and provide a date range with date from and date to value as filter in text input field
        Then they should see one record matches to series name
        and date last transferred between date from and date to filter value
        on browse page content.
        """
        mock_superuser(client)
        series = "fou"
        date_from_day = "01"
        date_from_month = "08"
        date_from_year = "2023"
        date_to_day = "31"
        date_to_month = "10"
        date_to_year = "2023"
        response = client.get(
            "/browse?series_filter="
            + series
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
            ["'fourth_body', 'fourth_series', '03/08/2023', '6', '2'"],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_transferring_body_and_series_and_date_from_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and select transferring body as filter from dropdown list
        and provide a series value as filter in text input field
        and provide a date range with only date from value as filter in text input field
        Then they should see one record matches to transferring body name, series_name
        and date last transferred greater than or equal to date from filter value
        on browse page content.
        """
        mock_superuser(client)
        transferring_body = "fi"
        series = "fifth"
        day = "01"
        month = "09"
        year = "2023"
        response = client.get(
            "/browse?transferring_body_filter="
            + transferring_body
            + "&series_filter="
            + series
            + "&date_from_day="
            + day
            + "&date_from_month="
            + month
            + "&date_from_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_transferring_body_and_series_and_date_to_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and select transferring body as filter from dropdown list
        and provide a series value as filter in text input field
        and provide a date range with only date to value as filter in text input field
        Then they should see one record matches to transferring body name, series_name
        and date last transferred less than or equal to date to filter value
        on browse page content.
        """
        mock_superuser(client)
        transferring_body = "fi"
        series = "fifth"
        day = "21"
        month = "09"
        year = "2023"
        response = client.get(
            "/browse?transferring_body_filter="
            + transferring_body
            + "&series_filter="
            + series
            + "&date_to_day="
            + day
            + "&date_to_month="
            + month
            + "&date_to_year="
            + year
        )

        assert response.status_code == 200

        expected_rows = [
            ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_get_with_transferring_body_and_series_and_date_from_and_date_to_filter(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        and select transferring body as filter from dropdown list
        and provide a series value as filter in text input field
        and provide a date range with date from and date to value as filter in text input field
        Then they should see one record matches to transferring body name, series_name
        and date last transferred between date from and date to filter value
        on browse page content.
        """
        mock_superuser(client)
        transferring_body = "fo"
        series = "fou"
        date_from_day = "01"
        date_from_month = "08"
        date_from_year = "2023"
        date_to_day = "31"
        date_to_month = "10"
        date_to_year = "2023"
        response = client.get(
            "/browse?transferring_body_filter="
            + transferring_body
            + "&series_filter="
            + series
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
            ["'fourth_body', 'fourth_series', '03/08/2023', '6', '2'"],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_display_first_page(
        self, client: FlaskClient, app, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        Then they should see first page with five records on browse page content
        (excluding previous and incl. next page option).
        """
        mock_superuser(client)

        app.config["DEFAULT_PAGE_SIZE"] = 2

        response = client.get("/browse?page=1")

        assert response.status_code == 200
        assert b'aria-label="Page 1"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
        next_option = soup.find("div", {"class": "govuk-pagination__next"})

        expected_rows = [
            [
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                "'first_body', 'first_series', '07/02/2023', '3', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

        assert not previous_option
        assert next_option.text.replace("\n", "").strip("") == "Nextpage"

    def test_browse_display_middle_page(
        self, client: FlaskClient, app, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        Then they should see first page with five records on browse page content (incl. previous and next page options).
        """
        mock_superuser(client)

        app.config["DEFAULT_PAGE_SIZE"] = 2

        response = client.get("/browse?page=2")

        assert response.status_code == 200
        assert b'aria-label="Page 2"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        page_options = soup.find_all(
            "span", class_="govuk-pagination__link-title"
        )

        expected_rows = [
            [
                "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                "'second_body', 'second_series', '26/04/2023', '7', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

        assert (
            " ".join(page_options[0].text.replace("\n", "").split())
            == "Previouspage"
        )
        assert (
            " ".join(page_options[1].text.replace("\n", "").split())
            == "Nextpage"
        )

    def test_browse_display_last_page(
        self, client: FlaskClient, app, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        Then they should see last page with n records on browse page content
        (incl. previous and excluding next page option).
        """
        mock_superuser(client)

        app.config["DEFAULT_PAGE_SIZE"] = 2

        response = client.get("/browse?page=3")

        assert response.status_code == 200
        assert b'aria-label="Page 3"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
        next_option = soup.find("div", {"class": "govuk-pagination__next"})

        expected_rows = [
            [
                "'sixth_body', 'sixth_series', '14/10/2023', '2', '1', "
                "'third_body', 'third_series', '17/06/2023', '3', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

        assert (
            " ".join(previous_option.text.replace("\n", "").split())
            == "Previouspage"
        )
        assert not next_option

    def test_browse_display_multiple_pages(
        self, client: FlaskClient, app, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request with page as a query string parameter
        Then they should see first page with five records on browse page content (incl. previous and next page options).
        """
        mock_superuser(client)

        app.config["DEFAULT_PAGE_SIZE"] = 2

        response = client.get("/browse?page=1")

        assert response.status_code == 200
        assert b'aria-label="Page 1"' in response.data
        assert b'aria-label="Page 2"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        # page_options = soup.find_all("span", class_="govuk-pagination__link-title")
        previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
        next_option = soup.find("div", {"class": "govuk-pagination__next"})
        expected_rows = [
            [
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                "'first_body', 'first_series', '07/02/2023', '3', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

        assert not previous_option
        assert next_option.text.replace("\n", "").strip("") == "Nextpage"

    def test_browse_with_transferring_body_sorting_a_to_z(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they select sorting option as transferring body ascending (A to Z)
        Then they should see first five records sorted in alphabetic order of transferring body (A to Z)
        on browse page content.
        """
        mock_superuser(client)

        response = client.get("/browse?sort=transferring_body_asc")

        assert response.status_code == 200

        expected_rows = [
            [
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                "'first_body', 'first_series', '07/02/2023', '3', '2', "
                "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                "'second_body', 'second_series', '26/04/2023', '7', '2', "
                "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_with_transferring_body_sorting_z_to_a(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they select sorting option as transferring body descending (Z to A)
        Then they should see first five records sorted in reverse alphabetic order of transferring body (Z to A)
        on browse page content.
        """
        mock_superuser(client)

        response = client.get("/browse?sort=transferring_body_desc")

        assert response.status_code == 200

        expected_rows = [
            [
                "'third_body', 'third_series', '17/06/2023', '3', '2', "
                "'sixth_body', 'sixth_series', '14/10/2023', '2', '1', "
                "'second_body', 'second_series', '26/04/2023', '7', '2', "
                "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                "'first_body', 'first_series', '07/02/2023', '3', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_with_series_sorting_a_to_z(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they select sorting option as series ascending (A to Z)
        Then they should see first five records sorted in alphabetic order of series (A to Z)
        on browse page content.
        """
        mock_superuser(client)

        response = client.get("/browse?sort=series_asc")

        assert response.status_code == 200

        expected_rows = [
            [
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                "'first_body', 'first_series', '07/02/2023', '3', '2', "
                "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                "'second_body', 'second_series', '26/04/2023', '7', '2', "
                "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_with_series_sorting_z_to_a(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they select sorting option as series descending (Z to A)
        Then they should see first five records sorted in reverse alphabetic order of series (Z to A)
        on browse page content.
        """
        mock_superuser(client)

        response = client.get("/browse?sort=series_desc")

        assert response.status_code == 200

        expected_rows = [
            [
                "'third_body', 'third_series', '17/06/2023', '3', '2', "
                "'sixth_body', 'sixth_series', '14/10/2023', '2', '1', "
                "'second_body', 'second_series', '26/04/2023', '7', '2', "
                "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                "'first_body', 'first_series', '07/02/2023', '3', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_with_date_consignment_transferred_sorting_oldest_first(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they select sorting option as date consignment transferred ascending
        Then they should see first five records sorted in oldest date first order of date consignment transferred
        on browse page content.
        """
        mock_superuser(client)

        response = client.get("/browse?sort=last_record_transferred_asc")

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', 'first_series', '07/02/2023', '3', '2', "
                "'second_body', 'second_series', '26/04/2023', '7', '2', "
                "'third_body', 'third_series', '17/06/2023', '3', '2', "
                "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_with_date_consignment_transferred_sorting_most_recent_first(
        self, client: FlaskClient, mock_superuser, browse_files
    ):
        """
        Given a superuser accessing the browse page
        When they select sorting option as date consignment transferred descending
        Then they should see first five records sorted in most recent date first order of date consignment transferred
        on browse page content.
        """
        mock_superuser(client)

        response = client.get("/browse?sort=last_record_transferred_desc")

        assert response.status_code == 200

        expected_rows = [
            [
                "'sixth_body', 'sixth_series', '14/10/2023', '2', '1', "
                "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                "'third_body', 'third_series', '17/06/2023', '3', '2', "
                "'second_body', 'second_series', '26/04/2023', '7', '2'"
            ],
        ]

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)


class TestBrowseTransferringBody:
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
            f"/browse?transferring_body_id={transferring_body_id}"
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
            f"/browse?transferring_body_id={transferring_body_id}"
        )

        assert response.status_code == 200
        assert b"You are viewing" in response.data
        assert b"Records found 3" in response.data

        html = response.data.decode()

        expected_breadcrumbs_html = f"""
        <div class="govuk-breadcrumbs">
            <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record" href="/browse">Everything</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                <p class="govuk-breadcrumbs__link--record">
                {browse_transferring_body_files[0].consignment.series.body.Name}</p>
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
            f"/browse?transferring_body_id={transferring_body_id}&series_filter="
            + series
        )

        assert response.status_code == 200

        expected_rows = [
            ["'first_body', 'second_series', '30/03/2023', '2', '1'"],
        ]

        verify_browse_view_header_row(response.data)
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
            f"/browse?transferring_body_id={transferring_body_id}&date_from_day="
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

        verify_browse_view_header_row(response.data)
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
            f"/browse?transferring_body_id={transferring_body_id}&date_to_day="
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

        verify_browse_view_header_row(response.data)
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
            f"/browse?transferring_body_id={transferring_body_id}&date_from_day="
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

        verify_browse_view_header_row(response.data)
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
            f"/browse?transferring_body_id={transferring_body_id}&series_filter={series}&date_from_day="
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

        verify_browse_view_header_row(response.data)
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
            f"/browse?transferring_body_id={transferring_body_id}&series_filter={series}&date_to_day="
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

        verify_browse_view_header_row(response.data)
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
            f"/browse?transferring_body_id={transferring_body_id}&series_filter={series}&date_from_day="
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

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)


class TestSeries:
    def test_browse_series(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a series id
        Then they should see results based on series filter on browse page content.
        """
        series_id = browse_files[0].consignment.series.SeriesId

        mock_standard_user(client, browse_files[0].consignment.series.body.Name)

        response = client.get(f"/browse?series_id={series_id}")

        assert response.status_code == 200
        assert b"You are viewing" in response.data
        assert b"Records found 2" in response.data

        expected_rows = [
            [
                "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1', "
                "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"
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

        response = client.get(f"/browse?series_id={series_id}")

        assert response.status_code == 200
        assert b"You are viewing" in response.data
        assert b"Records found 2" in response.data

        html = response.data.decode()

        expected_breadcrumbs_html = f"""
        <div class="govuk-breadcrumbs">
            <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                    <a class="govuk-breadcrumbs__link--record" href="/browse">Everything</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <a class="govuk-breadcrumbs__link--record"
                        href="/browse?transferring_body_id={browse_files[0].consignment.series.body.BodyId}">{browse_files[0].consignment.series.body.Name}</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <p class="govuk-breadcrumbs__link--record">{browse_files[0].consignment.series.Name}</p>
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


class TestConsignment:
    def test_browse_consignment(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a user accessing the browse page
        When they make a GET request with a consignment id
        Then they should see results based on consignment filter on browse page content.
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
                "'20/05/2023', 'fifth_file.doc', 'Open', '-', '-', "
                "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', '10 years', "
                "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', '70 years', "
                "'15/01/2023', 'second_file.ppt', 'Open', '-', '-', "
                "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023', '25 years'"
            ],
        ]

        verify_consignment_view_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

    def test_browse_consignment_breadcrumb(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
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
                    <a class="govuk-breadcrumbs__link--record"
                        href="/browse?transferring_body_id={browse_consignment_files[0].consignment.series.body.BodyId}">{browse_consignment_files[0].consignment.series.body.Name}</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <a class="govuk-breadcrumbs__link--record"
                        href="/browse?series_id={browse_consignment_files[0].consignment.series.SeriesId}">{browse_consignment_files[0].consignment.series.Name}</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <p class="govuk-breadcrumbs__link--record">{consignment_reference}</p>
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
