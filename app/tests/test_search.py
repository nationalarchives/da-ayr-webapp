import pytest
from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html


def verify_search_header_row(data):
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
            "Consignment Reference",
            "Title",
            "Status",
            "Record opening",
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


class TestSearch:
    @property
    def route_url(self):
        return "/search"

    def test_search_get(self, client: FlaskClient, mock_superuser):
        """
        Given a superuser accessing the search page
        When they make a GET request
        Then they should see the search form and page content.
        """
        mock_superuser(client)
        response = client.get(f"{self.route_url}")

        assert response.status_code == 200
        assert b"Search" in response.data
        assert b"Search for digital records" in response.data
        assert b"Search" in response.data

    def test_search_top_search(self, client, mock_superuser):
        """
        Given a superuser accessing the search page
        When they make a GET request
        Then they should see the top search component available on search page content.
        """
        mock_superuser(client)

        response = client.get(f"{self.route_url}")

        assert response.status_code == 200

        html = response.data.decode()
        search_html = f"""<div class="search__container govuk-grid-column-full">
    <div class="search__container__content">
        <p class="govuk-body search__heading">Search for digital records</p>
        <form method="get" action="{self.route_url}">
            <div class="govuk-form-group govuk-form-group__search-form">
                <label for="searchInput"></label>
                <input class="govuk-input govuk-!-width-three-quarters"
                       id="searchInput"
                       name="query"
                       type="text"
                       value="">
                <button class="govuk-button govuk-button__search-button"
                        data-module="govuk-button"
                        type="submit">Search</button>
            </div>
            <p class="govuk-body-s">
                Search using a record metadata term, for example – transferring body, series,
                consignment
                ref etc.
            </p>
        </form>
    </div>
</div>"""

        assert_contains_html(
            search_html,
            html,
            "div",
            {"class": "search__container govuk-grid-column-full"},
        )

    def test_search_no_query(self, client: FlaskClient, mock_superuser):
        """
        Given a superuser accessing the search page
        When they make a GET request without a query
        Then they should not see any records found.
        """
        mock_superuser(client)
        form_data = {"foo": "bar"}
        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200
        assert b"records found" not in response.data

    def test_search_with_no_results(self, client: FlaskClient, mock_superuser):
        """
        Given a superuser with a search query
        When they make a request on the search page, and no results are found
        Then they should see no records found.
        """
        mock_superuser(client)

        form_data = {"query": "bar"}
        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200
        assert b"Records found 0"

    @pytest.mark.parametrize(
        "query_params, expected_results",
        [
            (
                "query=junk",
                [
                    [""],
                ],
            ),
            (
                "query=TDR-2023-FI1",
                [
                    [
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '-', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '12/04/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '-', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2023'"
                    ],
                ],
            ),
            (
                "query=docx&sort=series-asc",
                [
                    [
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2023'"
                    ],
                ],
            ),
            (
                "query=docx&sort=series-desc",
                [
                    [
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2023'"
                    ],
                ],
            ),
            (
                "query=docx&sort=consignment-reference-asc",
                [
                    [
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2023'"
                    ],
                ],
            ),
            (
                "query=docx&sort=consignment-reference-desc",
                [
                    [
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2023'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=file_name-asc",
                [
                    [
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '-', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '12/04/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '-', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2023'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=file_name-desc",
                [
                    [
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '-', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '12/04/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '-'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=opening_date-desc",
                [
                    [
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '-', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '-', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '12/04/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=opening_date-asc",
                [
                    [
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '12/04/2023', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '-', "
                        "'first_body', 'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '-'"
                    ],
                ],
            ),
        ],
    )
    def test_search_full_test(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
        query_params,
        expected_results,
    ):
        """
        Given a superuser accessing the search page
        When they make a GET request
        and provide different values as query string
        and sorting orders (asc, desc)
        Then they should see results based on
        matching query string value(s) and the result sorted in sorting order
        on search page content.
        """

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(f"{self.route_url}?{query_params}")

        assert response.status_code == 200

        verify_search_header_row(response.data)
        verify_data_rows(response.data, expected_results)

    def test_search_results_display_single_page(
        self,
        client: FlaskClient,
        app,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user with access to a body, and there are files from that body and another body
            and a search query which matches a property from related file data
        When they make a request on the search page with the search term
        Then a table is populated with the n results with metadata fields for the files from there body.
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        app.config["DEFAULT_PAGE_SIZE"] = 5
        form_data = {"query": "first"}
        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200
        assert b"Records found 5" in response.data

        expected_rows = [
            [
                "'first_body', 'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '-', "
                "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                "'first_body', 'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'first_body', 'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '-', "
                "'first_body', 'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2023'"
            ],
        ]

        verify_search_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

        assert (
            b'<nav class="govuk-pagination govuk-pagination--centred" role="navigation" aria-label="Pagination">'
            not in response.data
        )

    def test_search_results_display_multiple_pages(
        self,
        client: FlaskClient,
        app,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user with access to a body, and there are files from that body and another body
            and a search query which matches a property from related file data
            and the pagination size K is set to less than the number of files in the body
        When they make a request on the search page with the search term
        Then a table is populated with the first K results with metadata fields for the files from there body.
        And the pagination widget is displayed
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        app.config["DEFAULT_PAGE_SIZE"] = 2
        form_data = {"query": "first"}
        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200
        assert b"Records found 5" in response.data

        expected_rows = [
            [
                "'first_body', 'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '-', "
                "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023'"
            ],
        ]

        verify_search_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

        # check pagination
        assert b'aria-label="Page 1"' in response.data
        assert b'aria-label="Page 2"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
        next_option = soup.find("div", {"class": "govuk-pagination__next"})

        assert not previous_option
        assert next_option.text.replace("\n", "").strip("") == "Nextpage"

    def test_search_results_display_first_page(
        self,
        client: FlaskClient,
        app,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user with access to a body, and there are files from that body and another body
            and a search query which matches a property from related file data
            and the pagination size K is set to less than the number of files in the body
        When they make a request on the search page with the search term
        Then a table is populated with the first K results with metadata fields for the files from there body.
        And the pagination widget is displayed (incl. previous page option)
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        app.config["DEFAULT_PAGE_SIZE"] = 2
        form_data = {"query": "first"}

        response = client.get(f"{self.route_url}?page=1", data=form_data)
        # response = client.get(f"{self.route_url}?page=1")

        assert response.status_code == 200
        assert b'aria-label="Page 1"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
        next_option = soup.find("div", {"class": "govuk-pagination__next"})

        expected_rows = [
            [
                "'first_body', 'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '-', "
                "'first_body', 'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023'"
            ],
        ]

        verify_search_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

        assert not previous_option
        assert next_option.text.replace("\n", "").strip("") == "Nextpage"

    def test_search_results_display_middle_page(
        self,
        client: FlaskClient,
        app,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user with access to a body, and there are files from that body and another body
            and a search query which matches a property from related file data
            and the pagination size K is set to less than the number of files in the body
        When they make a request on the search page with the search term
        Then a table is populated with the first K results with metadata fields for the files from there body.
        And the pagination widget is displayed (incl. previous and next page options).
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        app.config["DEFAULT_PAGE_SIZE"] = 2
        form_data = {"query": "first"}

        response = client.get(f"{self.route_url}?page=2", data=form_data)

        assert response.status_code == 200
        assert b'aria-label="Page 2"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        page_options = soup.find_all(
            "span", class_="govuk-pagination__link-title"
        )

        expected_rows = [
            [
                "'first_body', 'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '12/04/2023', "
                "'first_body', 'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '-'"
            ],
        ]

        verify_search_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

        assert (
            " ".join(page_options[0].text.replace("\n", "").split())
            == "Previouspage"
        )
        assert (
            " ".join(page_options[1].text.replace("\n", "").split())
            == "Nextpage"
        )

    def test_search_results_display_last_page(
        self,
        client: FlaskClient,
        app,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user with access to a body, and there are files from that body and another body
            and a search query which matches a property from related file data
            and the pagination size K is set to less than the number of files in the body
        When they make a request on the search page with the search term
        Then a table is populated with the first K results with metadata fields for the files from there body.
        And the pagination widget is displayed (incl. next page option).
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        app.config["DEFAULT_PAGE_SIZE"] = 2
        form_data = {"query": "first"}

        response = client.get(f"{self.route_url}?page=3", data=form_data)

        assert response.status_code == 200
        assert b'aria-label="Page 3"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
        next_option = soup.find("div", {"class": "govuk-pagination__next"})

        expected_rows = [
            [
                "'first_body', 'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2023'"
            ],
        ]

        verify_search_header_row(response.data)
        verify_data_rows(response.data, expected_rows)

        assert (
            " ".join(previous_option.text.replace("\n", "").split())
            == "Previouspage"
        )
        assert not next_option

    def test_search_results_summary_display(
        self, client: FlaskClient, mock_superuser, browse_consignment_files
    ):
        mock_superuser(client)

        form_data = {"query": "fi"}

        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200

        soup = BeautifulSoup(response.data, "html.parser")
        table = soup.find("table")
        headers = table.find_all("th")
        rows = table.find_all("td")

        expected_row = (
            [
                "Results found within each Transferring body",
                "Records found",
            ],
        )
        assert [
            header.text.replace("\n", " ").strip(" ") for header in headers
        ] == expected_row[0]

        expected_rows = [
            [
                "'first_body', '15'",
            ],
        ]

        row_data = ""
        for row_index, row in enumerate(rows):
            row_data = (
                row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
            )
            if row_index < len(rows) - 1:
                row_data = row_data + ", "

        assert [row_data] == expected_rows[0]
