from unittest.mock import patch

from bs4 import BeautifulSoup
from flask.testing import FlaskClient
from moto import mock_aws

from app.tests.factories import FileFactory


@mock_aws
@patch("keycloak.KeycloakOpenID")
def test_main_headings_h1_precedes_h2(
    mock_keycloak_openid, app, client: FlaskClient, mock_all_access_user
):
    """
    Verify that only one H1 is present on each page and if any H2 headings are present on a page that
    a H1 heading exists and appears before them in document order.
    """
    bucket_name = "sub_bucket"
    app.config["RECORD_BUCKET_NAME"] = bucket_name
    file = FileFactory()

    mock_all_access_user(client)

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
        f"/browse/record/{file.FileId}",
    ]

    for route in routes:
        response = client.get(route)

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
