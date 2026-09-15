from unittest.mock import patch

from bs4 import BeautifulSoup
from flask.testing import FlaskClient
from moto import mock_aws

from app.tests.factories import FileFactory

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


@mock_aws
@patch("keycloak.KeycloakOpenID")
@patch("app.main.routes.setup_opensearch")
def test_main_headings_h1_precedes_h2(
    mock_setup_opensearch,
    mock_keycloak_openid,
    app,
    client: FlaskClient,
    mock_all_access_user,
):
    """
    Verify that only one H1 is present on each page and if any H2 headings are present on a page that
    a H1 heading exists and appears before them in document order.
    """
    bucket_name = "sub_bucket"
    app.config["RECORD_BUCKET_NAME"] = bucket_name
    file = FileFactory()

    mock_all_access_user(client)

    mock_setup_opensearch.return_value = MockOpenSearch(
        search_return_value=OS_MOCK_RESULTS
    )

    routes = [
        "/",
        "/sign-in",
        "/signed-out",
        "/accessibility",
        "/cookies",
        "/privacy",
        "/how-to-use-this-service",
        "/terms-of-use",
        "/browse",
        "/search/results?query=test&search_area=everywhere&sort=file_name",
        f"/browse/record/{file.FileId}",
        f"/record/{file.FileId}",
    ]

    for route in routes:
        response = client.get(route, follow_redirects=True)

        if response.status_code != 200:
            continue

        soup = BeautifulSoup(response.data.decode(), "html.parser")
        headings = soup.find_all(["h1", "h2"])

        if not headings:
            continue

        h1_tags = [h for h in headings if h.name == "h1"]

        assert len(h1_tags) == 1, (
            f"Route '{route}' failed: Expected exactly 1 H1 heading, "
            f"but found {len(h1_tags)}."
        )

        if any(h.name == "h2" for h in headings):
            assert len(h1_tags) >= 1, (
                f"Route '{route}' failed: H2 headings are present, "
                f"but no H1 heading was found."
            )

            first_heading = headings[0]
            assert first_heading.name == "h1", (
                f"Route '{route}' failed hierarchy check: "
                f"An <{first_heading.name}> appears before any H1 main title."
            )
