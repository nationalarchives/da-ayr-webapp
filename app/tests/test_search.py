import uuid
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import opensearchpy
from bs4 import BeautifulSoup
from flask import url_for
from flask.testing import FlaskClient
from werkzeug.exceptions import NotFound

from app.tests.utils import (
    decompose_desktop_invisible_elements,
    decompose_inner_tables,
    get_table_rows_header_values,
)

OS_MOCK_RESULTS = {
    "hits": {
        "total": {"value": 1000},
        "hits": [
            {
                "_source": {
                    "file_name": "fifth_file.doc",
                    "file_id": "1e2a9d26-b330-4f99-92ff-b1a5b2c1d610",
                    "series_name": "first_series",
                    "series_id": "sbar",
                    "status": "Open",
                    "consignment_reference": "cbar",
                    "consignment_id": "ibar",
                    "closure_type": "Open",
                    "opening_date": "2025-01-01T00:00:00",
                    "date_last_modified": "2025-01-01T00:00:00",
                },
                "highlight": {
                    "content": ["alpha beta gamma"],
                    "test_field_1.keyword": ["should not be shown"],
                },
            }
        ],
    }
}


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
        search_side_effect=None,
        index_return_value=None,
        get_mapping_return_value=None,
        **args,
    ):
        self.search_return_value = search_return_value or {"hits": {"hits": []}}
        self.search_side_effect = search_side_effect
        self.index_return_value = index_return_value or {"result": "created"}
        self.indices = MockIndices(get_mapping_return_value)

    def search(self, *args, **kwargs):
        if self.search_side_effect:
            raise self.search_side_effect
        return self.search_return_value

    def index(self, *args, **kwargs):
        return self.index_return_value


class TestSearchRedirect:
    @property
    def route_url(self):
        return "/search"

    def test_search_redirects_all_access_user_to_search_results(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an all-access user accessing /search
        When they submit a query
        Then they are redirected to canonical /search/results
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}", data={"query": "fi"})

        assert response.status_code == 302
        assert response.headers["Location"] == url_for(
            "main.search_results", query="fi"
        )

    def test_search_redirects_standard_user_to_search_results(
        self, client: FlaskClient, mock_standard_user, browse_consignment_files
    ):
        """
        Given a standard user accessing /search
        When they submit a query
        Then they are redirected to canonical /search/results
        """
        mock_standard_user(
            client, browse_consignment_files[0].consignment.series.body.Name
        )

        response = client.get(f"{self.route_url}", data={"query": "fi"})

        assert response.status_code == 302
        assert response.headers["Location"] == url_for(
            "main.search_results", query="fi"
        )

    def test_search_redirect_preserves_search_query_parameters(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given a /search request with explicit search parameters
        When the route redirects to /search/results
        Then the query parameters are preserved
        """
        mock_all_access_user(client)

        response = client.get(
            self.route_url,
            query_string={
                "query": "test",
                "search_area": "metadata",
                "sort": "least_matches",
                "search_filter": "extra term",
            },
        )

        assert response.status_code == 302
        parsed_url = urlparse(response.headers["Location"])
        params = parse_qs(parsed_url.query)

        assert parsed_url.path == "/search/results"
        assert params["query"] == ["test"]
        assert params["search_area"] == ["metadata"]
        assert params["sort"] == ["least_matches"]
        assert params["search_filter"] == ["extra term"]


class TestSearchResults:
    @property
    def route_url(self):
        return "/search/results"

    @patch("app.main.routes.setup_opensearch")
    def test_search_results_renders_top_search_with_default_everywhere_selected(
        self, mock_setup_opensearch, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an authenticated user on /search/results
        When the page is rendered
        Then the top-search component is visible and "everywhere" is selected by default
        """
        mock_all_access_user(client)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )

        response = client.get(f"{self.route_url}?query=test")

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        heading = soup.find("legend", {"class": "top-search__els__heading"})
        search_input = soup.find("input", {"id": "search-input"})
        search_submit = soup.find("button", {"id": "search-submit"})

        everywhere = soup.find("input", {"id": "everywhere"})
        metadata = soup.find("input", {"id": "metadata"})
        record = soup.find("input", {"id": "record"})

        assert heading is not None
        assert heading.get_text(strip=True) == "Search for digital records"
        assert search_input is not None
        assert search_submit is not None
        assert everywhere is not None
        assert metadata is not None
        assert record is not None
        assert "checked" in everywhere.attrs

    @patch("app.main.routes.setup_opensearch")
    def test_search_results_top_search_radio_reflects_selected_search_area(
        self, mock_setup_opensearch, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an authenticated user on /search/results
        When search_area is provided in the query string
        Then the matching top-search radio remains selected
        """
        mock_all_access_user(client)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )

        for area in ["everywhere", "metadata", "record"]:
            response = client.get(
                f"{self.route_url}?query=test&search_area={area}"
            )

            assert response.status_code == 200
            soup = BeautifulSoup(response.data, "html.parser")
            selected_radio = soup.find("input", {"id": area})

            assert selected_radio is not None
            assert "checked" in selected_radio.attrs

    @patch("app.main.routes.setup_opensearch")
    def test_search_results_renders_empty_state_without_query(
        self, mock_setup_opensearch, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an authenticated user on /search/results
        When no query is provided
        Then the empty state is rendered without calling OpenSearch
        """
        mock_all_access_user(client)

        response = client.get(self.route_url)

        assert response.status_code == 200
        assert b"No results found" in response.data
        assert b"Help with your search" in response.data
        mock_setup_opensearch.assert_not_called()

    @patch("app.main.routes.setup_opensearch")
    def test_search_results_renders_expected_table_headers_for_query(
        self, mock_setup_opensearch, client: FlaskClient, mock_all_access_user
    ):
        """
        Given a query that returns results
        When /search/results is requested
        Then the results table headers are rendered as expected
        """
        mock_all_access_user(client)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )

        response = client.get(f"{self.route_url}?query=test")

        assert response.status_code == 200
        assert b"fifth_file.doc" in response.data

        soup = BeautifulSoup(response.data, "html.parser")
        decompose_desktop_invisible_elements(soup)
        decompose_inner_tables(soup)
        table = soup.find("table", attrs={"id": "tbl_result"})

        assert table is not None
        headers = get_table_rows_header_values(table)
        assert headers[0].startswith("Showing 1")
        assert headers[0].endswith("of 1,000")
        assert headers[1:] == ["Series", "Status", "Opening date"]

    @patch("app.main.routes.setup_opensearch")
    def test_search_results_with_query_and_no_hits_renders_no_results(
        self, mock_setup_opensearch, client: FlaskClient, mock_all_access_user
    ):
        """
        Given a valid query with zero hits
        When /search/results is requested
        Then no-results helper content is shown and no table is rendered
        """
        mock_all_access_user(client)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value={"hits": {"total": {"value": 0}, "hits": []}}
        )

        response = client.get(f"{self.route_url}?query=test")

        assert response.status_code == 200
        assert b"No results found" in response.data
        assert b"Help with your search" in response.data

        soup = BeautifulSoup(response.data, "html.parser")
        assert soup.find("table", attrs={"id": "tbl_result"}) is None

    @patch("app.main.routes.setup_opensearch")
    def test_search_results_record_links_include_return_to_for_current_results(
        self, mock_setup_opensearch, client: FlaskClient, mock_all_access_user
    ):
        """
        Given a user on a populated search results page
        When record links are rendered
        Then each link preserves a return_to URL for the current search page state
        """
        mock_all_access_user(client)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )

        response = client.get(
            f"{self.route_url}?query=test&search_area=metadata&sort=least_matches&page=2"
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        record_link = soup.select_one("a.browse-records__file-link")

        assert record_link is not None

        parsed_record_href = urlparse(record_link["href"])
        record_params = parse_qs(parsed_record_href.query)

        assert "return_to" in record_params

        parsed_return_to = urlparse(record_params["return_to"][0])
        return_to_params = parse_qs(parsed_return_to.query)

        assert parsed_return_to.path == self.route_url
        assert return_to_params["query"] == ["test"]
        assert return_to_params["search_area"] == ["metadata"]
        assert return_to_params["sort"] == ["least_matches"]
        assert return_to_params["page"] == ["2"]
        assert parsed_return_to.fragment == "browse-records"

    def test_search_results_back_link_targets_browse_for_all_access_user(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an all-access user on search results
        When the page is rendered
        Then the Back link targets browse records anchor
        """
        mock_all_access_user(client)

        response = client.get(self.route_url)

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        back_link = soup.select_one("a.govuk-back-link")

        assert back_link is not None
        assert back_link["href"] == "/browse#browse-records"

    def test_search_results_back_link_targets_body_browse_for_standard_user(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user on search results
        When the page is rendered
        Then the Back link targets that user's transferring body browse anchor
        """
        body = browse_consignment_files[0].consignment.series.body
        mock_standard_user(client, body.Name)

        response = client.get(self.route_url)

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        back_link = soup.select_one("a.govuk-back-link")

        assert back_link is not None
        assert (
            back_link["href"]
            == f"/browse/transferring_body/{body.BodyId}#browse-records"
        )

    def test_search_results_back_link_uses_same_origin_referrer(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given a same-origin previous page
        When search results are rendered
        Then the Back link targets that previous page
        """
        mock_all_access_user(client)

        referrer = "http://localhost/browse/records?series_filter=HO+405#browse-records"
        response = client.get(self.route_url, headers={"Referer": referrer})

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        back_link = soup.select_one("a.govuk-back-link")

        assert back_link is not None
        assert back_link["href"] == referrer

    def test_search_results_back_link_ignores_external_referrer(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an external previous page referrer
        When search results are rendered
        Then the Back link falls back to the safe internal route
        """
        mock_all_access_user(client)

        response = client.get(
            self.route_url,
            headers={"Referer": "https://example.com/untrusted"},
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        back_link = soup.select_one("a.govuk-back-link")

        assert back_link is not None
        assert back_link["href"] == "/browse#browse-records"

    @patch("app.main.routes.setup_opensearch")
    def test_search_results_clear_all_terms_targets_browse_for_all_access_user(
        self, mock_setup_opensearch, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an all-access user on search results
        When Clear all terms is rendered
        Then it links to /browse#browse-records
        """
        mock_all_access_user(client)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )

        response = client.get(f"{self.route_url}?query=test")

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        clear_all_link = soup.find("a", string="Clear all terms", href=True)

        assert clear_all_link is not None
        assert clear_all_link["href"] == "/browse#browse-records"

    @patch("app.main.routes.setup_opensearch")
    def test_search_results_clear_all_terms_targets_body_browse_for_standard_user(
        self,
        mock_setup_opensearch,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user on search results
        When Clear all terms is rendered
        Then it links to that user's transferring body browse anchor
        """
        body = browse_consignment_files[0].consignment.series.body
        mock_standard_user(client, body.Name)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )

        response = client.get(f"{self.route_url}?query=test")

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        clear_all_link = soup.find("a", string="Clear all terms", href=True)

        assert clear_all_link is not None
        assert (
            clear_all_link["href"]
            == f"/browse/transferring_body/{body.BodyId}#browse-records"
        )

    @patch("app.main.routes.execute_search")
    @patch("app.main.routes.setup_opensearch")
    def test_search_results_applies_body_filter_for_standard_user(
        self,
        mock_setup_opensearch,
        mock_execute_search,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user searching records
        When the OpenSearch query is built
        Then the query includes the user's transferring body filter
        """
        body = browse_consignment_files[0].consignment.series.body
        mock_standard_user(client, body.Name)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )
        mock_execute_search.return_value = OS_MOCK_RESULTS

        response = client.get(f"{self.route_url}/{body.BodyId}?query=test")

        assert response.status_code == 200
        _, dsl_query, _, _ = mock_execute_search.call_args[0]
        assert dsl_query["query"]["bool"]["filter"] == [
            {
                "term": {
                    "transferring_body_id.keyword": str(body.BodyId),
                }
            }
        ]

    def test_search_results_redirects_when_search_filter_is_added(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given a base query and an additional search_filter term
        When search results are requested
        Then the request redirects with the merged query and no search_filter
        """
        mock_all_access_user(client)

        response = client.get(
            f"{self.route_url}?query=test&search_filter=extra term"
        )

        assert response.status_code == 302
        redirect_location = response.headers["Location"]
        parsed_url = urlparse(redirect_location)
        params = parse_qs(parsed_url.query)

        assert parsed_url.path == self.route_url
        assert params["query"] == ['test+"extra term"']
        assert "search_filter" not in params
        assert parsed_url.fragment == "browse-records"

    def test_search_results_redirects_when_search_filter_only_is_added(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given only a search_filter term
        When search results are requested
        Then the request redirects with that term as the quoted query
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?search_filter=extra term")

        assert response.status_code == 302
        redirect_location = response.headers["Location"]
        parsed_url = urlparse(redirect_location)
        params = parse_qs(parsed_url.query)

        assert parsed_url.path == self.route_url
        assert params["query"] == ['"extra term"']
        assert "search_filter" not in params
        assert parsed_url.fragment == "browse-records"

    @patch("app.main.routes.execute_search", side_effect=NotFound())
    @patch("app.main.routes.setup_opensearch")
    def test_search_results_redirects_invalid_page_to_page_one(
        self,
        mock_setup_opensearch,
        _mock_execute_search,
        client: FlaskClient,
        mock_all_access_user,
    ):
        """
        Given a page number outside valid result bounds
        When search execution raises NotFound
        Then the route redirects back to page 1
        """
        mock_all_access_user(client)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )

        response = client.get(f"{self.route_url}?query=test&page=999")

        assert response.status_code == 302
        redirect_location = response.headers["Location"]
        parsed_url = urlparse(redirect_location)
        params = parse_qs(parsed_url.query)

        assert parsed_url.path == self.route_url
        assert params["page"] == ["1"]
        assert params["query"] == ["test"]

    @patch("app.main.routes.setup_opensearch")
    def test_search_results_returns_504_for_opensearch_timeout(
        self, mock_setup_opensearch, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an OpenSearch timeout during search
        When /search/results is requested
        Then the route returns a 504 response
        """
        mock_all_access_user(client)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_side_effect=opensearchpy.exceptions.ConnectionTimeout()
        )

        response = client.get(f"{self.route_url}?query=test")

        assert response.status_code == 504
        assert b"Bad Gateway" in response.data

    @patch("app.main.routes.AYRUser")
    def test_search_results_returns_403_for_standard_user_without_body(
        self, mock_ayr_user, client: FlaskClient, mock_all_access_user
    ):
        """
        Given a standard user without a mapped transferring body
        When they access /search/results
        Then the route returns 403
        """
        mock_all_access_user(client)
        mock_ayr_user.return_value.is_standard_user = True
        mock_ayr_user.return_value.is_all_access_user = False
        mock_ayr_user.return_value.transferring_body = None

        response = client.get(f"{self.route_url}?query=test")

        assert response.status_code == 403

    @patch("app.main.routes.AYRUser")
    def test_search_results_returns_404_when_standard_user_body_missing(
        self, mock_ayr_user, client: FlaskClient, mock_all_access_user
    ):
        """
        Given a standard user mapped to a non-existent body
        When they access /search/results
        Then the route returns 404
        """
        mock_all_access_user(client)
        mock_ayr_user.return_value.is_standard_user = True
        mock_ayr_user.return_value.is_all_access_user = False
        mock_ayr_user.return_value.transferring_body = SimpleNamespace(
            BodyId=uuid.uuid4()
        )

        response = client.get(f"{self.route_url}?query=test")

        assert response.status_code == 404

    def test_search_results_path_id_returns_404_for_all_access_user(
        self, client: FlaskClient, mock_all_access_user
    ):
        """
        Given an all-access user
        When they access /search/results/<_id>
        Then the route returns 404 because path-scoped results are standard-user only
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}/{uuid.uuid4()}?query=test")

        assert response.status_code == 404

    @patch("app.main.routes.execute_search")
    @patch("app.main.routes.setup_opensearch")
    def test_search_results_ignores_path_body_id_for_standard_user(
        self,
        mock_setup_opensearch,
        mock_execute_search,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given a standard user and a mismatched body id in the path
        When /search/results/<_id> is requested
        Then the query still uses the user's own body filter
        """
        body = browse_consignment_files[0].consignment.series.body
        other_body_id = uuid.uuid4()

        mock_standard_user(client, body.Name)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )
        mock_execute_search.return_value = OS_MOCK_RESULTS

        response = client.get(f"{self.route_url}/{other_body_id}?query=test")

        assert response.status_code == 200
        _, dsl_query, _, _ = mock_execute_search.call_args[0]
        assert dsl_query["query"]["bool"]["filter"] == [
            {
                "term": {
                    "transferring_body_id.keyword": str(body.BodyId),
                }
            }
        ]

    @patch("app.main.routes.get_open_search_fields_to_search_on_and_sorting")
    @patch("app.main.routes.execute_search")
    @patch("app.main.routes.setup_opensearch")
    def test_search_results_passes_selected_search_area_and_sort(
        self,
        mock_setup_opensearch,
        mock_execute_search,
        mock_get_fields_and_sorting,
        client: FlaskClient,
        mock_all_access_user,
    ):
        """
        Given explicit search_area and sort query params
        When /search/results builds OpenSearch fields and sorting
        Then those selected values are passed through unchanged
        """
        mock_all_access_user(client)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )
        mock_execute_search.return_value = OS_MOCK_RESULTS
        mock_get_fields_and_sorting.return_value = (
            ["file_name^1"],
            [{"_score": {"order": "asc"}}],
        )

        response = client.get(
            f"{self.route_url}?query=test&search_area=metadata&sort=least_matches"
        )

        assert response.status_code == 200
        mock_get_fields_and_sorting.assert_called_once_with(
            "metadata", "least_matches"
        )

    @patch("app.main.routes.extract_search_terms")
    @patch("app.main.routes.execute_search")
    @patch("app.main.routes.setup_opensearch")
    def test_search_results_trims_trailing_comma_before_extracting_terms(
        self,
        mock_setup_opensearch,
        mock_execute_search,
        mock_extract_search_terms,
        client: FlaskClient,
        mock_all_access_user,
    ):
        """
        Given a query that ends with a trailing comma
        When search terms are extracted
        Then the trailing comma is removed before extraction
        """
        mock_all_access_user(client)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )
        mock_execute_search.return_value = OS_MOCK_RESULTS
        mock_extract_search_terms.return_value = (["test"], [])

        response = client.get(f"{self.route_url}?query=test,")

        assert response.status_code == 200
        mock_extract_search_terms.assert_called_once_with("test")

    @patch("app.main.routes.setup_opensearch")
    def test_search_results_single_term_remove_link_targets_browse(
        self, mock_setup_opensearch, client: FlaskClient, mock_all_access_user
    ):
        """
        Given one applied search term for an all-access user
        When the term removal link is rendered
        Then it points back to /browse
        """
        mock_all_access_user(client)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )

        response = client.get(f"{self.route_url}?query=test")

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        remove_term_link = soup.find(
            "a",
            attrs={
                "class": "search-term-link",
                "aria-label": "Remove filter for 'test'",
            },
        )

        assert remove_term_link is not None
        assert remove_term_link["href"] == "/browse"

    @patch("app.main.routes.setup_opensearch")
    def test_search_results_single_term_remove_link_targets_transferring_body_for_standard_user(
        self,
        mock_setup_opensearch,
        client: FlaskClient,
        mock_standard_user,
        browse_consignment_files,
    ):
        """
        Given one applied search term for a standard user
        When the term removal link is rendered
        Then it points back to that user's transferring body browse route
        """
        body = browse_consignment_files[0].consignment.series.body
        mock_standard_user(client, body.Name)
        mock_setup_opensearch.return_value = MockOpenSearch(
            search_return_value=OS_MOCK_RESULTS
        )

        response = client.get(f"{self.route_url}?query=test")

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        remove_term_link = soup.find(
            "a",
            attrs={
                "class": "search-term-link",
                "aria-label": "Remove filter for 'test'",
            },
        )

        assert remove_term_link is not None
        assert (
            remove_term_link["href"]
            == f"/browse/transferring_body/{body.BodyId}"
        )
