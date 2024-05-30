import pytest
from bs4 import BeautifulSoup
from flask import url_for
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html
from app.tests.test_browse import verify_desktop_data_rows
from app.tests.utils import decompose_desktop_invisible_elements


def verify_search_desktop_transferring_body_header_row(data):
    """
    this function check header row column values against expected row
    :param data: response data
    """
    soup = BeautifulSoup(data, "html.parser")
    decompose_desktop_invisible_elements(soup)
    table = soup.find("table")
    headers = table.find_all("th")

    expected_row = (
        [
            "Series reference",
            "Consignment reference",
            "File name",
            "Status",
            "Record opening date",
        ],
    )
    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_row[0]


def verify_search_results_summary_header_row(data):
    """
    this function check header row column values against expected row
    :param data: response data
    """
    soup = BeautifulSoup(data, "html.parser")
    decompose_desktop_invisible_elements(soup)
    table = soup.find("table")
    headers = table.find_all("th")

    expected_row = (
        [
            "Results found within each Transferring body",
            "Records found",
        ],
    )
    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_row[0]


class TestSearchRedirect:
    @property
    def route_url(self):
        return "/search"

    def test_search_route_redirect_all_access_user(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an all_access_user accessing the search route
        When they make a GET request
        Then they should see the search results summary page content.
        """
        mock_all_access_user(client)

        query = "fi"
        form_data = {"query": query}

        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 302
        assert response.headers["Location"] == url_for(
            "main.search_results_summary", query=query
        )

    def test_search_route_redirect_standard_user(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a standard user accessing the search route
        When they make a GET request
        Then they should see the search transferring body page content.
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        query = "fi"
        form_data = {"query": query}

        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 302
        assert response.headers["Location"] == url_for(
            "main.search_transferring_body",
            _id=str(transferring_body_id),
            query=query,
        )


class TestSearchResultsSummary:
    @property
    def route_url(self):
        return "/search_results_summary"

    @property
    def browse_all_route_url(self):
        return "/browse"

    def test_search_results_summary_get(
        self, app, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an all_access_user accessing the search results summary page
        When they make a GET request
        Then they should see the search form and page content.
        """
        mock_all_access_user(client)
        response = client.get(f"{self.route_url}")

        assert response.status_code == 200
        assert b"Search for digital records" in response.data

        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.title
        assert (
            title_tag.string
            == f"Search results summary – {app.config['SERVICE_NAME']} – GOV.UK"
        )

    def test_search_results_summary_top_search(
        self, client, mock_all_access_user
    ):
        """
        Given an all_access_user accessing the search results summary page
        When they make a GET request
        Then they should see the top search component available on search page content.
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}")

        assert response.status_code == 200

        html = response.data.decode()
        search_html = """<div class="search__container govuk-grid-column-full">
    <div class="search__container__content">
        <label class="govuk-label search__heading" for="search-input">Search for digital records</label>
        <form method="get" action="/search">
            <div class="govuk-form-group govuk-form-group__search-form">
                <input class="govuk-input govuk-!-width-three-quarters"
                       id="search-input"
                       name="query"
                       type="text"
                       value="">
                <button class="govuk-button govuk-button__search-button"
                        data-module="govuk-button"
                        type="submit">Search</button>
            <p class="govuk-body-s">
                Search by file name, transferring body, series or consignment reference.
            </p>
            </div>
        </form>
    </div>
</div>"""

        assert_contains_html(
            search_html,
            html,
            "div",
            {"class": "search__container govuk-grid-column-full"},
        )

    def test_search_results_summary_no_query(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an all_access_user accessing the search results summary page
        When they make a GET request without a query
        Then they should not see any results on the page.
        """
        mock_all_access_user(client)
        form_data = {"foo": "bar"}
        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200
        assert b"records found" not in response.data

    def test_search_results_summary_with_no_results(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an all_access_user with a search results summary query
        When they make a request on the search results summary page, and no results are found
        Then they should see not see any results on the page.
        """
        mock_all_access_user(client)

        form_data = {"query": "junk"}
        response = client.get(f"{self.route_url}", data=form_data)
        html = response.data.decode()

        expected_html = """
        <ul class="govuk-list govuk-list--bullet">
        <li>
        Try changing or removing one or more applied
                    search terms.
        </li>
        <li>
        Alternatively, use the breadcrumbs to navigate back to the browse view.
        </li>
        </ul>"""
        assert response.status_code == 200
        assert b"No results found" in response.data
        assert_contains_html(
            expected_html,
            html,
            "ul",
            {"class": "govuk-list govuk-list--bullet"},
        )

    def test_search_results_summary_with_results_single_term(
        self,
        client: FlaskClient,
        mock_all_access_user,
        browse_consignment_files,
    ):
        """
        Given an all_access_user
        When they make a request on the search results summary page with the single search term
        Then they should be redirected to search results summary screen
        with search results summary page content
        """
        mock_all_access_user(client)

        form_data = {"query": "fi"}

        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', '5'",
            ],
        ]

        verify_search_results_summary_header_row(response.data)
        verify_desktop_data_rows(response.data, expected_rows)

    def test_search_results_summary_with_results_multiple_terms(
        self,
        client: FlaskClient,
        mock_all_access_user,
        browse_consignment_files,
    ):
        """
        Given an all_access_user
        When they make a request on the search results summary page with the single search term
        Then they should be redirected to search results summary screen
        with search results summary page content
        """
        mock_all_access_user(client)

        form_data = {"query": "fi, body"}

        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200

        expected_rows = [
            [
                "'first_body', '5'",
            ],
        ]

        verify_search_results_summary_header_row(response.data)
        verify_desktop_data_rows(response.data, expected_rows)

    def test_search_results_summary_breadcrumbs(
        self,
        client: FlaskClient,
        mock_all_access_user,
        browse_consignment_files,
    ):
        """
        Given an all_access_user
        When they make a request on the search results summary page with the search term
        Then they should be redirected to search results summary screen
        and see breadcrumb values All available records > Results summary
        with search results summary page content
        """
        mock_all_access_user(client)

        form_data = {"query": "fi"}

        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200

        html = response.data.decode()

        search_html = f"""<div class="govuk-breadcrumbs  ">
    <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record" href="{self.browse_all_route_url}">All available records</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">Results summary</span>
                </li>
    </ol>
</div>"""
        assert_contains_html(
            search_html,
            html,
            "div",
            {"class": "govuk-breadcrumbs"},
        )


class TestSearchTransferringBody:
    @property
    def route_url(self):
        return "/search/transferring_body"

    @property
    def search_results_summary_route_url(self):
        return "/search_results_summary"

    @property
    def browse_all_route_url(self):
        return "/browse"

    @property
    def browse_transferring_body_route_url(self):
        return f"{self.browse_all_route_url}/transferring_body"

    def test_search_transferring_body_get(
        self,
        app,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user accessing the search transferring body page
        When they make a GET request
        Then they should see the search form and page content.
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(f"{self.route_url}/{transferring_body_id}")

        assert response.status_code == 200
        assert b"Search" in response.data
        assert b"Search for digital records" in response.data
        assert b"Search" in response.data

        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.title
        assert (
            title_tag.string
            == f"Search results – {app.config['SERVICE_NAME']} – GOV.UK"
        )

    def test_search_transferring_body_top_search(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given a standard user accessing the search transferring body page
        When they make a GET request
        Then they should see the top search component available on search page content.
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(f"{self.route_url}/{transferring_body_id}")

        assert response.status_code == 200

        html = response.data.decode()

        search_html = """<div class="search__container govuk-grid-column-full">
    <div class="search__container__content">
        <label class="govuk-label search__heading" for="search-input">Search for digital records</label>
        <form method="get" action="/search">
            <div class="govuk-form-group govuk-form-group__search-form">
                <input class="govuk-input govuk-!-width-three-quarters"
                       id="search-input"
                       name="query"
                       type="text"
                       value="">
                <button class="govuk-button govuk-button__search-button"
                        data-module="govuk-button"
                        type="submit">Search</button>
            <p class="govuk-body-s">
                Search by file name, series or consignment reference.
            </p>
            </div>
        </form>
    </div>
</div>"""

        assert_contains_html(
            search_html,
            html,
            "div",
            {"class": "search__container govuk-grid-column-full"},
        )

    def test_search_transferring_body_no_query(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a standard user accessing the search transferring body page
        When they make a GET request without a query
        Then they should not see any results on the page.
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        form_data = {"foo": "bar"}

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200
        assert b"records found" not in response.data

    def test_search_transferring_body_with_no_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a standard user with a search transferring body page
        When they make a request and no results are found
        Then they should not see search results on the page.
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        form_data = {"query": "junk"}

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        html = response.data.decode()

        expected_html = """
        <ul class="govuk-list govuk-list--bullet">
        <li>
        Try changing or removing one or more applied
                    search terms.
        </li>
        <li>
        Alternatively, use the breadcrumbs to navigate back to the browse view.
        </li>
        </ul>"""
        assert response.status_code == 200
        assert b"No results found" in response.data
        assert_contains_html(
            expected_html,
            html,
            "ul",
            {"class": "govuk-list govuk-list--bullet"},
        )

    def test_search_transferring_body_with_table_data_links(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
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

        form_data = {"query": "first_file"}

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        browse_series_route_url = f"{self.browse_all_route_url}/series"
        browse_consignment_route_url = (
            f"{self.browse_all_route_url}/consignment"
        )
        record_route_url = "/record"

        series_id = browse_consignment_files[0].consignment.series.SeriesId
        consignment_id = browse_consignment_files[0].consignment.ConsignmentId
        file_id = browse_consignment_files[0].FileId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200
        assert b"Records found 1" in response.data

        verify_search_desktop_transferring_body_header_row(response.data)

        table = BeautifulSoup(response.data, "html.parser").find("table")
        decompose_desktop_invisible_elements(table)
        anchors = table.find_all("a")
        rows = table.find_all("td")

        expected_anchors_hrefs = [
            f"""{browse_series_route_url}/{series_id}""",
            f"""{browse_consignment_route_url}/{consignment_id}""",
            f"""{record_route_url}/{file_id}""",
        ]
        expected_beginning_rows = [
            "first_series",
            "TDR-2023-FI1",
            "first_file.docx",
        ]
        expected_anchors_text = expected_beginning_rows
        expected_all_rows_text = expected_beginning_rows + [
            "Closed",
            "25/02/2023",
        ]

        assert [anchor["href"] for anchor in anchors] == expected_anchors_hrefs
        assert [
            anchor.get_text() for anchor in anchors
        ] == expected_anchors_text
        assert (
            list(filter(None, [row.get_text(strip=True) for row in rows]))
            == expected_all_rows_text
        )

    @pytest.mark.parametrize(
        "query_params, expected_results",
        [
            (
                "query=TDR-2023-FI1",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                        "'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1,th",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1,second",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '–'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1,docx",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=file_name-asc",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                        "'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=file_name-desc",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090', "
                        "'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=opening_date-desc",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090', "
                        "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=opening_date-asc",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090', "
                        "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '–'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=closure_type-asc",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090', "
                        "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '–'"
                    ]
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=closure_type-desc",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090'"
                    ]
                ],
            ),
            (
                "query=TDR-2023-FI1,docx&sort=opening_date-asc",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1,doc&sort=opening_date-asc",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090', "
                        "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–'"
                    ],
                ],
            ),
        ],
    )
    def test_search_transferring_body_results_full_test(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
        query_params,
        expected_results,
    ):
        """
        Given a standard user accessing the search transferring body page
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

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}?{query_params}"
        )

        assert response.status_code == 200

        verify_search_desktop_transferring_body_header_row(response.data)
        verify_desktop_data_rows(response.data, expected_results)

    def test_search_transferring_body_results_display_single_page(
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

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200
        assert b"Records found 5" in response.data

        expected_rows = [
            [
                "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–', "
                "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                "'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '–', "
                "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090'"
            ],
        ]

        verify_search_desktop_transferring_body_header_row(response.data)
        verify_desktop_data_rows(response.data, expected_rows)

        assert (
            b'<nav class="govuk-pagination govuk-pagination--centred" role="navigation" aria-label="Pagination">'
            not in response.data
        )

    def test_search_transferring_body_results_display_multiple_pages(
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

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200
        assert b"Records found 5" in response.data

        expected_rows = [
            [
                "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–', "
                "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023'"
            ],
        ]

        verify_search_desktop_transferring_body_header_row(response.data)
        verify_desktop_data_rows(response.data, expected_rows)

        # check pagination
        assert b'aria-label="Page 1"' in response.data
        assert b'aria-label="Page 2"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
        next_option = soup.find("div", {"class": "govuk-pagination__next"})

        assert not previous_option
        assert next_option.text.replace("\n", "").strip("") == "Nextpage"

    def test_search_transferring_body_results_display_first_page(
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

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}?page=1", data=form_data
        )

        assert response.status_code == 200
        assert b'aria-label="Page 1"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
        next_option = soup.find("div", {"class": "govuk-pagination__next"})

        expected_rows = [
            [
                "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–', "
                "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023'"
            ],
        ]

        verify_search_desktop_transferring_body_header_row(response.data)
        verify_desktop_data_rows(response.data, expected_rows)

        assert not previous_option
        assert next_option.text.replace("\n", "").strip("") == "Nextpage"

    def test_search_transferring_body_results_display_middle_page(
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

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}?page=2", data=form_data
        )

        assert response.status_code == 200
        assert b'aria-label="Page 2"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        page_options = soup.find_all(
            "span", class_="govuk-pagination__link-title"
        )

        expected_rows = [
            [
                "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                "'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '–'"
            ],
        ]

        verify_search_desktop_transferring_body_header_row(response.data)
        verify_desktop_data_rows(response.data, expected_rows)

        assert (
            " ".join(page_options[0].text.replace("\n", "").split())
            == "Previouspage"
        )
        assert (
            " ".join(page_options[1].text.replace("\n", "").split())
            == "Nextpage"
        )

    def test_search_transferring_body_results_display_last_page(
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

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}?page=3", data=form_data
        )

        assert response.status_code == 200
        assert b'aria-label="Page 3"' in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
        next_option = soup.find("div", {"class": "govuk-pagination__next"})

        expected_rows = [
            [
                "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090'"
            ],
        ]

        verify_search_desktop_transferring_body_header_row(response.data)
        verify_desktop_data_rows(response.data, expected_rows)

        assert (
            " ".join(previous_option.text.replace("\n", "").split())
            == "Previouspage"
        )
        assert not next_option

    def test_search_transferring_body_breadcrumbs_all_access_user_single_term(
        self,
        client: FlaskClient,
        mock_all_access_user,
        browse_consignment_files,
    ):
        """
        Given an all_access_user
        When they make a request on the search transferring body page with the search term
        Then they should be redirected to search transferring body screen
        with search results summary page content
        and see a bread crumbs rendered as All available records > Results summary > Transferring body > ‘Search term’
        """
        mock_all_access_user(client)

        query = "fi"
        form_data = {"query": query}

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200

        html = response.data.decode()
        search_html = f"""<div class="govuk-breadcrumbs  ">
    <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record" href="{self.browse_all_route_url}">All available records</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <a class="govuk-breadcrumbs__link--record--transferring-body"
                           href="{self.search_results_summary_route_url}?query={query}">Results summary</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                        <a class="govuk-breadcrumbs__link--record--transferring-body"
                           href="{self.browse_transferring_body_route_url}/{transferring_body_id}">first_body</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">‘{query}’</span>
                </li>
    </ol>
    </div>"""

        assert_contains_html(
            search_html,
            html,
            "div",
            {"class": "govuk-breadcrumbs"},
        )

    def test_search_transferring_body_breadcrumbs_all_access_user_multiple_terms(
        self,
        client: FlaskClient,
        mock_all_access_user,
        browse_consignment_files,
    ):
        """
        Given an all_access_user
        When they make a request on the search transferring body page with the search term
        Then they should be redirected to search transferring body screen
        with search results summary page content
        and see a bread crumbs rendered as All available records > Results summary > Transferring body > ‘Search term’
        """
        mock_all_access_user(client)

        term1 = "fi"
        term2 = "second"
        query = term1 + "," + term2
        form_data = {"query": query}

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200

        html = response.data.decode()
        search_html = f"""<div class="govuk-breadcrumbs  ">
    <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record" href="{self.browse_all_route_url}">All available records</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <a class="govuk-breadcrumbs__link--record--transferring-body"
                           href="{self.search_results_summary_route_url}?query={query}">Results summary</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                        <a class="govuk-breadcrumbs__link--record--transferring-body"
                           href="{self.browse_transferring_body_route_url}/{transferring_body_id}">first_body</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">‘{term1}’ + ‘{term2}’</span>
                </li>
    </ol>
    </div>"""

        assert_contains_html(
            search_html,
            html,
            "div",
            {"class": "govuk-breadcrumbs"},
        )

    def test_search_transferring_body_breadcrumbs_standard_user_single_search_term(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a standard user
        When they make a request on the search transferring body page with the search term
        Then they should be redirected to search transferring body screen
        with search results summary page content
        and see a bread crumbs rendered as All available records > Results summary > Transferring body > ‘Search term’
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        query = "fi"
        form_data = {"query": query}

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200

        html = response.data.decode()
        search_html = f"""<div class="govuk-breadcrumbs  ">
    <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                        <a class="govuk-breadcrumbs__link--record--transferring-body"
                           href="{self.browse_transferring_body_route_url}/{transferring_body_id}">first_body</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">‘{query}’</span>
                </li>
    </ol>
</div>"""

        assert_contains_html(
            search_html,
            html,
            "div",
            {"class": "govuk-breadcrumbs"},
        )

    def test_search_transferring_body_breadcrumbs_standard_user_multiple_search_terms(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a standard user
        When they make a request on the search transferring body page with the search term
        Then they should be redirected to search transferring body screen
        with search results summary page content
        and see a bread crumbs rendered as All available records > Results summary > Transferring body >
        ‘Search term’ + ‘Search term’
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        term1 = "fi"
        term2 = "st"
        form_data = {"query": term1 + "," + term2}

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200

        html = response.data.decode()
        search_html = f"""<div class="govuk-breadcrumbs  ">
    <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                        <a class="govuk-breadcrumbs__link--record--transferring-body"
                           href="{self.browse_transferring_body_route_url}/{transferring_body_id}">first_body</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">‘{term1}’ + ‘{term2}’</span>
                </li>
    </ol>
</div>"""

        assert_contains_html(
            search_html,
            html,
            "div",
            {"class": "govuk-breadcrumbs"},
        )

    def test_search_transferring_body_breadcrumbs_standard_user_invalid_search_terms(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given an all_access_user
        When they make a request on the search transferring body page with the search term
        Then they should be redirected to search transferring body screen
        with search results summary page content
        and see a bread crumbs rendered as All available records > Results summary > Transferring body > ‘Search term’
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        # added blank search term
        query = "fi"
        form_data = {"query": query + ", "}

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200

        html = response.data.decode()
        search_html = f"""<div class="govuk-breadcrumbs  ">
    <ol class="govuk-breadcrumbs__list">
                <li class="govuk-breadcrumbs__list-item">
                        <a class="govuk-breadcrumbs__link--record--transferring-body"
                           href="{self.browse_transferring_body_route_url}/{transferring_body_id}">first_body</a>
                </li>
                <li class="govuk-breadcrumbs__list-item">
                    <span class="govuk-breadcrumbs__link govuk-breadcrumbs__link--record">‘{query}’</span>
                </li>
    </ol>
</div>"""

        assert_contains_html(
            search_html,
            html,
            "div",
            {"class": "govuk-breadcrumbs"},
        )

    def test_search_transferring_body_display_filter_tray_all_access_user(
        self, client, mock_all_access_user, browse_consignment_files
    ):
        """
        Given an all access user accessing the search transferring body page
        When they make a GET request
        Then they should see the filter tray component available on search page content
        and 'Clear all' link should redirect the user to 'browse all' page.
        """
        mock_all_access_user(client)

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        term1 = "TDR-2023-FI1"
        term2 = "first"
        query = f"{term1},{term2}"

        form_data = {"query": query}
        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200

        html = response.data.decode()

        search_filter_html = f"""
        <div class="govuk-grid-column-one-third govuk-grid-column-one-third--browse-all-filters">
            <div class="browse-all-filter-container">
                <div class="browse-filter__header">
                    <h2 class="govuk-heading-m govuk-heading-m--search">
                        <label class="govuk-label govuk-heading-m govuk-heading-m--search"
                        for="search_filter">Search within results</label>
                    </h2>
                </div>
                <div class="govuk-form-group govuk-form-group--search-all-filter">
                    <input class="govuk-input govuk-!-width-full govuk-input--browse-all-input"
                    id="search_filter"
                    name="search_filter"
                    type="text">
                </div>
                <div class="search-form__buttons">
                    <button
                    type="submit"
                    class="govuk-button govuk-button__search-filters-form-apply-button"
                    data-module="govuk-button">
                        Apply terms
                    </button>
                    <a
                        class="govuk-link govuk-link--transferring-filter"
                        href="{self.browse_all_route_url}#browse-records"
                    >
                        Clear all terms
                    </a>
                </div>
                <h3 class="govuk-heading-s govuk-heading-s--search-term">Search terms applied</h3>
                <div class="ayr-filter-tags">
                        <div class="search-term">
                            <button
                                type="button"
                                class="button-search-term"
                                data-module="search-term-button"
                                aria-label="Remove filter for '{term1}'"
                            >
                                <a href="{self.route_url}/{transferring_body_id}?query={term2}">
                                    {term1}
                                    <img
                                        src="/assets/image/cancel-filters.svg"
                                        height="30px"
                                        width="30px"
                                        class="close-icon"
                                        alt="">
                                </a>
                            </button>
                        </div>

                        <div class="search-term">
                            <button
                                type="button"
                                class="button-search-term"
                                data-module="search-term-button"
                                aria-label="Remove filter for '{term2}'"
                            >
                                <a href="{self.route_url}/{transferring_body_id}?query={term1}">
                                    {term2}
                                    <img
                                        src="/assets/image/cancel-filters.svg"
                                        height="30px"
                                        width="30px"
                                        class="close-icon"
                                        alt="">
                                </a>
                            </button>
                        </div>
                </div>
            </div>
        </div>
        """

        assert_contains_html(
            search_filter_html,
            html,
            "div",
            {
                "class": "govuk-grid-column-one-third govuk-grid-column-one-third--browse-all-filters"
            },
        )

    def test_search_transferring_body_display_filter_tray_standard_user(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given a standard user accessing the search transferring body page
        When they make a GET request
        Then they should see the filter tray component available on search page content
        and 'Clear all' link should redirect the user to 'browse transferring body' page.
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        term1 = "TDR-2023-FI1"
        term2 = "first"
        query = f"{term1},{term2}"

        form_data = {"query": query}
        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200

        html = response.data.decode()

        search_filter_html = f"""
        <div class="govuk-grid-column-one-third govuk-grid-column-one-third--browse-all-filters">
            <div class="browse-all-filter-container">
                <div class="browse-filter__header">
                    <h2 class="govuk-heading-m govuk-heading-m--search">
                        <label class="govuk-label govuk-heading-m govuk-heading-m--search"
                        for="search_filter">Search within results</label>
                    </h2>
                </div>
                <div class="govuk-form-group govuk-form-group--search-all-filter">
                    <input class="govuk-input govuk-!-width-full govuk-input--browse-all-input"
                    id="search_filter"
                    name="search_filter"
                    type="text">
                </div>
                <div class="search-form__buttons">
                    <button
                        type="submit"
                        class="govuk-button govuk-button__search-filters-form-apply-button"
                        data-module="govuk-button"
                    >
                        Apply terms
                    </button>
                    <a
                        class="govuk-link govuk-link--transferring-filter"
                        href="{self.browse_transferring_body_route_url}/{transferring_body_id}#browse-records"
                    >
                        Clear all terms
                    </a>
                </div>
                <h3 class="govuk-heading-s govuk-heading-s--search-term">Search terms applied</h3>
                <div class="ayr-filter-tags">
                        <div class="search-term">
                            <button
                                type="button"
                                class="button-search-term"
                                data-module="search-term-button"
                                aria-label="Remove filter for '{term1}'"
                            >
                                <a href="{self.route_url}/{transferring_body_id}?query={term2}">
                                    {term1}
                                    <img
                                        src="/assets/image/cancel-filters.svg"
                                        height="30px"
                                        width="30px"
                                        class="close-icon"
                                        alt=""
                                    >
                                </a>
                            </button>
                        </div>

                        <div class="search-term">
                            <button
                                type="button"
                                class="button-search-term"
                                data-module="search-term-button"
                                aria-label="Remove filter for '{term2}'"
                            >
                                <a href="{self.route_url}/{transferring_body_id}?query={term1}">
                                    {term2}
                                    <img
                                        src="/assets/image/cancel-filters.svg"
                                        height="30px"
                                        width="30px"
                                        class="close-icon"
                                        alt=""
                                    >
                                </a>
                            </button>
                        </div>
                </div>
            </div>
        </div>
        """

        assert_contains_html(
            search_filter_html,
            html,
            "div",
            {
                "class": "govuk-grid-column-one-third govuk-grid-column-one-third--browse-all-filters"
            },
        )

    def test_search_transferring_body_display_multiple_search_terms_in_filter_tray(
        self, client, mock_standard_user, browse_consignment_files
    ):
        """
        Given a standard user accessing the search transferring body page
        When they make a GET request with multiple search terms
        Then they should see the filter tray component filled with
        individual entry of search term rendered in <div> tag
        on page content.
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        term1 = "TDR-2023-FI1"
        term2 = "first"
        term3 = "second"
        query = f"{term1},{term2},{term3}"

        form_data = {"query": query}
        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200

        html = response.data.decode()

        search_filter_html = f"""<div class="ayr-filter-tags">
                                        <div class="search-term">
                                            <button type="button"
                                            class="button-search-term"
                                            data-module="search-term-button"
                                            aria-label="Remove filter for '{term1}'"
                                        >
                                    <a href="{self.route_url}/{transferring_body_id}?query={term2},{term3}">
                                            {term1}
                                            <img src="/assets/image/cancel-filters.svg"
                                            height="30px"
                                            width="30px"
                                            class="close-icon"
                                            alt="">
                                            </a>
                                            </button>
                                        </div>
                                        <div class="search-term">
                                            <button type="button"
                                            class="button-search-term"
                                            data-module="search-term-button"
                                            aria-label="Remove filter for '{term2}'"
                                        >
                                    <a href="{self.route_url}/{transferring_body_id}?query={term1},{term3}">
                                            {term2}
                                            <img src="/assets/image/cancel-filters.svg"
                                            height="30px"
                                            width="30px"
                                            class="close-icon"
                                            alt="">
                                            </a>
                                            </button>
                                        </div>
                                        <div class="search-term">
                                            <button type="button"
                                                class="button-search-term"
                                                data-module="search-term-button"
                                                aria-label="Remove filter for '{term3}'"
                                            >
                                    <a href="{self.route_url}/{transferring_body_id}?query={term1},{term2}">
                                            {term3}
                                            <img src="/assets/image/cancel-filters.svg"
                                            height="30px"
                                            width="30px"
                                            class="close-icon"
                                            alt="">
                                            </a>
                                            </button>"""

        assert_contains_html(
            search_filter_html,
            html,
            "div",
            {"class": "ayr-filter-tags"},
        )

    @pytest.mark.parametrize(
        "query_params, expected_results",
        [
            (
                "query=TDR-2023-FI1&search_filter=th",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–', "
                        "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&search_filter=second",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'second_file.ppt', 'Open', '–'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&search_filter=docx",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=file_name-asc&search_filter=docx",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'first_file.docx', 'Closed', '25/02/2023', "
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090'"
                    ],
                ],
            ),
            (
                "query=TDR-2023-FI1&sort=file_name-desc&search_filter=th",
                [
                    [
                        "'first_series', 'TDR-2023-FI1', 'third_file.docx', 'Closed', '10/03/2090', "
                        "'first_series', 'TDR-2023-FI1', 'fourth_file.xls', 'Closed', '25/03/2070', "
                        "'first_series', 'TDR-2023-FI1', 'fifth_file.doc', 'Open', '–'"
                    ],
                ],
            ),
        ],
    )
    def test_search_transferring_body_with_search_filter_full_test(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
        query_params,
        expected_results,
    ):
        """
        Given a standard user with a search transferring body page
        When they make a request with a query and search filter (additional search terms)
        Then they should see search results based on query search and search term searched within the search
        on the page.
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}?{query_params}"
        )

        assert response.status_code == 200

        verify_search_desktop_transferring_body_header_row(response.data)
        verify_desktop_data_rows(response.data, expected_results)
