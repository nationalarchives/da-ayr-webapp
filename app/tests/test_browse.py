from flask.testing import FlaskClient

from app.tests.mock_database import create_two_test_files


def test_load_browse_page(client: FlaskClient):
    """
    Given a user accessing the search page
    When they make a GET request
    Then they should see the search form and page content.
    """
    response = client.get("/browse")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data


def test_submit_search_query(client: FlaskClient):
    """
    Given a user accessing the search page
    When they make a POST request
    Then they should see the search form and page content.
    """
    create_two_test_files()

    response = client.get("/browse")
    query = "test"
    response = client.post("/browse", data={"query": query})

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"Records found 2" in response.data
    assert b"test series1" in response.data
    assert b"test series2" in response.data
