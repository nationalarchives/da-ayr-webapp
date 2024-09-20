from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from flask import url_for
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html
from app.tests.utils import (
    decompose_desktop_invisible_elements,
    evaluate_table_body_rows,
)

os_mock_return_summary = {
    "hits": {"total": {"value": 1000}, "hits": []},
    "aggregations": {
        "aggregate_by_transferring_body": {
            "buckets": [
                {
                    "doc_count": 1000,
                    "key": "foo",
                    "top_transferring_body_hits": {
                        "hits": {
                            "hits": [{"_source": {"transferring_body": "bar"}}]
                        }
                    },
                }
            ]
        }
    },
}
os_mock_return_tb = {
    "hits": {
        "total": {
            "value": 1000,
        },
        "hits": [
            {
                "_source": {
                    "series_name": "first_series",
                    "series_id": "sbar",
                    "status": "Open",
                    "closure_date": None,
                    "consignment_reference": "cbar",
                    "consignment_id": "ibar",
                    "metadata": {
                        "file_name": "fifth_file.doc",
                        "file_id": "1e2a9d26-b330-4f99-92ff-b1a5b2c1d610",
                        "closure_type": "Open",
                        "opening_date": "fooDate",
                    },
                },
            },
        ],
    }
}


class MockOpenSearch:
    def __init__(self, search_return_value=None, index_return_value=None):
        self.search_return_value = search_return_value or {"hits": {"hits": []}}
        self.index_return_value = index_return_value or {"result": "created"}

    def search(self, *args, **kwargs):
        return self.search_return_value

    def index(self, *args, **kwargs):
        return self.index_return_value


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
        soup = BeautifulSoup(html, "html.parser")
        label = soup.find("label", string="Search for digital records")
        textbox = soup.find("input", {"id": "search-input"})
        button = soup.find("button", {"id": "search-submit"})
        text = soup.find(
            "p",
            {"id": "search-description"},
        )
        text_content = text.get_text(strip=True)

        assert label is not None
        assert textbox is not None
        assert button is not None
        assert text is not None
        assert (
            text_content
            == "Search by file name, transferring body, series or consignment reference."
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

    @patch("app.main.routes.OpenSearch")
    def test_search_results_summary_with_no_results(
        self, mock_search_client, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an all_access_user with a search results summary query
        When they make a request on the search results summary page, and no results are found
        Then they should see not see any results on the page.
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value={
                "hits": {"total": {"value": 0}, "hits": []},
                "aggregations": {
                    "aggregate_by_transferring_body": {"buckets": []}
                },
            }
        )
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

    @patch("app.main.routes.OpenSearch")
    def test_search_results_summary_shows_correct_amount_of_records(
        self, mock_search_client, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an all_access_user with a search results summary query
        When they make a request on the search results summary page, and no results are found
        Then they should see not see any results on the page.
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value={
                "hits": {"total": {"value": 0}, "hits": []},
                "aggregations": {
                    "aggregate_by_transferring_body": {
                        "buckets": [
                            {
                                "doc_count": 22,
                                "key": "foo1",
                                "top_transferring_body_hits": {
                                    "hits": {
                                        "hits": [
                                            {
                                                "_source": {
                                                    "transferring_body": "bar2"
                                                }
                                            }
                                        ]
                                    }
                                },
                            },
                            {
                                "doc_count": 47,
                                "key": "foo2",
                                "top_transferring_body_hits": {
                                    "hits": {
                                        "hits": [
                                            {
                                                "_source": {
                                                    "transferring_body": "bar2"
                                                }
                                            }
                                        ]
                                    }
                                },
                            },
                        ]
                    }
                },
            }
        )
        mock_all_access_user(client)

        form_data = {"query": "a"}
        response = client.get(f"{self.route_url}", data=form_data)
        soup = BeautifulSoup(response.data, "html.parser")
        browse_details_div = soup.find("div", {"class": "browse-details"})
        heading = browse_details_div.find("h1")
        heading_text = heading.get_text(strip=True)
        assert heading and browse_details_div
        assert heading_text == "Records found 69"

    @patch("app.main.routes.OpenSearch")
    def test_search_results_summary_with_results_single_term(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_all_access_user,
    ):
        """
        Given an all_access_user
        When they make a request on the search results summary page with the single search term
        Then they should be redirected to search results summary screen
        with search results summary page content
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_summary
        )
        mock_all_access_user(client)

        form_data = {"query": "fi"}

        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        expected_results = [["bar", "1000"]]
        verify_search_results_summary_header_row(response.data)
        assert evaluate_table_body_rows(soup, expected_results=expected_results)

    @patch("app.main.routes.OpenSearch")
    def test_search_results_summary_with_results_multiple_terms(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_all_access_user,
    ):
        """
        Given an all_access_user
        When they make a request on the search results summary page with the single search term
        Then they should be redirected to search results summary screen
        with search results summary page content
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_summary
        )
        mock_all_access_user(client)

        form_data = {"query": "fi, body"}

        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        expected_results = [["bar", "1000"]]

        verify_search_results_summary_header_row(response.data)
        assert evaluate_table_body_rows(soup, expected_results=expected_results)

    @patch("app.main.routes.OpenSearch")
    def test_search_results_summary_breadcrumbs(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_all_access_user,
    ):
        """
        Given an all_access_user
        When they make a request on the search results summary page with the search term
        Then they should be redirected to search results summary screen
        and see breadcrumb values All available records > Results summary
        with search results summary page content
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_summary
        )
        mock_all_access_user(client)

        form_data = {"query": "fi"}

        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        anchor_all = soup.find("a", string="All available records", href=True)
        span_summary = soup.find("span", string="Results summary")

        assert anchor_all["href"] == self.browse_all_route_url
        assert span_summary


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

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_get(
        self,
        mock_search_client,
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
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
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

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_top_search(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user accessing the search transferring body page
        When they make a GET request
        Then they should see the top search component available on search page content.
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(f"{self.route_url}/{transferring_body_id}")

        assert response.status_code == 200

        html = response.data.decode()

        soup = BeautifulSoup(html, "html.parser")
        label = soup.find("label", string="Search for digital records")
        textbox = soup.find("input", {"id": "search-input"})
        button = soup.find("button", {"id": "search-submit"})
        text = soup.find(
            "p",
            {"id": "search-description"},
        )
        text_content = text.get_text(strip=True)

        assert label is not None
        assert textbox is not None
        assert button is not None
        assert text is not None
        assert (
            text_content
            == "Search by file name, series or consignment reference."
        )

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_no_query(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user accessing the search transferring body page
        When they make a GET request without a query
        Then they should not see any results on the page.
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value={"hits": {"total": {"value": 0}, "hits": []}}
        )

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

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_with_no_results(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user with a search transferring body page
        When they make a request and no results are found
        Then they should not see search results on the page.
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value={"hits": {"total": {"value": 0}, "hits": []}}
        )

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

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_with_table_data_links(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user with access to a body, and there are files from that body and another body
            and a search query which matches a property from related file data
        When they make a request on the search page with the search term
        Then a table is populated with the n results with metadata fields for the files from there body.
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )

        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        form_data = {"query": "first_file"}

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200
        assert b"Records found 1" in response.data

        verify_search_desktop_transferring_body_header_row(response.data)

        table = BeautifulSoup(response.data, "html.parser").find("tbody")
        decompose_desktop_invisible_elements(table)
        rows = table.find_all("tr")

        data = []

        for row in rows:
            row_data = []
            cells = row.find_all("td")
            for cell in cells:
                anchor = cell.find("a", href=True)
                if anchor:
                    row_data.append(anchor["href"])
            data.append(row_data)
        assert data == [
            [
                "/browse/series/sbar",
                "/browse/consignment/ibar",
                "/record/1e2a9d26-b330-4f99-92ff-b1a5b2c1d610",
            ]
        ]

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_results_display_multiple_pages(
        self,
        mock_search_client,
        client: FlaskClient,
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
        # a total value of 15 with a default pagination of 5 is 3 pages, 15 records found
        mock_search_client.return_value = MockOpenSearch(
            search_return_value={"hits": {"total": {"value": 15}, "hits": []}}
        )
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        form_data = {"query": "first"}

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200
        assert b"Records found 15" in response.data

        # check pagination
        assert b'aria-label="Page 1"' in response.data
        assert b'aria-label="Page 2"' in response.data
        assert b'aria-label="Page 3"' in response.data
        assert b'aria-label="Page 4"' not in response.data

        soup = BeautifulSoup(response.data, "html.parser")

        previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
        next_option = soup.find("div", {"class": "govuk-pagination__next"})

        assert not previous_option
        assert next_option.text.replace("\n", "").strip("") == "Nextpage"

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_results_display_first_page(
        self,
        mock_search_client,
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
        mock_search_client.return_value = MockOpenSearch(
            search_return_value={"hits": {"total": {"value": 15}, "hits": []}}
        )
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

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

        assert not previous_option
        assert next_option.text.replace("\n", "").strip("") == "Nextpage"

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_results_display_middle_page(
        self,
        mock_search_client,
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
        mock_search_client.return_value = MockOpenSearch(
            search_return_value={"hits": {"total": {"value": 15}, "hits": []}}
        )
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
            "span", attrs={"data-testid": "pagination-link-title"}
        )

        assert (
            " ".join(page_options[0].text.replace("\n", "").split())
            == "Previouspage"
        )
        assert (
            " ".join(page_options[1].text.replace("\n", "").split())
            == "Nextpage"
        )

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_results_display_last_page(
        self,
        mock_search_client,
        client: FlaskClient,
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
        mock_search_client.return_value = MockOpenSearch(
            search_return_value={"hits": {"total": {"value": 15}, "hits": []}}
        )
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

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

        assert (
            " ".join(previous_option.text.replace("\n", "").split())
            == "Previouspage"
        )
        assert not next_option

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_breadcrumbs_all_access_user_single_term(
        self,
        mock_search_client,
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
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
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

        soup = BeautifulSoup(response.data, "html.parser")
        anchor_records = soup.find(
            "a", string="All available records", href=True
        )
        anchor_summary = soup.find("a", string="Results summary", href=True)
        anchor_t_body = soup.find("a", string="first_body", href=True)
        span_query = soup.find("span", string=f"‘{query}’")

        assert anchor_records["href"] == self.browse_all_route_url
        assert (
            anchor_summary["href"]
            == f"{self.search_results_summary_route_url}?query={query}"
        )
        assert (
            anchor_t_body["href"]
            == f"{self.browse_transferring_body_route_url}/{transferring_body_id}"
        )
        assert span_query

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_breadcrumbs_all_access_user_multiple_terms(
        self,
        mock_search_client,
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
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
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

        soup = BeautifulSoup(response.data, "html.parser")
        anchor_records = soup.find(
            "a", string="All available records", href=True
        )
        anchor_summary = soup.find("a", string="Results summary", href=True)
        anchor_t_body = soup.find("a", string="first_body", href=True)
        span_query = soup.find("span", string=f"‘{term1}’ + ‘{term2}’")

        assert anchor_records["href"] == self.browse_all_route_url
        assert (
            anchor_summary["href"]
            == f"{self.search_results_summary_route_url}?query={query}"
        )
        assert (
            anchor_t_body["href"]
            == f"{self.browse_transferring_body_route_url}/{transferring_body_id}"
        )
        assert span_query

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_breadcrumbs_standard_user_single_search_term(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user
        When they make a request on the search transferring body page with the search term
        Then they should be redirected to search transferring body screen
        with search results summary page content
        and see a bread crumbs rendered as All available records > Results summary > Transferring body > ‘Search term’
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
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

        soup = BeautifulSoup(response.data, "html.parser")
        anchor_records = soup.find(
            "a", string="All available records", href=True
        )
        anchor_summary = soup.find("a", string="Results summary", href=True)
        anchor_t_body = soup.find("a", string="first_body", href=True)
        span_query = soup.find("span", string=f"‘{query}’")

        assert anchor_records is None
        assert anchor_summary is None
        assert (
            anchor_t_body["href"]
            == f"{self.browse_transferring_body_route_url}/{transferring_body_id}"
        )
        assert span_query

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_breadcrumbs_standard_user_multiple_search_terms(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user
        When they make a request on the search transferring body page with the search term
        Then they should be redirected to search transferring body screen
        with search results summary page content
        and see a bread crumbs rendered as All available records > Results summary > Transferring body >
        ‘Search term’ + ‘Search term’
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
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

        soup = BeautifulSoup(response.data, "html.parser")
        anchor_records = soup.find(
            "a", string="All available records", href=True
        )
        anchor_summary = soup.find("a", string="Results summary", href=True)
        anchor_t_body = soup.find("a", string="first_body", href=True)
        span_query = soup.find("span", string=f"‘{term1}’ + ‘{term2}’")

        assert anchor_records is None
        assert anchor_summary is None
        assert (
            anchor_t_body["href"]
            == f"{self.browse_transferring_body_route_url}/{transferring_body_id}"
        )
        assert span_query

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_breadcrumbs_standard_user_invalid_search_terms(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given an all_access_user
        When they make a request on the search transferring body page with the search term
        Then they should be redirected to search transferring body screen
        with search results summary page content
        and see a bread crumbs rendered as All available records > Results summary > Transferring body > ‘Search term’
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
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

        soup = BeautifulSoup(response.data, "html.parser")
        anchor_records = soup.find(
            "a", string="All available records", href=True
        )
        anchor_summary = soup.find("a", string="Results summary", href=True)
        anchor_t_body = soup.find("a", string="first_body", href=True)
        span_query = soup.find("span", string=f"‘{query}’")

        assert anchor_records is None
        assert anchor_summary is None
        assert (
            anchor_t_body["href"]
            == f"{self.browse_transferring_body_route_url}/{transferring_body_id}"
        )
        assert span_query

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_display_filter_tray_all_access_user(
        self,
        mock_search_client,
        client,
        mock_all_access_user,
        browse_consignment_files,
    ):
        """
        Given an all access user accessing the search transferring body page
        When they make a GET request
        Then they should see the filter tray component available on search page content
        and 'Clear all' link should redirect the user to 'browse all' page.
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
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

        soup = BeautifulSoup(response.data, "html.parser")

        anchor_clear = soup.find("a", string="Clear all terms", href=True)
        button_term1 = soup.find(
            "button", {"aria-label": f"Remove filter for '{term1}'"}
        )
        button_term2 = soup.find(
            "button", {"aria-label": f"Remove filter for '{term1}'"}
        )
        anchor_term1 = soup.find(
            "a",
            {"href": f"{self.route_url}/{transferring_body_id}?query={term2}"},
        )
        anchor_term2 = soup.find(
            "a",
            {"href": f"{self.route_url}/{transferring_body_id}?query={term1}"},
        )

        assert (
            anchor_clear["href"]
            == f"{self.browse_all_route_url}#browse-records"
        )
        assert button_term1 and button_term2 and anchor_term1 and anchor_term2

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_display_filter_tray_standard_user(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user accessing the search transferring body page
        When they make a GET request
        Then they should see the filter tray component available on search page content
        and 'Clear all' link should redirect the user to 'browse transferring body' page.
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
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
        soup = BeautifulSoup(response.data, "html.parser")

        anchor_clear = soup.find("a", string="Clear all terms", href=True)
        button_term1 = soup.find(
            "button", {"aria-label": f"Remove filter for '{term1}'"}
        )
        button_term2 = soup.find(
            "button", {"aria-label": f"Remove filter for '{term2}'"}
        )
        anchor_term1 = soup.find(
            "a",
            {"href": f"{self.route_url}/{transferring_body_id}?query={term2}"},
        )
        anchor_term2 = soup.find(
            "a",
            {"href": f"{self.route_url}/{transferring_body_id}?query={term1}"},
        )

        assert (
            anchor_clear["href"]
            == f"{self.browse_transferring_body_route_url}/{transferring_body_id}#browse-records"
        )
        assert button_term1 and button_term2 and anchor_term1 and anchor_term2

    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_display_multiple_search_terms_in_filter_tray(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user accessing the search transferring body page
        When they make a GET request with multiple search terms
        Then they should see the filter tray component filled with
        individual entry of search term rendered in <div> tag
        on page content.
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
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
        soup = BeautifulSoup(response.data, "html.parser")

        anchor_clear = soup.find("a", string="Clear all terms", href=True)
        button_term1 = soup.find(
            "button", {"aria-label": f"Remove filter for '{term1}'"}
        )
        button_term2 = soup.find(
            "button", {"aria-label": f"Remove filter for '{term2}'"}
        )
        button_term3 = soup.find(
            "button", {"aria-label": f"Remove filter for '{term3}'"}
        )

        anchor_term1 = soup.find(
            "a",
            {
                "href": f"{self.route_url}/{transferring_body_id}?query={term2},{term3}"
            },
        )
        anchor_term2 = soup.find(
            "a",
            {
                "href": f"{self.route_url}/{transferring_body_id}?query={term1},{term3}"
            },
        )
        anchor_term3 = soup.find(
            "a",
            {
                "href": f"{self.route_url}/{transferring_body_id}?query={term1},{term2}"
            },
        )

        assert (
            anchor_clear["href"]
            == f"{self.browse_transferring_body_route_url}/{transferring_body_id}#browse-records"
        )
        assert (
            button_term1
            and button_term2
            and button_term3
            and anchor_term1
            and anchor_term2
            and anchor_term3
        )

    @pytest.mark.parametrize(
        "query_params, mock_open_search_return, expected_results",
        [
            (
                "query=TDR-2023-FI1",
                os_mock_return_tb,
                [["first_series", "cbar", "fifth_file.doc", "Open", "fooDate"]],
            ),
        ],
    )
    @patch("app.main.routes.OpenSearch")
    def test_search_transferring_body_with_search_filter_full_test(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
        query_params,
        mock_open_search_return,
        expected_results,
    ):

        mock_search_client.return_value = MockOpenSearch(
            search_return_value=mock_open_search_return
        )

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
        soup = BeautifulSoup(response.data, "html.parser")
        assert evaluate_table_body_rows(soup, expected_results)
