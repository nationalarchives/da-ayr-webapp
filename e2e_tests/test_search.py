import os
import re

import requests
from playwright.sync_api import Page, expect


def print_opensearch_scores(query="a", transferring_body_id=None):
    """Helper to print OpenSearch scores for debugging ordering differences."""
    opensearch_host = os.environ.get(
        "OPEN_SEARCH_HOST", "http://localhost:9200"
    )
    opensearch_user = os.environ.get("OPEN_SEARCH_USER", "admin")
    opensearch_pass = os.environ.get(
        "OPEN_SEARCH_PASSWORD",
        os.environ.get("OPENSEARCH_INITIAL_ADMIN_PASSWORD", ""),
    )

    search_body = {
        "query": {
            "bool": {
                "should": [{"multi_match": {"query": query, "fields": ["*"]}}],
                "minimum_should_match": 1,
            }
        },
        "sort": [
            {"_score": {"order": "desc"}},
            {"file_name.keyword": {"order": "asc"}},
            {"file_id.keyword": {"order": "asc"}},
        ],
        "size": 20,
        "_source": ["file_name", "consignment_reference", "transferring_body"],
    }

    if transferring_body_id:
        search_body["query"]["bool"]["filter"] = [
            {"term": {"transferring_body_id.keyword": transferring_body_id}}
        ]

    try:
        response = requests.get(
            f"{opensearch_host}/documents/_search",
            json=search_body,
            auth=(opensearch_user, opensearch_pass),
            verify=False,
            timeout=10,
        )
        results = response.json()
        print("\n=== OpenSearch Scores ===")
        for hit in results.get("hits", {}).get("hits", []):
            print(
                f"Score: {hit['_score']:.6f}, "
                f"File: {hit['_source'].get('file_name', 'N/A')}, "
                f"Consignment: {hit['_source'].get('consignment_reference', 'N/A')}, "
                f"ID: {hit['_id']}"
            )
        print("=========================\n")
    except Exception as e:
        print(f"Could not fetch OpenSearch scores: {e}")


def verify_search_results_summary_header_row(header_rows):
    assert header_rows == [
        "Results found within each Transferring body",
        "Records found",
    ]


def verify_search_transferring_body_header_row(header_rows):
    assert header_rows == [
        "Found within",
        "Search results",
        "Series",
        "Consignment ref",
        "Status",
        "Record opening date",
    ]


def verify_search_transferring_body_table_header_row(header_rows):
    assert header_rows == [
        "Found within",
        "Search results",
    ]


def verify_search_transferring_body_inner_table_row(header_rows):
    assert set(header_rows) == {
        "Consignment ref",
        "Record opening date",
        "Series",
        "Status",
    }


class TestSearch:
    @property
    def browse_route_url(self):
        return "/browse"

    def test_search_returns_results_summary(self, aau_user_page: Page, utils):
        """
        Given a standard user
        When they interact with the search form and submit a query
        Then the table should contain the expected headers and entries
        and sorted transferring bodies in alphabetic order (A to Z)
        on a search results summary screen
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.wait_for_selector("#tbl_result")

        header_rows = utils.get_desktop_page_table_headers(aau_user_page)
        rows = utils.get_desktop_page_table_rows(aau_user_page)

        expected_rows = [["Testing A", "16"], ["AYR Test Data Department", "2"]]
        verify_search_results_summary_header_row(header_rows)
        assert rows == expected_rows


class TestSearchResultsSummary:
    @property
    def search_results_summary_route_url(self):
        return "/search_results_summary?query=a"

    def test_select_transferring_body_search_results(
        self, aau_user_page: Page, utils
    ):
        """
        Given a user on the search results summary page for a query
        When they click on one of the transferring bodies
        Then they are redirected to the search results for that transferring body for the query
        """
        aau_user_page.goto(self.search_results_summary_route_url)
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.wait_for_selector("#tbl_result")
        aau_user_page.click('label[for="contact"]')
        aau_user_page.locator(
            ".govuk-button.govuk-button__sort-container-update-button"
        ).nth(1).click()

        header_rows = utils.get_desktop_page_transferring_body_table_headers(
            aau_user_page
        )

        inner_table_header_rows = (
            utils.get_desktop_page_transferring_body_inner_table_headers(
                aau_user_page
            )
        )

        table_row_metadata = utils.get_desktop_page_table_metadata(
            aau_user_page
        )

        # Print OpenSearch scores for debugging
        # Testing A transferring_body_id
        print_opensearch_scores(
            query="a",
            transferring_body_id="c3e3fd83-4d52-4638-a085-1f4e4e4dfa50",
        )

        expected_row_metadata = [
            ["TSTA 1", "TDR-2023-BV6", "Closed", "18/10/2048"],
            ["TSTA 1", "TDR-2023-BV6", "Open", "–"],
            ["TSTA 1", "TDR-2023-BV6", "Open", "–"],
            ["TSTA 1", "TDR-2023-BV6", "Open", "–"],
            ["TSTA 1", "TDR-2023-BV6", "Open", "–"],
            ["TSTA 1", "TDR-2023-GXFH", "Open", "–"],
            ["TSTA 1", "TDR-2023-GXFH", "Open", "–"],
            ["TSTA 1", "TDR-2023-GXFH", "Open", "–"],
            ["TSTA 1", "TDR-2023-GXFH", "Open", "–"],
            ["TSTA 1", "TDR-2023-GXFH", "Open", "–"],
        ]

        assert table_row_metadata == expected_row_metadata
        # # Sort both lists to make comparison order-independent
        # # (OpenSearch result order can vary between environments)
        # assert sorted(table_row_metadata) == sorted(expected_row_metadata)

        verify_search_transferring_body_table_header_row(header_rows)
        verify_search_transferring_body_inner_table_row(inner_table_header_rows)


class TestSearchTransferringBody:
    @property
    def browse_route_url(self):
        return "/browse"

    @property
    def browse_transferring_body_route_url(self):
        return "/browse/transferring_body"

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    def test_remove_all_terms_as_standard_user_redirects_to_browse_transferring_body(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with a search term
        and then remove the search term
        Then they should be redirected to browse transferring body page.
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        locator = aau_user_page.locator(
            "a.search-term-link[aria-label=\"Remove filter for 'a'\"] img.close-icon"
        )
        locator.wait_for(state="visible")
        locator.click()

        browse_transferring_body_url = re.escape(
            self.browse_transferring_body_route_url
        )
        params = r"\?.*search_area=everywhere.*"
        # Use regex to match URL with additional query parameters
        pattern = rf""".*{browse_transferring_body_url}/{re.escape(self.transferring_body_id)}{params}"""
        url_pattern = re.compile(pattern)
        expect(aau_user_page).to_have_url(url_pattern)

    def test_click_on_clear_all_as_aau_user_redirects_to_browse(
        self, aau_user_page: Page
    ):
        """
        Given an all access user on the search transferring body page
        When they interact with the search form and submit a query with multiple search terms
        and the click on clear all option
        Then they should be redirected to browse all page.
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.get_by_role("link", name="Clear all").click()

        expect(aau_user_page).to_have_url(
            f"{self.browse_route_url}#browse-records"
        )

    def test_click_on_clear_all_as_standard_user_redirects_to_browse_transferring_body(
        self, standard_user_page: Page
    ):
        """
        Given a standard access user on the search transferring body page
        When they interact with the search form and submit a query with multiple search terms
        and the click on clear all option
        Then they should be redirected to browse all page.
        """
        url = f"{self.browse_transferring_body_route_url}/{self.transferring_body_id}#browse-records"
        standard_user_page.goto(url)
        standard_user_page.locator("#search-input").click()
        standard_user_page.locator("#search-input").fill("a")
        standard_user_page.get_by_role("button", name="Search").click()
        standard_user_page.get_by_role("link", name="Clear all").click()

        expect(standard_user_page).to_have_url(url)
