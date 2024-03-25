import pytest
from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html
from app.tests.factories import (
    BodyFactory,
    ConsignmentFactory,
    FileFactory,
    SeriesFactory,
)


def verify_series_view_header_row(data):
    """
    this function check header row column values against expected row
    :param data: response data
    """
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th", class_="browse__series__desktop__header")

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


def verify_series_data_rows(data, expected_rows):
    """
    This function checks data rows for a data table compared with expected rows
    :param data: response data
    :param expected_rows: expected rows to be compared
    """
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    top_rows = table.find_all("tr", class_="browse__mobile-table__top-row")

    row_data = ""
    for row in top_rows:
        cells = row.find_all("td")
        for cell_index, cell in enumerate(cells):
            row_data += "'" + cell.text.replace("\n", " ").strip(" ") + "'"
            if cell_index < len(cells) - 1:
                row_data += ", "
        row_data += ", "

    # Remove the extra comma at the end of row_data
    row_data = row_data.rstrip(", ")

    assert [row_data] == expected_rows[0]


class TestSeries:
    @property
    def route_url(self):
        return "/browse/series"

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

        response = client.get(f"{self.route_url}/{series_id}")

        assert response.status_code == 200
        assert b"You are viewing" in response.data

        html = response.data.decode()

        expected_breadcrumbs_html = f"""
        <div class="govuk-breadcrumbs">
            <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record" href="/browse">Everything</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record--transferring-body"
                    href="/browse/transferring_body/{browse_files[0].consignment.series.body.BodyId}">{browse_files[0].consignment.series.body.Name}</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">
                {browse_files[0].consignment.series.Name}</span>
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

    def test_browse_series_filter_no_results(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a user accessing the browse series page
        When they make a GET request with a transferring body id and provide filter value in query string
        Then if no data returned based on filter value
        they should see the browse series page content with no results found.
        """
        series_id = browse_files[0].consignment.series.SeriesId

        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        response = client.get(
            f"{self.route_url}/{series_id}?date_from_day=01&date_from_month=03&date_from_year=2024"
        )

        html = response.data.decode()

        expected_html = """
        <ul class="govuk-list govuk-list--bullet">
        <li>
            Try changing or removing one or more applied
                filters.
        </li>
        <li>Alternatively, use the breadcrumbs to navigate back to the browse view.</li>
    </ul>"""
        assert response.status_code == 200
        assert b"No results found" in response.data
        assert_contains_html(
            expected_html,
            html,
            "ul",
            {"class": "govuk-list govuk-list--bullet"},
        )

    @pytest.mark.parametrize(
        "query_params, expected_results",
        [
            (
                "",
                [
                    [
                        "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                        "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
                    ],
                ],
            ),
            (
                "date_from_day=01&date_from_month=02&date_from_year=2023",
                [
                    [
                        "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"
                    ],
                ],
            ),
            (
                "date_to_day=31&date_to_month=01&date_to_year=2023",
                [
                    [
                        "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
                    ],
                ],
            ),
            (
                "date_from_day=01&date_from_month=01&date_from_year=2023&date_to_day=27"
                "&date_to_month=02&date_to_year=2023",
                [
                    [
                        "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                        "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
                    ],
                ],
            ),
            (
                "sort=last_record_transferred-asc",
                [
                    [
                        "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1', "
                        "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"
                    ],
                ],
            ),
            (
                "sort=last_record_transferred-desc",
                [
                    [
                        "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                        "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
                    ],
                ],
            ),
            (
                "sort=consignment_reference-desc",
                [
                    [
                        "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                        "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
                    ],
                ],
            ),
            (
                "sort=consignment_reference-asc",
                [
                    [
                        "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1', "
                        "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"
                    ],
                ],
            ),
            (
                "sort=records_held-asc",
                [
                    [
                        "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1', "
                        "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"
                    ],
                ],
            ),
            (
                "sort=records_held-desc",
                [
                    [
                        "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                        "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
                    ],
                ],
            ),
            (
                "sort=consignment_reference-asc&date_from_day=01&date_from_month=01"
                "&date_from_year=2023&date_to_day=27&date_to_month=02&date_to_year=2023",
                [
                    [
                        "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1', "
                        "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"
                    ],
                ],
            ),
            (
                "sort=records_held-desc&date_from_day=01&date_from_month=01&date_from_year=2023"
                "&date_to_day=27&date_to_month=02&date_to_year=2023",
                [
                    [
                        "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2', "
                        "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1'"
                    ],
                ],
            ),
        ],
    )
    def test_browse_series_full_test(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
        query_params,
        expected_results,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a series id
        and provide different filter values
        and sorting orders (asc, desc)
        Then they should see results based on series and
        matches to filter value(s) and the result sorted in sorting order
        on browse page content.
        """
        mock_standard_user(
            client,
            browse_files[0].consignment.series.body.Name,
        )

        series_id = browse_files[0].consignment.series.SeriesId

        response = client.get(f"{self.route_url}/{series_id}?{query_params}")

        assert response.status_code == 200

        verify_series_view_header_row(response.data)
        verify_series_data_rows(response.data, expected_results)

    def test_browse_series_standard_user_accessing_series_from_different_transferring_body(
        self,
        client: FlaskClient,
        mock_standard_user,
    ):
        """
        Given a Series in a Body with Name "foo" and id series_id
        And a standard user with access to Body "bar"
        When they make a GET request to `browse/series/{series_id}`
        Then they should receive a 404 response
        """
        series = SeriesFactory(body=BodyFactory(Name="foo"))
        FileFactory(consignment=ConsignmentFactory(series=series))

        mock_standard_user(client, "bar")

        response = client.get(f"{self.route_url}/{series.SeriesId}")

        assert response.status_code == 404
