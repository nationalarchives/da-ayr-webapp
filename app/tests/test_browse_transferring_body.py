import pytest
from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html
from app.tests.test_browse import verify_data_rows


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


class TestBrowseTransferringBody:
    @property
    def route_url(self):
        return "/browse/transferring_body"

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

        response = client.get(f"{self.route_url}/{transferring_body_id}")

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
                        "'first_body', 'first_series', '14/10/2023', '1', '1', "
                        "'first_body', 'second_series', '30/03/2023', '2', '1', "
                        "'first_body', 'third_series', '07/07/2023', '3', '1'"
                    ],
                ],
            ),
            (
                "series_filter=second",
                [
                    ["'first_body', 'second_series', '30/03/2023', '2', '1'"],
                ],
            ),
            (
                "date_from_day=01&date_from_month=10&date_from_year=2023",
                [
                    ["'first_body', 'first_series', '14/10/2023', '1', '1'"],
                ],
            ),
            (
                "date_to_day=31&date_to_month=03&date_to_year=2023",
                [
                    ["'first_body', 'second_series', '30/03/2023', '2', '1'"],
                ],
            ),
            (
                "date_from_day=01&date_from_month=07&date_from_year=2023&date_to_day=31"
                "&date_to_month=10&date_to_year=2023",
                [
                    [
                        "'first_body', 'first_series', '14/10/2023', '1', '1', "
                        "'first_body', 'third_series', '07/07/2023', '3', '1'"
                    ],
                ],
            ),
            (
                "series_filter=first&date_from_day=01&date_from_month=10&date_from_year=2023",
                [
                    ["'first_body', 'first_series', '14/10/2023', '1', '1'"],
                ],
            ),
            (
                "series_filter=second&date_to_day=31&date_to_month=03&date_to_year=2023",
                [
                    ["'first_body', 'second_series', '30/03/2023', '2', '1'"],
                ],
            ),
            (
                "series_filter=first&date_from_day=01&date_from_month=07&date_from_year=2023"
                "&date_to_day=31&date_to_month=10&date_to_year=2023",
                [
                    ["'first_body', 'first_series', '14/10/2023', '1', '1'"],
                ],
            ),
            (
                "sort=series-asc",
                [
                    [
                        "'first_body', 'first_series', '14/10/2023', '1', '1', "
                        "'first_body', 'second_series', '30/03/2023', '2', '1', "
                        "'first_body', 'third_series', '07/07/2023', '3', '1'"
                    ],
                ],
            ),
            (
                "sort=series-desc",
                [
                    [
                        "'first_body', 'third_series', '07/07/2023', '3', '1', "
                        "'first_body', 'second_series', '30/03/2023', '2', '1', "
                        "'first_body', 'first_series', '14/10/2023', '1', '1'"
                    ],
                ],
            ),
            (
                "sort=last_record_transferred-asc",
                [
                    [
                        "'first_body', 'second_series', '30/03/2023', '2', '1', "
                        "'first_body', 'third_series', '07/07/2023', '3', '1', "
                        "'first_body', 'first_series', '14/10/2023', '1', '1'"
                    ],
                ],
            ),
            (
                "sort=last_record_transferred-desc",
                [
                    [
                        "'first_body', 'first_series', '14/10/2023', '1', '1', "
                        "'first_body', 'third_series', '07/07/2023', '3', '1', "
                        "'first_body', 'second_series', '30/03/2023', '2', '1'"
                    ],
                ],
            ),
            (
                "sort=records_held-desc",
                [
                    [
                        "'first_body', 'third_series', '07/07/2023', '3', '1', "
                        "'first_body', 'second_series', '30/03/2023', '2', '1', "
                        "'first_body', 'first_series', '14/10/2023', '1', '1'"
                    ],
                ],
            ),
            (
                "sort=records_held-asc",
                [
                    [
                        "'first_body', 'first_series', '14/10/2023', '1', '1', "
                        "'first_body', 'second_series', '30/03/2023', '2', '1', "
                        "'first_body', 'third_series', '07/07/2023', '3', '1'"
                    ],
                ],
            ),
            (
                "sort=records_held-desc&date_from_day=01&date_from_month=01&date_from_year=2023"
                "&date_to_day=31&date_to_month=12&date_to_year=2023",
                [
                    [
                        "'first_body', 'third_series', '07/07/2023', '3', '1', "
                        "'first_body', 'second_series', '30/03/2023', '2', '1', "
                        "'first_body', 'first_series', '14/10/2023', '1', '1'"
                    ],
                ],
            ),
            (
                "sort=last_record_transferred-desc&date_from_day=01&date_from_month=01"
                "&date_from_year=2023&date_to_day=31&date_to_month=12&date_to_year=2023",
                [
                    [
                        "'first_body', 'first_series', '14/10/2023', '1', '1', "
                        "'first_body', 'third_series', '07/07/2023', '3', '1', "
                        "'first_body', 'second_series', '30/03/2023', '2', '1'"
                    ],
                ],
            ),
        ],
    )
    def test_browse_transferring_body_full_test(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_transferring_body_files,
        query_params,
        expected_results,
    ):
        """
        Given a standard user accessing the browse page
        When they make a GET request with a transferring body id
        and provide different filter values
        and sorting orders (asc, desc)
        Then they should see results based on transferring body and
        matches to filter value(s) and the result sorted in sorting order
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
            f"{self.route_url}/{transferring_body_id}?{query_params}"
        )

        assert response.status_code == 200

        verify_transferring_body_view_header_row(response.data)
        verify_data_rows(response.data, expected_results)
