import pytest
from bs4 import BeautifulSoup
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


class TestBrowse:
    @property
    def route_url(self):
        return "/browse"

    @property
    def transferring_body_route_url(self):
        return "/browse/transferring_body"

    def test_standard_user_redirected_to_browse_transferring_body_when_accessing_browse(
        self, client: FlaskClient, mock_standard_user
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request
        Then they should be redirected to the transferring_body browse page for
            the body they have access to
        """
        body = BodyFactory()
        mock_standard_user(client, body.Name)

        response = client.get(f"{self.route_url}")

        assert response.status_code == 302
        assert response.headers[
            "Location"
        ] == self.transferring_body_route_url + "/" + str(body.BodyId)

    def test_browse_get_view(self, client: FlaskClient, mock_superuser):
        """
        Given a superuser accessing the browse page
        When they make a GET request
        Then they should see the browse page content.
        """
        mock_superuser(client)

        response = client.get(f"{self.route_url}")

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

        response = client.get(f"{self.route_url}")

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
        response = client.get(f"{self.route_url}", data={"query": query})

        assert response.status_code == 200

        assert b"Search for digital records" in response.data
        assert b"Records found 27" in response.data

    @pytest.mark.parametrize(
        "query_params, expected_results",
        [
            (
                "series_filter=junk",
                [
                    [""],
                ],
            ),
            (
                "",
                [
                    [
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'first_body', 'first_series', '07/02/2023', '3', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                        "'second_body', 'second_series', '26/04/2023', '7', '2', "
                        "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
                    ],
                ],
            ),
            (
                "transferring_body_filter=fi",
                [
                    [
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'first_body', 'first_series', '07/02/2023', '3', '2'"
                    ],
                ],
            ),
            (
                "transferring_body_filter=t",
                [
                    [
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'first_body', 'first_series', '07/02/2023', '3', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                        "'sixth_body', 'sixth_series', '14/10/2023', '2', '1', "
                        "'third_body', 'third_series', '17/06/2023', '3', '2'"
                    ],
                ],
            ),
            (
                "date_from_day=01&date_from_month=10&date_from_year=2023",
                [
                    ["'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"],
                ],
            ),
            (
                "date_to_day=31&date_to_month=03&date_to_year=2023",
                [
                    ["'first_body', 'first_series', '07/02/2023', '3', '2'"],
                ],
            ),
            (
                "series_filter=fi",
                [
                    [
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'first_body', 'first_series', '07/02/2023', '3', '2'"
                    ],
                ],
            ),
            (
                "series_filter=f",
                [
                    [
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'first_body', 'first_series', '07/02/2023', '3', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2'"
                    ],
                ],
            ),
            (
                "date_from_day=01&date_from_month=09&date_from_year=2023",
                [
                    [
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
                    ],
                ],
            ),
            (
                "date_to_day=26&date_to_month=04&date_to_year=2023",
                [
                    [
                        "'first_body', 'first_series', '07/02/2023', '3', '2', "
                        "'second_body', 'second_series', '26/04/2023', '7', '2'"
                    ],
                ],
            ),
            (
                "date_from_day=01&date_from_month=08&date_from_year=2023&date_to_day=31"
                "&date_to_month=10&date_to_year=2023",
                [
                    [
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                        "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
                    ],
                ],
            ),
            (
                "transferring_body_filter=fif&series_filter=fi",
                [
                    ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
                ],
            ),
            (
                "transferring_body_filter=fifth&date_from_day=01&date_from_month=09&date_from_year=2023",
                [
                    ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
                ],
            ),
            (
                "transferring_body_filter=fifth&date_to_day=21&date_to_month=09&date_to_year=2023",
                [
                    ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
                ],
            ),
            (
                "transferring_body_filter=f&date_from_day=01&date_from_month=08&date_from_year=2023&date_to_day=31"
                "&date_to_month=10&date_to_year=2023",
                [
                    [
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2'"
                    ],
                ],
            ),
            (
                "series_filter=fifth&date_from_day=01&date_from_month=09&date_from_year=2023",
                [
                    ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
                ],
            ),
            (
                "series_filter=fifth&date_to_day=21&date_to_month=09&date_to_year=2023",
                [
                    ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
                ],
            ),
            (
                "series_filter=fou&date_from_month=08&date_from_year=2023&date_to_day=31"
                "&date_to_month=10&date_to_year=2023",
                [
                    ["'fourth_body', 'fourth_series', '03/08/2023', '6', '2'"],
                ],
            ),
            (
                "transferring_body_filter=fi&series_filter=fifth&date_from_day=01"
                "&date_from_month=09&date_from_year=2023",
                [
                    ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
                ],
            ),
            (
                "transferring_body_filter=fi&series_filter=fifth&date_to_day=21&"
                "date_to_month=09&date_to_year=2023",
                [
                    ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
                ],
            ),
            (
                "transferring_body_filter=fo&series_filter=fou&date_from_month=08&date_from_year=2023"
                "&date_to_day=31&date_to_month=10&date_to_year=2023",
                [
                    ["'fourth_body', 'fourth_series', '03/08/2023', '6', '2'"],
                ],
            ),
            (
                "transferring_body-asc",
                [
                    [
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'first_body', 'first_series', '07/02/2023', '3', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                        "'second_body', 'second_series', '26/04/2023', '7', '2', "
                        "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
                    ],
                ],
            ),
            (
                "sort=transferring_body-desc",
                [
                    [
                        "'third_body', 'third_series', '17/06/2023', '3', '2', "
                        "'sixth_body', 'sixth_series', '14/10/2023', '2', '1', "
                        "'second_body', 'second_series', '26/04/2023', '7', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                        "'first_body', 'first_series', '07/02/2023', '3', '2'"
                    ],
                ],
            ),
            (
                "sort=series-asc",
                [
                    [
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'first_body', 'first_series', '07/02/2023', '3', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                        "'second_body', 'second_series', '26/04/2023', '7', '2', "
                        "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
                    ],
                ],
            ),
            (
                "sort=series-desc",
                [
                    [
                        "'third_body', 'third_series', '17/06/2023', '3', '2', "
                        "'sixth_body', 'sixth_series', '14/10/2023', '2', '1', "
                        "'second_body', 'second_series', '26/04/2023', '7', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                        "'first_body', 'first_series', '07/02/2023', '3', '2'"
                    ],
                ],
            ),
            (
                "sort=last_record_transferred-asc",
                [
                    [
                        "'first_body', 'first_series', '07/02/2023', '3', '2', "
                        "'second_body', 'second_series', '26/04/2023', '7', '2', "
                        "'third_body', 'third_series', '17/06/2023', '3', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"
                    ],
                ],
            ),
            (
                "sort=last_record_transferred-desc",
                [
                    [
                        "'sixth_body', 'sixth_series', '14/10/2023', '2', '1', "
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                        "'third_body', 'third_series', '17/06/2023', '3', '2', "
                        "'second_body', 'second_series', '26/04/2023', '7', '2'"
                    ],
                ],
            ),
            (
                "sort=last_record_transferred-desc&transferring_body_filter=f",
                [
                    [
                        "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
                        "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
                        "'first_body', 'first_series', '07/02/2023', '3', '2'"
                    ],
                ],
            ),
        ],
    )
    def test_browse_full_test(
        self,
        client: FlaskClient,
        mock_superuser,
        browse_files,
        query_params,
        expected_results,
    ):
        """
        Given a superuser accessing the browse page
        When they make a GET request
        and provide different filter values
        and sorting orders (asc, desc)
        Then they should see results based on
        matching filter value(s) and the result sorted in sorting order
        on browse page content.
        """
        mock_superuser(client)

        response = client.get(f"{self.route_url}?{query_params}")

        assert response.status_code == 200

        verify_browse_view_header_row(response.data)
        verify_data_rows(response.data, expected_results)

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

        response = client.get(f"{self.route_url}?page=1")

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

        response = client.get(f"{self.route_url}?page=2")

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

        response = client.get(f"{self.route_url}?page=3")

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

        response = client.get(f"{self.route_url}?page=1")

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
