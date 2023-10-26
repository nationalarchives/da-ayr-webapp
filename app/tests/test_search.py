from flask.testing import FlaskClient


def test_poc_search_get(client: FlaskClient):
    """
    Given a user accessing the search page
    When they make a GET request
    Then they should see the search form and page content.
    """
    response = client.get("/poc-search-view", follow_redirects=True)

    assert response.status_code == 200
    assert b"Search design PoC" in response.data
    assert b"Search for digital records" in response.data
    assert b"Search" in response.data
