from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import opensearchpy
import pytest
from bs4 import BeautifulSoup
from flask import url_for
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html
from app.tests.factories import FileFactory
from app.tests.utils import (
    decompose_desktop_invisible_elements,
    decompose_inner_tables,
    get_table_rows_cell_values,
    get_table_rows_header_values,
)

highlight_tag = "uuid_prefix_highlight_tag"
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
                    "file_name": "fifth_file.doc",
                    "file_id": "1e2a9d26-b330-4f99-92ff-b1a5b2c1d610",
                    "series_name": "first_series",
                    "series_id": "sbar",
                    "status": "Open",
                    "closure_date": None,
                    "consignment_reference": "cbar",
                    "consignment_id": "ibar",
                    "closure_type": "Open",
                    "opening_date": "fooDate",
                },
                "highlight": {
                    "series_name": [
                        f"<{highlight_tag}>test1</{highlight_tag}> and",
                        f"this is just a sentence with a mark <{highlight_tag}>element</{highlight_tag}> in it",
                    ],
                    "transferring_body": [
                        f"this is a <{highlight_tag}>cool test</{highlight_tag}> and",
                        f"sea shells <{highlight_tag}>on the</{highlight_tag}> sea shore",
                    ],
                    "test_field_1.keyword": ["should not be shown"],
                    "test_field_2.keyword": ["should not be shown also"],
                },
            },
        ],
    }
}

os_mock_return_tb_closed_record = {
    "hits": {
        "total": {
            "value": 1000,
        },
        "hits": [
            {
                "_source": {
                    "file_name": "fifth_file.doc",
                    "file_id": "1e2a9d26-b330-4f99-92ff-b1a5b2c1d610",
                    "series_name": "first_series",
                    "series_id": "sbar",
                    "status": "Closed",
                    "closure_date": "2001-01-01T00:00:00",
                    "consignment_reference": "cbar",
                    "consignment_id": "ibar",
                    "closure_type": "Closed",
                    "opening_date": "2025-01-01T00:00:00",
                },
                "highlight": {
                    "series_name": [
                        "<mark>test1</mark>",
                        "this is just a sentence with a mark <mark>element</mark> in it",
                    ],
                    "transferring_body": [
                        "t<mark>est2</mark>",
                        "sea shells <mark>on the</mark> sea shore",
                    ],
                },
            },
        ],
    }
}

expected_file_name = "fifth_file.doc"


class MockIndices:
    def __init__(self, get_mapping_return_value=None):
        self.get_mapping_return_value = get_mapping_return_value or {
            "documents": {
                "mappings": {
                    "properties": {
                        "field1": {},
                        "field2": {},
                        "field3": {},
                    }
                }
            }
        }

    def get_mapping(self, *args, **kwargs):
        return self.get_mapping_return_value


class MockOpenSearch:
    def __init__(
        self,
        search_return_value=None,
        index_return_value=None,
        get_mapping_return_value=None,
        **args,
    ):
        self.search_return_value = search_return_value or {"hits": {"hits": []}}
        self.index_return_value = index_return_value or {"result": "created"}
        self.indices = MockIndices(get_mapping_return_value)

    def search(self, *args, **kwargs):
        return self.search_return_value

    def index(self, *args, **kwargs):
        return self.index_return_value


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

    @patch("app.main.util.search_utils.OpenSearch")
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
        Alternatively, use the breadcrumbs to navigate back to the
        <a class="govuk-link govuk-link--no-visited-state" href="/browse">browse view</a>.
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

    @patch("app.main.util.search_utils.OpenSearch")
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
        heading = browse_details_div.find("h2")
        heading_text = heading.get_text(strip=True)
        assert heading and browse_details_div
        assert heading_text == "Records found 69"

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_results_summary_timeout_shows_504_bad_gateway(
        self, mock_search_client, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an all_access_user with a search results summary query
        When they make a request on the search results summary page,
            and an opensearchpy.exceptions.ConnectionTimeout occurs
        Then they should see not see any results on the page.
        """
        mock_search_client.return_value.search.side_effect = (
            opensearchpy.exceptions.ConnectionTimeout
        )
        mock_all_access_user(client)

        form_data = {"query": "junk"}
        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 504
        assert b"Bad Gateway" in response.data

    @patch("app.main.util.search_utils.OpenSearch")
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
        table_body = soup.find("tbody")
        expected_cell_values = [["bar", "1000"]]

        table_cell_values = get_table_rows_cell_values(table_body)
        assert table_cell_values == expected_cell_values

    @patch("app.main.util.search_utils.OpenSearch")
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
        table_body = soup.find("tbody")
        expected_cell_values = [["bar", "1000"]]

        table_cell_values = get_table_rows_cell_values(table_body)
        assert table_cell_values == expected_cell_values

    @patch("app.main.util.search_utils.OpenSearch")
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

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_results_summary_no_perms_standard_users(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
    ):
        """
        Given a standard user
        When they make a request to the search summary page
        Then they should receive a 403 code
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_summary
        )
        mock_standard_user(client)

        form_data = {"query": "fi"}

        response = client.get(f"{self.route_url}", data=form_data)

        assert response.status_code == 403


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

    @patch("app.main.util.search_utils.OpenSearch")
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

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_top_search(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user accessing a page that has the top search component
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
        label = soup.find("legend", {"class": "top-search__els__heading"})
        label_text = label.get_text(strip=True)
        textbox = soup.find("input", {"id": "search-input"})
        button = soup.find("button", {"id": "search-submit"})

        radio_1 = soup.find("input", {"id": "everywhere"})
        radio_2 = soup.find("input", {"id": "metadata"})
        radio_3 = soup.find("input", {"id": "record"})

        assert label is not None and label_text == "Search for digital records"
        assert textbox is not None
        assert button is not None
        assert radio_1 and radio_2 and radio_3
        # radio for search area "everywhere" should be checked by default
        assert "checked" in radio_1.attrs

    @pytest.mark.parametrize(
        "radio_arg, expected_checked_radio",
        [
            ("everywhere", "everywhere"),
            ("metadata", "metadata"),
            ("record", "record"),
        ],
    )
    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_top_search_radio_previously_selected(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
        radio_arg,
        expected_checked_radio,
    ):
        """
        Given a standard user accessing a page that has the top search component
        When they make a GET request
        Then they should see the checked radio associated with the arg in the URL.
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

        response = client.get(
            f"{self.route_url}/{transferring_body_id}?search_area={radio_arg}"
        )

        assert response.status_code == 200
        html = response.data.decode()
        soup = BeautifulSoup(html, "html.parser")

        radio = soup.find("input", {"id": expected_checked_radio})
        assert radio
        assert "checked" in radio.attrs

    @patch("app.main.util.search_utils.OpenSearch")
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

    @patch("app.main.util.search_utils.OpenSearch")
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
        Alternatively, use the breadcrumbs to navigate back to the
        <a class="govuk-link govuk-link--no-visited-state" href="/browse">browse view</a>.
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

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_results_timeout_error(
        self, mock_search_client, client: FlaskClient, mock_standard_user
    ):
        """
        Given a user with access to a transferring body
        When they make a request on the search results summary page
            and an opensearchpy.exceptions.ConnectionTimeout occurs
        Then they should receive a 504 Gateway Timeout response
        """
        file = FileFactory()

        mock_standard_user(client, file.consignment.series.body.Name)

        transferring_body_id = file.consignment.series.body.BodyId

        mock_search_client.return_value.search.side_effect = (
            opensearchpy.exceptions.ConnectionTimeout
        )

        form_data = {"query": "bar"}

        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 504
        assert b"Bad Gateway" in response.data

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_result_has_accordion(
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
        Then the result contains a button with aria-expanded set to false by default
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

        soup = BeautifulSoup(response.data, "html.parser")
        button = soup.find("button", attrs={"aria-expanded": False})

        assert button is not None

    @patch("app.main.util.search_utils.OpenSearch")
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

    @patch("app.main.util.search_utils.OpenSearch")
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

    @patch("app.main.util.search_utils.OpenSearch")
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

    @patch("app.main.util.search_utils.OpenSearch")
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

    @patch("app.main.util.search_utils.OpenSearch")
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

    @patch("app.main.util.search_utils.OpenSearch")
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
        query = f"{term1}+{term2}"
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

    @patch("app.main.util.search_utils.OpenSearch")
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

    @patch("app.main.util.search_utils.OpenSearch")
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
        query = f"{term1}+{term2}"
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

        assert anchor_records is None
        assert anchor_summary is None
        assert (
            anchor_t_body["href"]
            == f"{self.browse_transferring_body_route_url}/{transferring_body_id}"
        )
        assert span_query

    @patch("app.main.util.search_utils.OpenSearch")
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

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_breadcrumbs_empty_search_term(
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
        form_data = {"query": ""}

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
        span_query = soup.find("span", string="‘’")

        assert anchor_records is None
        assert anchor_summary is None
        assert (
            anchor_t_body["href"]
            == f"{self.browse_transferring_body_route_url}/{transferring_body_id}"
        )
        assert span_query

    @patch("app.main.util.search_utils.OpenSearch")
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
        query = f"{term1}+{term2}"

        form_data = {"query": query}
        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200

        soup = BeautifulSoup(response.data, "html.parser")

        anchor_clear = soup.find("a", string="Clear all terms", href=True)
        button_term1 = soup.find(
            "a", {"aria-label": f"Remove filter for '{term1}'"}
        )
        button_term2 = soup.find(
            "a", {"aria-label": f"Remove filter for '{term2}'"}
        )

        # Verify that the remove links exist and have the correct query parameter
        # Get the hrefs from the button elements
        href_term1 = button_term1["href"] if button_term1 else None
        href_term2 = button_term2["href"] if button_term2 else None

        # Parse and check the query parameters
        if href_term1:
            parsed = urlparse(href_term1)
            query_params = parse_qs(parsed.query)
            expected_query = term2
            assert (
                "query" in query_params
                and query_params["query"][0] == expected_query
            ), f"Expected query={expected_query}, got query={query_params.get('query', [''])[0]}"

        if href_term2:
            parsed = urlparse(href_term2)
            query_params = parse_qs(parsed.query)
            expected_query = term1
            assert (
                "query" in query_params
                and query_params["query"][0] == expected_query
            ), f"Expected query={expected_query}, got query={query_params.get('query', [''])[0]}"

        assert (
            anchor_clear["href"]
            == f"{self.browse_all_route_url}#browse-records"
        )
        assert button_term1 and button_term2

    @patch("app.main.util.search_utils.OpenSearch")
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
        query = f"{term1}+{term2}"

        form_data = {"query": query}
        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        anchor_clear = soup.find("a", string="Clear all terms", href=True)
        button_term1 = soup.find(
            "a", {"aria-label": f"Remove filter for '{term1}'"}
        )
        button_term2 = soup.find(
            "a", {"aria-label": f"Remove filter for '{term2}'"}
        )

        # Verify that the remove links exist and have the correct query parameter
        # Get the hrefs from the button elements
        href_term1 = button_term1["href"] if button_term1 else None
        href_term2 = button_term2["href"] if button_term2 else None

        # Parse and check the query parameters
        if href_term1:
            parsed = urlparse(href_term1)
            query_params = parse_qs(parsed.query)
            expected_query = term2
            assert (
                "query" in query_params
                and query_params["query"][0] == expected_query
            ), f"Expected query={expected_query}, got query={query_params.get('query', [''])[0]}"

        if href_term2:
            parsed = urlparse(href_term2)
            query_params = parse_qs(parsed.query)
            expected_query = term1
            assert (
                "query" in query_params
                and query_params["query"][0] == expected_query
            ), f"Expected query={expected_query}, got query={query_params.get('query', [''])[0]}"

        assert (
            anchor_clear["href"]
            == f"{self.browse_transferring_body_route_url}/{transferring_body_id}#browse-records"
        )
        assert button_term1 and button_term2

    @patch("app.main.util.search_utils.OpenSearch")
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
        query = f"{term1}+{term2}+{term3}"

        form_data = {"query": query}
        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        anchor_clear = soup.find("a", string="Clear all terms", href=True)
        button_term1 = soup.find(
            "a", {"aria-label": f"Remove filter for '{term1}'"}
        )
        button_term2 = soup.find(
            "a", {"aria-label": f"Remove filter for '{term2}'"}
        )
        button_term3 = soup.find(
            "a", {"aria-label": f"Remove filter for '{term3}'"}
        )

        # Verify that the remove links exist and have the correct query parameter
        # Get the hrefs from the button elements
        href_term1 = button_term1["href"] if button_term1 else None
        href_term2 = button_term2["href"] if button_term2 else None
        href_term3 = button_term3["href"] if button_term3 else None

        # Parse and check the query parameters
        if href_term1:
            parsed = urlparse(href_term1)
            query_params = parse_qs(parsed.query)
            expected_query = f"{term2}+{term3}"
            assert (
                "query" in query_params
                and query_params["query"][0] == expected_query
            ), f"Expected query={expected_query}, got query={query_params.get('query', [''])[0]}"

        if href_term2:
            parsed = urlparse(href_term2)
            query_params = parse_qs(parsed.query)
            expected_query = f"{term1}+{term3}"
            assert (
                "query" in query_params
                and query_params["query"][0] == expected_query
            ), f"Expected query={expected_query}, got query={query_params.get('query', [''])[0]}"

        if href_term3:
            parsed = urlparse(href_term3)
            query_params = parse_qs(parsed.query)
            expected_query = f"{term1}+{term2}"
            assert (
                "query" in query_params
                and query_params["query"][0] == expected_query
            ), f"Expected query={expected_query}, got query={query_params.get('query', [''])[0]}"

        assert (
            anchor_clear["href"]
            == f"{self.browse_transferring_body_route_url}/{transferring_body_id}#browse-records"
        )
        assert button_term1 and button_term2 and button_term3

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_verify_table_headers(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user
        When they make a request on the search page with the search term
        Then the tables have correct headers
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
        soup = BeautifulSoup(response.data, "html.parser")
        decompose_desktop_invisible_elements(soup)

        inner_table = soup.find("table", {"id": "inner-table"})
        inner_table_headers = get_table_rows_header_values(inner_table)
        expected_headers_inner_table = (
            [
                "Series",
                "Consignment ref",
                "Status",
                "Record opening date",
            ],
        )

        decompose_inner_tables(soup)

        main_table = soup.find("table")
        main_table_headers = get_table_rows_header_values(main_table)
        expected_headers_main_table = (
            [
                "Found within",
                "Search results",
            ],
        )

        assert inner_table_headers == expected_headers_inner_table[0]
        assert main_table_headers == expected_headers_main_table[0]

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_with_table_data_links_inner_table(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user
        When they make a request on the search page with the search term
        Then an inner table is populated inside the accordion with metadata of which some are anchors
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

        table = BeautifulSoup(response.data, "html.parser").find(
            "table", {"id": "inner-table"}
        )
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
            if len(row_data) > 1:
                data.append(row_data)

        assert data == [
            [
                "/browse/series/sbar",
                "/browse/consignment/ibar",
            ]
        ]

    @pytest.mark.parametrize(
        "query_params, mock_open_search_return, expected_cell_values, expected_sort_select_value",
        [
            (
                "&query=foobar",
                os_mock_return_tb,
                [["first_series", "cbar", "Open", "fooDate"]],
                "file_name",
            ),
            (
                "sort=file_name&query=foobar",
                os_mock_return_tb,
                [["first_series", "cbar", "Open", "fooDate"]],
                "file_name",
            ),
            (
                "sort=description&query=foobar",
                os_mock_return_tb,
                [["first_series", "cbar", "Open", "fooDate"]],
                "description",
            ),
            (
                "sort=metadata&query=foobar",
                os_mock_return_tb,
                [["first_series", "cbar", "Open", "fooDate"]],
                "metadata",
            ),
            (
                "sort=content&query=foobar",
                os_mock_return_tb,
                [["first_series", "cbar", "Open", "fooDate"]],
                "content",
            ),
            (
                "sort=most_matches&query=foobar",
                os_mock_return_tb,
                [["first_series", "cbar", "Open", "fooDate"]],
                "most_matches",
            ),
            (
                "sort=least_matches&query=foobar",
                os_mock_return_tb,
                [["first_series", "cbar", "Open", "fooDate"]],
                "least_matches",
            ),
        ],
    )
    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_with_search_term_happy_path_inner_table(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
        query_params,
        mock_open_search_return,
        expected_cell_values,
        expected_sort_select_value,
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
        select = soup.find("select", {"id": "sort"})
        option = select.find("option", selected=True)
        option_value = option.get("value")

        decompose_desktop_invisible_elements(soup)
        inner_table = soup.find("table", {"id": "inner-table"})
        inner_table_body = inner_table.find("tbody")
        inner_table_cell_values = get_table_rows_cell_values(inner_table_body)

        assert select
        assert option_value == expected_sort_select_value
        assert inner_table_cell_values == expected_cell_values

        # check all accordions are closed by default (no "open" attr)
        details_elements = soup.find_all("details")
        assert all("open" not in details.attrs for details in details_elements)

    @pytest.mark.parametrize(
        "query_params, mock_open_search_return, expected_cell_values, expected_sort_select_value",
        [
            # without any sort term the select value should be file_name by default
            (
                "query=foobar",
                os_mock_return_tb,
                [["first_series", "cbar", "Open", "fooDate"]],
                "file_name",
            ),
            # edge case: random sort options as letters
            (
                "sort=foo-bar&query=foobar",
                os_mock_return_tb,
                [["first_series", "cbar", "Open", "fooDate"]],
                "file_name",
            ),
            # edge case: random sort options as numbers
            (
                "sort=111-222&query=foobar",
                os_mock_return_tb,
                [["first_series", "cbar", "Open", "fooDate"]],
                "file_name",
            ),
            # edge case: random sort order
            (
                "sort=series_name-aaaaa&query=foobar",
                os_mock_return_tb,
                [["first_series", "cbar", "Open", "fooDate"]],
                "file_name",
            ),
        ],
    )
    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_with_search_term_edge_case_path_inner_table(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
        query_params,
        mock_open_search_return,
        expected_cell_values,
        expected_sort_select_value,
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

        select = soup.find("select", {"id": "sort"})

        option_first = select.find("option")
        option_first_value = option_first.get("value")

        decompose_desktop_invisible_elements(soup)
        inner_table = soup.find("table", {"id": "inner-table"})
        inner_table_body = inner_table.find("tbody")
        inner_table_cell_values = get_table_rows_cell_values(inner_table_body)

        assert select
        assert option_first_value == expected_sort_select_value
        assert inner_table_cell_values == expected_cell_values

    @pytest.mark.parametrize(
        "query_params, mock_open_search_return, expected_cell_values",
        [
            (
                "&query=foobar",
                os_mock_return_tb,
                [
                    [
                        "Series name +1",
                        "<mark>test1</mark> and ... this is just a sentence with a mark <mark>element</mark> in it",
                    ],
                    [
                        "File name",
                        "fifth_file.doc",
                    ],
                    [
                        "Transferring body",
                        "this is a <mark>cool test</mark> and ... sea shells <mark>on the</mark> sea shore",
                    ],
                ],
            ),
            (
                "&query=foobar&open_all=open_all",
                os_mock_return_tb,
                [
                    [
                        "Series name +1",
                        "<mark>test1</mark> and ... this is just a sentence with a mark <mark>element</mark> in it",
                    ],
                    [
                        "File name",
                        "fifth_file.doc",
                    ],
                    [
                        "Transferring body",
                        "this is a <mark>cool test</mark> and ... sea shells <mark>on the</mark> sea shore",
                    ],
                ],
            ),
            (
                "&query=!!!!!",
                os_mock_return_tb,
                [
                    [
                        "Series name +1",
                        "<mark>test1</mark> and ... this is just a sentence with a mark <mark>element</mark> in it",
                    ],
                    [
                        "File name",
                        "fifth_file.doc",
                    ],
                    [
                        "Transferring body",
                        "this is a <mark>cool test</mark> and ... sea shells <mark>on the</mark> sea shore",
                    ],
                ],
            ),
        ],
    )
    @patch("app.main.routes.uuid.uuid4")
    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_with_search_term_main_table(
        self,
        mock_search_client,
        mock_uuid4,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
        query_params,
        mock_open_search_return,
        expected_cell_values,
    ):
        """
        Given a user attempting to search for a specific term
        When the user searches for a term that returns multiple hits
        Then the table should be populated by <mark> tags that contains the found terms
        """

        mock_search_client.return_value = MockOpenSearch(
            search_return_value=mock_open_search_return
        )
        mock_uuid4.return_value.hex = "highlight_tag"

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

        # decomposing inner tables so we can get just the values of the main tables
        decompose_inner_tables(soup)
        decompose_desktop_invisible_elements(soup)

        table_body = soup.find("tbody")
        table_cell_values = get_table_rows_cell_values(table_body)

        mark_elements = soup.find_all("mark")
        mark_text_values = [mark.get_text(strip=True) for mark in mark_elements]

        assert mark_text_values == ["test1", "element", "cool test", "on the"]
        assert table_cell_values == expected_cell_values

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_standard_user_with_no_view_perms(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user with a specific transferring body role
        When they make a GET request to search a transferring body they dont have permissions to view
        Then they should receive a 404 code
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
        mock_standard_user(client, "non_existant_body")

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        form_data = {"query": "test"}
        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 404

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_standard_user_with_view_perms(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user with a specific transferring body role
        When they make a GET request to search a transferring body they have permissions to view
        Then they should receive a 200 code
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
        mock_standard_user(client, "first_body")

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        form_data = {"query": "test"}
        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert response.status_code == 200

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_returns_correct_date_format(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user accessing the search transferring body page
        When they make a GET request with any amount of search terms
        Then they should see search transferring body page with dates
        displayed in a DD/MM/YYYY format
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb_closed_record
        )
        mock_standard_user(client, "first_body")

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        form_data = {"query": "test", "sort": "closure_type-asc"}
        response = client.get(
            f"{self.route_url}/{transferring_body_id}", data=form_data
        )

        assert "01/01/2025" in response.text

        assert response.status_code == 200

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_all_accordions_open_with_open_all_query(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user
        When they make a GET request to the search page with the open_all param
        All details elements should have an open attribute (which would mean all accordions are open)
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
        mock_standard_user(client, "first_body")

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        form_data = {"query": "test"}
        response = client.get(
            f"{self.route_url}/{transferring_body_id}?open_all=open_all",
            data=form_data,
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        checkbox = soup.find("input", {"name": "open_all"})
        details_elements = soup.find_all("details")

        # we cant check CSS visibility with Beautiful soup, otherwise
        # we'd check if the field count element is not visible here
        assert "checked" in checkbox.attrs
        assert all("open" in details.attrs for details in details_elements)

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_file_name_in_source_shown_if_not_in_highlight(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user
        When they make a GET request to the search page with a query
        If the file_name is not found inside highlight
        Then it should be shown as the value inside _source AND be a link AND be the 2nd row
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
        mock_standard_user(client, "first_body")

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}",
            data={"query": "test"},
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        anchors = soup.find_all("a")
        anchors_text = []
        for anchor in anchors:
            anchors_text.append(anchor.get_text(strip=True))
        assert expected_file_name in anchors_text

        table_body = soup.find("tbody")
        table_rows_cell_values = get_table_rows_cell_values(table_body)
        assert table_rows_cell_values[1] == ["File name", expected_file_name]

    @patch("app.main.routes.uuid.uuid4")
    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_highlight_file_name_prioritized_over_source(
        self,
        mock_search_client,
        mock_uuid4,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user
        When they make a GET request to the search page with a query
        If highlight has a file_name field
        Then it should be shown in place of the file_name inside _source AND be an achor AND is the 2nd row
        """
        mock_uuid4.return_value.hex = "highlight_tag"
        mock_search_client.return_value = MockOpenSearch(
            search_return_value={
                "hits": {
                    "total": {
                        "value": 1000,
                    },
                    "hits": [
                        {
                            "_source": {
                                "file_name": "fifth_file.doc",
                            },
                            "highlight": {
                                "series_name": ["bar"],
                                "transferring_body": ["polo"],
                                "file_name": [
                                    f"<{highlight_tag}>fifth_file.doc</{highlight_tag}>"
                                ],
                            },
                        },
                    ],
                }
            }
        )
        mock_standard_user(client, "first_body")

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}",
            data={"query": "test"},
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        anchors = soup.find_all("a")
        anchors_text = []
        for anchor in anchors:
            anchors_text.append(anchor.get_text(strip=True))
        assert "fifth_file.doc" in anchors_text

        table_body = soup.find("tbody")
        table_rows_cell_values = get_table_rows_cell_values(table_body)
        assert table_rows_cell_values[0] == [
            "File name +2",
            "<mark>fifth_file.doc</mark>",
        ]
        assert ["File name", expected_file_name] not in table_rows_cell_values

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_keyword_fields_should_not_be_shown(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user
        When they make a GET request to the search page with a query
        If keyword fields that get returned from OS highlight exist
        Then they should not be shown in the table
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
        mock_standard_user(client, "first_body")

        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"{self.route_url}/{transferring_body_id}",
            data={"query": "test"},
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        table_body = soup.find("tbody")
        table_rows_cell_values = get_table_rows_cell_values(table_body)
        assert [
            "Test field 1.keyword",
            "should not be shown",
        ] not in table_rows_cell_values
        assert [
            "Test field 2.keyword",
            "should not be shown also",
        ] not in table_rows_cell_values

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_with_quotes(
        self,
        mock_search_client,
        client: FlaskClient,
        mock_all_access_user,
        browse_consignment_files,
    ):
        """
        Given a standard user accessing the search transferring body page
        When they make a GET request with a search term including quotes
        Then they should only see results that include that term.
        """
        mock_search_client.return_value = MockOpenSearch(
            search_return_value=os_mock_return_tb
        )
        mock_all_access_user(client)

        term1 = '"fi"'
        query = term1
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
        span_query = soup.find("span", string="‘fi’")

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

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_no_highlights_renders_file_name_and_search_results(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user accessing the search transferring body page
        When a record has no highlights
        Then the table should render only the file name and link in both columns
        And all accordions should be open if open_all param is present
        """
        file_name = "plain_file.txt"
        file_id = "abc123"
        mock_search_client.return_value = MockOpenSearch(
            search_return_value={
                "hits": {
                    "total": {"value": 1},
                    "hits": [
                        {
                            "_source": {
                                "file_name": file_name,
                                "file_id": file_id,
                                "series_name": "series_x",
                                "series_id": "sid",
                                "status": "Open",
                                "closure_date": None,
                                "consignment_reference": "cref",
                                "consignment_id": "cid",
                                "closure_type": "Open",
                                "opening_date": "2025-01-01",
                            },
                            # No highlight key at all
                        }
                    ],
                }
            }
        )
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"/search/transferring_body/{transferring_body_id}?query=plain&open_all=open_all"
        )
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        table_body = soup.find("tbody")
        table_rows_cell_values = get_table_rows_cell_values(table_body)
        assert ["File name", file_name] in table_rows_cell_values
        assert ["series_name", "series_x"] not in table_rows_cell_values
        assert ["consignment_reference", "cref"] not in table_rows_cell_values

        # Check all accordions are open
        details_elements = soup.find_all("details")
        assert all("open" in details.attrs for details in details_elements)

    @patch("app.main.util.search_utils.OpenSearch")
    def test_search_transferring_body_empty_highlights_renders_file_name_and_search_results(
        self,
        mock_search_client,
        client,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user accessing the search transferring body page
        When a record has an empty highlights dict
        Then the table should render only the file name and link in both columns
        And all accordions should be open if open_all param is present
        """
        file_name = "plain_file2.txt"
        file_id = "def456"
        mock_search_client.return_value = MockOpenSearch(
            search_return_value={
                "hits": {
                    "total": {"value": 1},
                    "hits": [
                        {
                            "_source": {
                                "file_name": file_name,
                                "file_id": file_id,
                                "series_name": "series_y",
                                "series_id": "sid2",
                                "status": "Open",
                                "closure_date": None,
                                "consignment_reference": "cref2",
                                "consignment_id": "cid2",
                                "closure_type": "Open",
                                "opening_date": "2025-01-02",
                            },
                            "highlight": {},
                        }
                    ],
                }
            }
        )
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )
        transferring_body_id = browse_consignment_files[
            0
        ].consignment.series.body.BodyId

        response = client.get(
            f"/search/transferring_body/{transferring_body_id}?query=plain&open_all=open_all"
        )
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        table_body = soup.find("tbody")
        table_rows_cell_values = get_table_rows_cell_values(table_body)
        assert ["File name", file_name] in table_rows_cell_values
        assert ["series_name", "series_y"] not in table_rows_cell_values
        assert ["consignment_reference", "cref2"] not in table_rows_cell_values

        # Check all accordions are open
        details_elements = soup.find_all("details")
        assert all("open" in details.attrs for details in details_elements)
