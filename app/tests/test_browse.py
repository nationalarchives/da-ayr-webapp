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


def test_browse_series(client: FlaskClient):
    """
    Given a user accessing the search page
    When they make a GET request with a series id
    Then they should see the series page content.
    """
    files = create_two_test_files()
    file = files[0]
    series_id = file.file_consignments.SeriesId

    response = client.get(f"/browse?series_id={series_id}")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"Records found 1" in response.data
    assert b"test body1" in response.data


def test_browse_consignment(client: FlaskClient):
    """
    Given a user accessing the search page
    When they make a GET request with a consignment id
    Then they should see the consignment page content.
    """
    files = create_two_test_files()
    file = files[0]
    consignment_id = file.file_consignments.ConsignmentId

    response = client.get(f"/browse?consignment_id={consignment_id}")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"Records found 2" in response.data


def test_browse_transferring_body(client: FlaskClient):
    """
    Given a user accessing the search page
    When they make a GET request with a transferring body id
    Then they should see the transferring body page content.
    """

    files = create_two_test_files()
    file = files[0]
    transferring_body_id = file.file_consignments.consignment_bodies.BodyId

    response = client.get(
        f"/browse?transferring_body_id={transferring_body_id}"
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"Records found 1" in response.data
    assert b"test body1" in response.data
