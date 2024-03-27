from bs4 import BeautifulSoup
from flask.testing import FlaskClient


def verify_cookies_header_row(data):
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")

    expected_row = (
        [
            "Cookie name",
            "What it does/typical content",
            "Duration",
        ],
    )
    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_row[0]


def verify_cookies_data_rows(data, expected_rows):
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


class TestRoutes:
    def test_cookies_get(self, app, client: FlaskClient):
        """
        Given a standard user accessing the cookies page
        When they make a GET request
        Then they should see cookies page content
        """
        response = client.get("/cookies")

        assert response.status_code == 200
        assert b"Cookies" in response.data
        assert b"Why do we use cookies?" in response.data
        assert b"Essential cookies" in response.data

        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.title
        assert (
            title_tag.string
            == f"Cookies – {app.config['SERVICE_NAME']} – GOV.UK"
        )

        expected_rows = [
            [
                "'session', 'A cookie that holds information for authorisation purpose', 'Expires when you exit the "
                "browser', 'KEYCLOAK_SESSION_LEGACY', 'A cookie set by the authorisation component of the service that "
                "keeps track of the session as you use the service', 'Expires when you exit the browser', "
                "'KEYCLOAK_SESSION', 'A cookie set by the authorisation component of the service that keeps track of "
                "the session as you use the service', 'Expires when you exit the browser', 'KEYCLOAK_IDENTITY_LEGACY', "
                "'A cookie set by the authorisation component of the service that keeps track of elements related to "
                "your identity as you use the service', 'Expires when you exit the browser', 'KEYCLOAK_IDENTITY', "
                "'A cookie set by the authorisation component of the service that keeps track of elements related to "
                "your identity as you use the service', 'Expires when you exit the browser', 'AUTH_SESSION_ID_LEGACY', "
                "'A cookie set by the authorisation component of the service that keeps track of the session identity "
                "as you use the service', 'Expires when you exit the browser', 'AUTH_SESSION_ID', 'A cookie set by the "
                "authorisation component of the service that keeps track of the session identity as you use the "
                "service', 'Expires when you exit the browser', 'KC_RESTART', 'A cookie set by the authorisation "
                "component of the service that keeps track of the session as you use the service', 'Expires when you "
                "exit the browser', 'KC_AUTH_STATE', 'A cookie set by the authorisation component of the service that "
                "keeps track of the session as you use the service', 'Expires when you exit the browser'"
            ]
        ]

        verify_cookies_header_row(response.data)
        verify_cookies_data_rows(response.data, expected_rows)
