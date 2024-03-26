from bs4 import BeautifulSoup
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html


class TestRoutes:
    def test_cookies_get(self, app, client: FlaskClient):
        """
        Given a standard user accessing the cookies page
        When they make a GET request
        Then they should see cookies page content
        """

        response = client.get("/cookies")

        html = response.data.decode()

        expected_html = """
<table class="govuk-table" id="tbl_cookies">
        <thead class="govuk-table__head">
            <tr class="govuk-table__row">
                <th scope="col" class="govuk-table__header govuk-!-width-one-third">Cookie name</th>
                <th scope="col" class="govuk-table__header govuk-!-width-one-third">What it does/typical content</th>
                <th scope="col" class="govuk-table__header govuk-!-width-one-third">Duration</th>
            </tr>
        </thead>
        <tbody class="govuk-table__body">
            <tr class="govuk-table__row">
                <td class="govuk-table__cell"><strong>session</strong></td>
                <td class="govuk-table__cell">A cookie that holds information for authorisation purpose</td>
                <td class="govuk-table__cell">Expires when you exit the browser</td>
            </tr>
        </tbody>
    </table>
    """

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

        assert_contains_html(
            expected_html,
            html,
            "table",
            {"class": "govuk-table"},
        )
