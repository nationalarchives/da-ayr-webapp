from unittest.mock import Mock, patch

import pytest
from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.factories import FileFactory


def _browse_search_documents():
    filenames = [
        "first_file.txt",
        "second_file.pdf",
        "third_file.doc",
        "fourth_file.docx",
        "fifth_file.docx",
        "sixth_file.ppt",
        *[f"file_{number}.txt" for number in range(7, 28)],
    ]
    return [
        {
            "_source": {
                "file_id": f"00000000-0000-0000-0000-{number:012d}",
                "file_name": filename,
                "file_path": f"/data/{filename}",
                "closure_type": "Open",
                "opening_date": "2024-01-02T00:00:00",
                "date_last_modified": "2024-01-03T00:53:25.593740+00:00",
                "series_id": "00000000-0000-0000-0000-000000000101",
                "series_name": "HO 405",
                "transferring_body_id": (
                    "00000000-0000-0000-0000-000000000201"
                ),
                "transferring_body": "Land Registry",
                "consignment_id": "00000000-0000-0000-0000-000000000301",
                "consignment_reference": "AYR-2026-KSJ2",
                "consignment_transfer_complete_date": "2024-02-03",
            }
        }
        for number, filename in enumerate(filenames, start=1)
    ]


def _search_response(total=27, page=1, per_page=5, hits=None):
    documents = _browse_search_documents()
    start = (page - 1) * per_page
    page_hits = (
        hits if hits is not None else documents[start : start + per_page]
    )
    return {
        "hits": {
            "total": {"value": total, "relation": "eq"},
            "hits": page_hits,
        }
    }


def _set_empty_search_response(execute_search):
    execute_search.side_effect = None
    execute_search.return_value = _search_response(total=0, hits=[])


def _mock_browse_aggregation_response(query):
    if "browse_transferring_bodies" in query["aggs"]:
        return {
            "aggregations": {
                "browse_transferring_bodies": {
                    "buckets": [
                        {"key": {"transferring_body": "first_body"}},
                        {"key": {"transferring_body": "second_body"}},
                    ]
                }
            }
        }
    return {
        "aggregations": {
            "browse_autofill_options": {"buckets": []},
        }
    }


def _autofill_row(body, series, consignment_reference=""):
    return {
        "transferring_body": body,
        "series": series,
        "consignment_reference": consignment_reference,
    }


def verify_browse_view_header_row(data, expected_first_header):
    """
    Check browse records header row values against expected values.
    """
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")

    expected_row = [
        expected_first_header,
        "Series",
        "Status",
        "Opening date",
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_row


def verify_filters_heading(data, expected_heading):
    """
    Check the filters heading text against expected value.
    """
    soup = BeautifulSoup(data, "html.parser")
    heading = soup.find("h2", class_="govuk-heading-m--browse-filter-title")

    assert heading is not None
    assert " ".join(heading.get_text(separator=" ").split()) == expected_heading


def verify_scope_text(data, expected_text):
    """
    Check the scope text above records count against expected value.
    """
    soup = BeautifulSoup(data, "html.parser")
    scope_text = soup.find("span", class_="browse__scope-text")

    assert scope_text is not None
    assert " ".join(scope_text.get_text(separator=" ").split()) == expected_text


class TestBrowse:
    @pytest.fixture(autouse=True)
    def mock_opensearch(self, monkeypatch):
        open_search = Mock()
        open_search.search.side_effect = lambda **kwargs: (
            _mock_browse_aggregation_response(kwargs["body"])
        )
        execute_search = Mock(
            side_effect=lambda _client, _query, page, per_page, **_kwargs: (
                _search_response(page=page, per_page=per_page)
            )
        )
        monkeypatch.setattr(
            "app.main.routes.setup_opensearch", lambda: open_search
        )
        monkeypatch.setattr("app.main.routes.execute_search", execute_search)
        return execute_search

    @property
    def route_url(self):
        return "/browse"

    def test_browse_get_view_for_all_access_user(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given an all-access user
        When they visit browse records
        Then they see the records table with key record details
        and first page pagination
        """
        mock_all_access_user(client)

        response = client.get(self.route_url)

        assert response.status_code == 200
        assert b"Search for digital records" in response.data
        assert b"27 records" in response.data
        assert b"last modified" in response.data
        assert b"consignment" in response.data
        assert b"Land Registry" in response.data
        verify_filters_heading(response.data, "Filters (0)")
        verify_scope_text(response.data, "All available records")

        verify_browse_view_header_row(response.data, "Showing 1\u20135 of 27")

        soup = BeautifulSoup(response.data, "html.parser")
        record_links = soup.select(
            "tbody.govuk-table__body td[colspan='4'] > a[href^='/record/']"
        )
        assert len(record_links) == 5

    def test_browse_scopes_search_for_standard_user(
        self,
        client: FlaskClient,
        mock_standard_user,
        mock_opensearch,
        browse_files,
    ):
        """
        Given a standard user with access to one transferring body
        When they visit browse records
        Then the OpenSearch query is scoped to that body
        """
        mock_standard_user(client, "first_body")

        response = client.get(self.route_url)

        assert response.status_code == 200
        verify_filters_heading(response.data, "Filters (0)")
        verify_scope_text(response.data, "first_body")

        soup = BeautifulSoup(response.data, "html.parser")
        transferring_body_filter = soup.find(
            "input", id="transferring_body_filter"
        )
        assert transferring_body_filter is not None
        assert transferring_body_filter.get("value") == "first_body"
        body_id = browse_files[0].consignment.series.body.BodyId
        _, query, _, _ = mock_opensearch.call_args.args
        assert {
            "term": {"transferring_body_id.keyword": str(body_id)}
        } in query["query"]["bool"]["filter"]

    @patch("app.main.routes.AYRUser")
    def test_browse_forbids_standard_user_without_body(
        self, mock_ayr_user, client: FlaskClient, mock_standard_user
    ):
        mock_standard_user(client, "first_body")
        mock_ayr_user.return_value.is_standard_user = True
        mock_ayr_user.return_value.transferring_body = None

        response = client.get(self.route_url)

        assert response.status_code == 403

    def test_browse_second_page_shows_expected_range_and_links(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given more than one page of records
        When the user opens page 2
        Then pagination displays expected range and previous/next links
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?page=2")

        assert response.status_code == 200
        verify_browse_view_header_row(response.data, "Showing 6\u201310 of 27")
        verify_scope_text(response.data, "All available records")

        soup = BeautifulSoup(response.data, "html.parser")

        previous_link = soup.select_one(".govuk-pagination__prev a")
        next_link = soup.select_one(".govuk-pagination__next a")

        assert previous_link is not None
        assert next_link is not None
        assert "page=1" in previous_link["href"]
        assert "page=3" in next_link["href"]

    def test_browse_standard_user_transferring_body_does_not_count(
        self, client: FlaskClient, mock_standard_user, browse_files
    ):
        """
        Given a standard user with one accessible transferring body
        When they explicitly submit that transferring body filter
        Then it does not contribute to the filter count
        """
        mock_standard_user(client, "first_body")

        response = client.get(
            f"{self.route_url}?transferring_body_filter=first_body"
        )

        assert response.status_code == 200
        verify_filters_heading(response.data, "Filters (0)")

    @patch(
        "app.main.util.browse_utils.get_autofill_options_rows_from_opensearch"
    )
    def test_browse_standard_user_consignment_filter_without_series_backfills_and_applies_series(
        self,
        mock_get_autofill_options_rows,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
    ):
        """
        Given a standard user with a consignment filter and no series filter
        When browse records is requested
        Then the matching series value is auto-populated and applied
        """
        mock_standard_user(client, "first_body")
        mock_get_autofill_options_rows.return_value = [
            _autofill_row(
                "first_body",
                "first_series",
                "TDR-2023-FI1",
            )
        ]

        response = client.get(
            f"{self.route_url}?consignment_reference=TDR-2023-FI1"
        )

        assert response.status_code == 200

        soup = BeautifulSoup(response.data, "html.parser")
        transferring_body_filter = soup.find(
            "input", id="transferring_body_filter"
        )
        series_filter = soup.find("input", id="series_filter")
        consignment_filter = soup.find("input", id="consignment_reference")

        assert transferring_body_filter is not None
        assert series_filter is not None
        assert consignment_filter is not None
        assert transferring_body_filter.get("value") == "first_body"
        assert series_filter.get("value") == "first_series"
        assert consignment_filter.get("value") == "TDR-2023-FI1"
        verify_filters_heading(response.data, "Filters (2)")

    @patch(
        "app.main.util.browse_utils.get_autofill_options_rows_from_opensearch"
    )
    def test_browse_adds_consignment_filter_to_search(
        self,
        mock_get_autofill_options_rows,
        client: FlaskClient,
        mock_all_access_user,
        mock_opensearch,
        browse_files,
    ):
        """
        Given a consignment reference filter
        When browse records is requested with that filter
        Then a match phrase consignment filter is sent to OpenSearch
        """
        mock_all_access_user(client)
        mock_get_autofill_options_rows.return_value = [
            _autofill_row(
                "second_body",
                "second_series",
                "TDR-2023-TH3",
            )
        ]

        response = client.get(
            f"{self.route_url}?consignment_reference=TDR-2023-TH3"
        )

        assert response.status_code == 200
        assert b'value="TDR-2023-TH3"' in response.data
        verify_filters_heading(response.data, "Filters (3)")
        verify_scope_text(response.data, "All available records")

        soup = BeautifulSoup(response.data, "html.parser")
        transferring_body_filter = soup.find(
            "input", id="transferring_body_filter"
        )
        series_filter = soup.find("input", id="series_filter")

        assert transferring_body_filter is not None
        assert series_filter is not None
        assert transferring_body_filter.get("value") == "second_body"
        assert series_filter.get("value") == "second_series"

        _, query, _, _ = mock_opensearch.call_args.args
        assert {
            "match_phrase": {"consignment_reference": "TDR-2023-TH3"}
        } in query["query"]["bool"]["filter"]

    def test_browse_builds_match_phrase_consignment_filter(
        self,
        client: FlaskClient,
        mock_all_access_user,
        mock_opensearch,
        browse_files,
    ):
        """
        Given an all-access user with a partial consignment reference filter
        When browse records is requested
        Then OpenSearch receives the partial value as a match phrase filter
        """
        mock_all_access_user(client)

        response = client.get(
            f"{self.route_url}?consignment_reference=TDR-2023-TH"
        )

        assert response.status_code == 200
        _, query, _, _ = mock_opensearch.call_args.args
        assert {
            "match_phrase": {"consignment_reference": "TDR-2023-TH"}
        } in query["query"]["bool"]["filter"]

    def test_browse_builds_match_phrase_series_filter(
        self,
        client: FlaskClient,
        mock_all_access_user,
        mock_opensearch,
        browse_files,
    ):
        """
        Given an all-access user with a partial series filter
        When browse records is requested
        Then OpenSearch receives the partial value as a match phrase filter
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?series_filter=second")

        assert response.status_code == 200
        _, query, _, _ = mock_opensearch.call_args.args
        assert {"match_phrase": {"series_name": "second"}} in query["query"][
            "bool"
        ]["filter"]

    @patch(
        "app.main.util.browse_utils.get_autofill_options_rows_from_opensearch"
    )
    def test_browse_all_access_consignment_filter_autofills_transferring_body_and_series(
        self,
        mock_get_autofill_options_rows,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
    ):
        """
        Given an all-access user with no transferring body or series filter selected
        When they filter by consignment only
        Then transferring body and series are auto-populated from the match
        """
        mock_all_access_user(client)
        mock_get_autofill_options_rows.return_value = [
            _autofill_row(
                "second_body",
                "second_series",
                "TDR-2023-TH3",
            )
        ]

        initial_response = client.get(self.route_url)

        assert initial_response.status_code == 200
        initial_soup = BeautifulSoup(initial_response.data, "html.parser")
        initial_transferring_body_filter = initial_soup.find(
            "input", id="transferring_body_filter"
        )
        initial_series_filter = initial_soup.find("input", id="series_filter")

        assert initial_transferring_body_filter is not None
        assert initial_series_filter is not None
        assert not initial_transferring_body_filter.get("value")
        assert not initial_series_filter.get("value")

        filtered_response = client.get(
            f"{self.route_url}?consignment_reference=TDR-2023-TH3"
        )

        assert filtered_response.status_code == 200
        filtered_soup = BeautifulSoup(filtered_response.data, "html.parser")
        filtered_transferring_body_filter = filtered_soup.find(
            "input", id="transferring_body_filter"
        )
        filtered_series_filter = filtered_soup.find("input", id="series_filter")

        assert filtered_transferring_body_filter is not None
        assert filtered_series_filter is not None
        assert filtered_transferring_body_filter.get("value") == "second_body"
        assert filtered_series_filter.get("value") == "second_series"

    @patch(
        "app.main.util.browse_utils.get_autofill_options_rows_from_opensearch"
    )
    def test_browse_series_filter_backfills_transferring_body(
        self,
        mock_get_autofill_options_rows,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
    ):
        """
        Given a series filter that maps to a single transferring body
        When browse records is requested with that series
        Then the transferring body filter is auto-populated
        """
        mock_all_access_user(client)
        mock_get_autofill_options_rows.return_value = [
            _autofill_row("second_body", "second_series")
        ]

        response = client.get(f"{self.route_url}?series_filter=second_series")

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        transferring_body_filter = soup.find(
            "input", id="transferring_body_filter"
        )
        series_filter = soup.find("input", id="series_filter")

        assert transferring_body_filter is not None
        assert series_filter is not None
        assert transferring_body_filter.get("value") == "second_body"
        assert series_filter.get("value") == "second_series"

    @patch(
        "app.main.util.browse_utils.get_autofill_options_rows_from_opensearch"
    )
    def test_browse_skips_autofill_query_on_initial_load(
        self,
        mock_get_autofill_options_rows,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
    ):
        """
        Given no series or consignment filter in the request
        When browse records is requested
        Then the targeted autofill options query is not executed
        """
        mock_all_access_user(client)
        mock_get_autofill_options_rows.return_value = []

        response = client.get(self.route_url)

        assert response.status_code == 200
        mock_get_autofill_options_rows.assert_not_called()

    @patch(
        "app.main.util.browse_utils.get_autofill_options_rows_from_opensearch"
    )
    def test_browse_uses_targeted_autofill_query_for_series_filter(
        self,
        mock_get_autofill_options_rows,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
    ):
        """
        Given a series filter without an explicit transferring body
        When browse records is requested
        Then the targeted autofill options query executes with the series value
        """
        mock_all_access_user(client)
        mock_get_autofill_options_rows.return_value = []

        response = client.get(f"{self.route_url}?series_filter=second_series")

        assert response.status_code == 200
        call_args = mock_get_autofill_options_rows.call_args.args
        assert call_args[1:] == (None, "second_series", "")

    @patch(
        "app.main.util.browse_utils.get_transferring_body_options_from_opensearch"
    )
    def test_browse_queries_transferring_body_options_once_for_all_access_user(
        self,
        mock_get_transferring_body_options,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
    ):
        """
        Given an all-access user
        When browse records is requested
        Then transferring body options are queried exactly once
        """
        mock_all_access_user(client)
        mock_get_transferring_body_options.return_value = [
            "first_body",
            "second_body",
        ]

        response = client.get(self.route_url)

        assert response.status_code == 200
        mock_get_transferring_body_options.assert_called_once()

    @patch(
        "app.main.util.browse_utils.get_autofill_options_rows_from_opensearch"
    )
    @patch(
        "app.main.util.browse_utils.get_transferring_body_options_from_opensearch"
    )
    def test_browse_series_filter_uses_expected_filter_queries_once_each(
        self,
        mock_get_transferring_body_options,
        mock_get_autofill_options_rows,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
    ):
        """
        Given an all-access user with series filter only
        When browse records is requested
        Then transferring body options and autofill options queries each run once
        """
        mock_all_access_user(client)
        mock_get_transferring_body_options.return_value = [
            "first_body",
            "second_body",
        ]
        mock_get_autofill_options_rows.return_value = []

        response = client.get(f"{self.route_url}?series_filter=second_series")

        assert response.status_code == 200
        mock_get_transferring_body_options.assert_called_once()
        call_args = mock_get_autofill_options_rows.call_args.args
        assert call_args[1:] == (None, "second_series", "")

    @patch(
        "app.main.util.browse_utils.get_transferring_body_options_from_opensearch"
    )
    def test_browse_standard_user_skips_transferring_body_options_query(
        self,
        mock_get_transferring_body_options,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
    ):
        """
        Given a standard user with a single scope
        When browse records is requested
        Then transferring body options query is skipped
        """
        mock_standard_user(client, "first_body")

        response = client.get(self.route_url)

        assert response.status_code == 200
        mock_get_transferring_body_options.assert_not_called()

    def test_browse_series_filter_has_no_datalist(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given the browse records page
        When the series filter is rendered
        Then it is a plain text input without a datalist
        """
        mock_all_access_user(client)

        response = client.get(self.route_url)

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        series_filter = soup.find("input", id="series_filter")
        series_datalist = soup.find("datalist", id="series_options")

        assert series_filter is not None
        assert series_filter.get("list") is None
        assert series_datalist is None

    def test_browse_status_and_date_radio_defaults(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given the browse records page
        When filters render
        Then status defaults to all and dates defaults to last modified
        """
        mock_all_access_user(client)

        response = client.get(self.route_url)

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        status_all = soup.find("input", id="recordStatus-all")
        status_open = soup.find("input", id="recordStatus-open")
        status_closed = soup.find("input", id="recordStatus-closed")
        last_modified_date = soup.find("input", id="date_last_modified")
        transferred_date = soup.find("input", id="transferred_date")

        assert status_all is not None
        assert status_open is not None
        assert status_closed is not None
        assert last_modified_date is not None
        assert transferred_date is not None
        assert status_all.has_attr("checked")
        assert not status_open.has_attr("checked")
        assert not status_closed.has_attr("checked")
        assert last_modified_date.has_attr("checked")
        assert not transferred_date.has_attr("checked")

    def test_browse_status_filter_open_selection_persists(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given the open status filter
        When browse records is requested
        Then the open status option is selected
        and any visible status tags are open
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?record_status=open")

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        status_all = soup.find("input", id="recordStatus-all")
        status_open = soup.find("input", id="recordStatus-open")
        status_closed = soup.find("input", id="recordStatus-closed")

        assert status_all is not None
        assert status_open is not None
        assert status_closed is not None
        assert not status_all.has_attr("checked")
        assert status_open.has_attr("checked")
        assert not status_closed.has_attr("checked")

        status_tags = soup.select(
            "td.browse__meta-cell--status strong.govuk-tag"
        )
        assert all(
            tag.get_text(strip=True) in ["Open", "Unknown"]
            for tag in status_tags
        )

    def test_browse_date_filter_field_selection_persists(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given an opening date filter field selection
        When browse records is requested
        Then opening date radio remains selected
        """
        mock_all_access_user(client)

        response = client.get(
            f"{self.route_url}?date_filter_field=opening_date"
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        opening_date = soup.find("input", id="opening_date")

        assert opening_date is not None
        assert opening_date.has_attr("checked")

    def test_browse_consignment_filter_has_no_datalist(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given the browse records page
        When the consignment filter is rendered
        Then it is a plain text input without a datalist
        """
        mock_all_access_user(client)

        response = client.get(self.route_url)

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")
        consignment_filter = soup.find("input", id="consignment_reference")
        consignment_datalist = soup.find("datalist", id="consignment_options")

        assert consignment_filter is not None
        assert consignment_filter.get("list") is None
        assert consignment_datalist is None

    @pytest.mark.parametrize(
        "per_page, expected_header, expected_count",
        [
            (10, "Showing 1\u201310 of 27", 10),
            (20, "Showing 1\u201320 of 27", 20),
        ],
    )
    def test_browse_per_page_query_updates_page_size(
        self,
        client: FlaskClient,
        mock_all_access_user,
        browse_files,
        per_page,
        expected_header,
        expected_count,
    ):
        """
        Given browse records supports per_page query input
        When per_page is requested from the frontend
        Then the first page size and range text match per_page
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?per_page={per_page}")

        assert response.status_code == 200
        verify_browse_view_header_row(response.data, expected_header)

        soup = BeautifulSoup(response.data, "html.parser")
        record_links = soup.select(
            "tbody.govuk-table__body td[colspan='4'] > a[href^='/record/']"
        )
        assert len(record_links) == expected_count

    def test_browse_invalid_page_redirects_to_first_page(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given an invalid out-of-range page number
        When browse records is requested
        Then the user is redirected to page 1
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?page=999")

        assert response.status_code == 302
        assert "page=1" in response.headers["Location"]

    def test_browse_per_page_persists_in_filter_controls(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given records-per-page is explicitly selected
        When browse records filters are rendered
        Then per_page is preserved in filter form submits and clear-filters link
        """
        mock_all_access_user(client)

        response = client.get(f"{self.route_url}?per_page=20")

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        filters_form = soup.find("form", action="/browse#browse")
        assert filters_form is not None

        hidden_per_page = filters_form.find(
            "input",
            {"type": "hidden", "name": "per_page", "value": "20"},
        )
        clear_filters_link = filters_form.find("a", string="Clear filters")

        assert hidden_per_page is not None
        assert clear_filters_link is not None
        assert "per_page=20" in clear_filters_link.get("href", "")

    def test_browse_filters_and_sort_persist_in_per_page_controls(
        self, client: FlaskClient, mock_all_access_user, browse_files
    ):
        """
        Given browse records has active filters and sort
        When per-page controls are rendered
        Then sort and per-page controls preserve active query params
        and submit only their own value changes
        """
        mock_all_access_user(client)

        response = client.get(
            f"{self.route_url}?consignment_reference=TDR-2023-TH3&sort=file_name-desc&page=1&per_page=10"
        )

        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        forms = soup.select("form.ayr-results-control")
        assert len(forms) == 2

        sort_form = next(
            form for form in forms if form.find("select", {"name": "sort"})
        )
        per_page_form = next(
            form for form in forms if form.find("select", {"name": "per_page"})
        )

        for form in [sort_form, per_page_form]:
            hidden_consignment = form.find(
                "input",
                {
                    "type": "hidden",
                    "name": "consignment_reference",
                    "value": "TDR-2023-TH3",
                },
            )
            hidden_page = form.find("input", {"type": "hidden", "name": "page"})

            assert hidden_consignment is not None
            assert hidden_page is None

        selected_sort_option = sort_form.find("option", selected=True)
        selected_per_page_option = per_page_form.find("option", selected=True)
        assert selected_sort_option is not None
        assert selected_sort_option.get("value") == "file_name-desc"
        assert selected_per_page_option is not None
        assert selected_per_page_option.get("value") == "10"
        assert sort_form.get("data-auto-submit") is not None
        assert per_page_form.get("data-auto-submit") is not None
        assert "ayr-results-control--auto-submit" not in sort_form.get(
            "class", []
        )
        assert "ayr-results-control--auto-submit" not in per_page_form.get(
            "class", []
        )
        assert sort_form.find("button", {"type": "submit"}) is not None
        assert per_page_form.find("button", {"type": "submit"}) is not None
        assert (
            per_page_form.find("input", {"type": "hidden", "name": "sort"})
            is not None
        )

    def test_browse_no_results_for_nonsensical_filter(
        self,
        client: FlaskClient,
        mock_all_access_user,
        mock_opensearch,
        browse_files,
    ):
        """
        Given a nonsensical filter term
        When browse records is requested
        Then no records found is displayed
        """
        mock_all_access_user(client)
        _set_empty_search_response(mock_opensearch)

        response = client.get(f"{self.route_url}?series_filter=zzzzzzzzzzzzzz")

        assert response.status_code == 200
        assert b"No results found" in response.data

    def test_browse_invalid_page_redirects_when_no_results(
        self,
        client: FlaskClient,
        mock_all_access_user,
        mock_opensearch,
        browse_files,
    ):
        """
        Given a filter that returns zero records
        When page > 1 is requested
        Then the user is redirected to page 1
        """
        mock_all_access_user(client)
        _set_empty_search_response(mock_opensearch)

        response = client.get(
            f"{self.route_url}?series_filter=zzzzzzzzzzzzzz&page=2"
        )

        assert response.status_code == 302
        assert "page=1" in response.headers["Location"]
        assert "series_filter=zzzzzzzzzzzzzz" in response.headers["Location"]

    @pytest.mark.parametrize("body_name", ["first_body", "second_body"])
    def test_browse_scope_text_changes_for_different_accounts(
        self,
        client: FlaskClient,
        mock_standard_user,
        browse_files,
        body_name,
    ):
        """
        Given different standard user accounts
        When browse records is requested
        Then transferring body scope text reflects each account
        """
        mock_standard_user(client, body_name)
        response = client.get(self.route_url)

        assert response.status_code == 200
        verify_scope_text(response.data, body_name)

    def test_browse_no_results_message_shows_heading_but_not_filter_help(
        self, client: FlaskClient, mock_all_access_user, mock_opensearch
    ):
        """
        Given the browse records page returns zero results with an active filter
        When the page loads with query parameters
        Then "No results found" is displayed, search help is hidden, and filter help is shown
        """
        mock_all_access_user(client)
        _set_empty_search_response(mock_opensearch)

        # Pass the query string parameters so the filter-based empty state triggers
        response = client.get(
            f"{self.route_url}?transferring_body_filter=&series_filter=TSTA+2&consignment_reference=&record_status=all&date_filter_field=date_last_modified&date_from_day=&date_from_month=&date_from_year=&date_to_day=&date_to_month=&date_to_year=#browse"
        )

        assert response.status_code == 200

        html = response.data.decode()
        soup = BeautifulSoup(html, "html.parser")

        bullet_list = soup.find("ul", class_="govuk-list--bullet")
        list_text = " ".join(bullet_list.get_text().split())

        assert "Try changing or removing search terms" not in list_text
        assert (
            "Try changing or removing one or more applied filters" in list_text
        )

    def test_browse_hides_consignment_details_for_dri_to_ayr_records(
        self, client: FlaskClient, mock_all_access_user, mock_opensearch
    ):
        """
        Given a record with a consignment reference starting with DRI-TO-AYR-
        When the browse records page loads with that consignment filter
        Then the consignment details are hidden for that record (since DRI-TO-AYR
            records are not real consignments so we do not want to confuse users
            and they do not have transfer complete dates)
        """
        file = FileFactory(
            consignment__ConsignmentReference="DRI-TO-AYR-9999",
            consignment__TransferCompleteDatetime=None,
        )

        mock_all_access_user(client)
        source = {
            **_browse_search_documents()[0]["_source"],
            "consignment_reference": "DRI-TO-AYR-9999",
            "consignment_transfer_complete_date": None,
        }
        mock_opensearch.side_effect = None
        mock_opensearch.return_value = _search_response(
            total=1, hits=[{"_source": source}]
        )

        response = client.get(
            f"{self.route_url}?consignment_reference={file.consignment.ConsignmentReference}"
        )

        assert response.status_code == 200

        html = response.data.decode()
        soup = BeautifulSoup(html, "html.parser")

        assert soup.select("tr.browse-record-row__row--consignment") == []
        assert "consignment DRI-TO-AYR-9999" not in html
