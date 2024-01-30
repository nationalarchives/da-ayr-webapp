from bs4 import BeautifulSoup
from flask import url_for
from flask.testing import FlaskClient

from app.tests.assertions import assert_contains_html
from app.tests.factories import BodyFactory


def test_standard_user_redirected_to_browse_transferring_body_when_accessing_browse(
    client: FlaskClient, mock_standard_user
):
    """
    Given a standard user accessing the browse page
    When they make a GET request
    Then they should be redirected to the transferring_body browse page for
        the body they have access to
    """
    body = BodyFactory()
    mock_standard_user(client, body.Name)

    response = client.get("/browse")

    assert response.status_code == 302
    assert response.headers["Location"] == url_for(
        "main.browse", transferring_body_id=body.BodyId
    )


def test_browse_get_view(client: FlaskClient, mock_superuser):
    """
    Given a superuser accessing the browse page
    When they make a GET request
    Then they should see the browse page content.
    """
    mock_superuser(client)

    response = client.get("/browse")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data


def test_browse_check_transferring_bodies_list_filled_for_super_user(
    client: FlaskClient, browse_files, mock_superuser
):
    """
    Given a superuser accessing the browse page
    When they make a GET request
    Then they should see the browse page content
    and transferring body dropdown will be filled with list of all transferring bodies available in database
    """
    mock_superuser(client)

    response = client.get("/browse")

    assert response.status_code == 200

    html = response.data.decode()

    expected_html = f"""
        <select class="govuk-select govuk-select__filters-form-transferring-body-select"
        id="transferring_body_filter" name="transferring_body_filter">
            <option value="all" selected>Choose one...</option>
            <option value="first_body">{browse_files[0].consignment.series.body.Name}</option>
            <option value="second_body">{browse_files[3].consignment.series.body.Name}</option>
            <option value="third_body">{browse_files[10].consignment.series.body.Name}</option>
            <option value="fourth_body">{browse_files[13].consignment.series.body.Name}</option>
            <option value="fifth_body">{browse_files[19].consignment.series.body.Name}</option>
            <option value="sixth_body">{browse_files[25].consignment.series.body.Name}</option>
        </select>
    """

    assert_contains_html(
        expected_html,
        html,
        "select",
        {
            "class": "govuk-select govuk-select__filters-form-transferring-body-select"
        },
    )


def test_browse_submit_search_query(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a POST request
    Then they should see results in content.
    """
    mock_superuser(client)

    query = "test"
    response = client.post("/browse", data={"query": query})

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"Records found 6" in response.data


def test_browse_get_without_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    Then they should see first five records on browse page content.
    """
    mock_superuser(client)

    response = client.get("/browse")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        [
            "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
            "'first_body', 'first_series', '07/02/2023', '3', '2', "
            "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
            "'second_body', 'second_series', '26/04/2023', '7', '2', "
            "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_transferring_body_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and select transferring body as filter from dropdown list
    Then they should see first two records matches to transferring body name on browse page content.
    """
    mock_superuser(client)
    transferring_body = "fi"
    response = client.get(
        "/browse?transferring_body_filter=" + transferring_body
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        [
            "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
            "'first_body', 'first_series', '07/02/2023', '3', '2'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_series_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and provide a series value as filter in text input field
    Then they should see first two records matches to series name on browse page content.
    """
    mock_superuser(client)
    series = "fi"
    response = client.get("/browse?series_filter=" + series)

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        [
            "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
            "'first_body', 'first_series', '07/02/2023', '3', '2'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_date_from_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and provide a date range with only date from value as filter in text input field
    Then they should see two records matches to date last transferred greater than or equal to date from filter value
    on browse page content.
    """
    mock_superuser(client)
    day = "01"
    month = "09"
    year = "2023"
    response = client.get(
        "/browse?date_from_day="
        + day
        + "&date_from_month="
        + month
        + "&date_from_year="
        + year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        [
            "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
            "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_date_to_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and provide a date range with only date to value as filter in text input field
    Then they should see two records matches to date last transferred less than or equal to date to filter value
    on browse page content.
    """
    mock_superuser(client)
    day = "26"
    month = "04"
    year = "2023"
    response = client.get(
        "/browse?date_to_day="
        + day
        + "&date_to_month="
        + month
        + "&date_to_year="
        + year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        [
            "'first_body', 'first_series', '07/02/2023', '3', '2', "
            "'second_body', 'second_series', '26/04/2023', '7', '2'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_date_from_and_date_to_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and provide a date range with date from and date to value as filter in text input field
    Then they should see three records matches to date last transferred between date from and date to filter value
    on browse page content.
    """
    mock_superuser(client)
    date_from_day = "01"
    date_from_month = "08"
    date_from_year = "2023"
    date_to_day = "31"
    date_to_month = "10"
    date_to_year = "2023"
    response = client.get(
        "/browse?date_from_day="
        + date_from_day
        + "&date_from_month="
        + date_from_month
        + "&date_from_year="
        + date_from_year
        + "&date_to_day="
        + date_to_day
        + "&date_to_month="
        + date_to_month
        + "&date_to_year="
        + date_to_year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        [
            "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
            "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
            "'sixth_body', 'sixth_series', '14/10/2023', '2', '1'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_transferring_body_and_series_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and select transferring body as filter from dropdown list
    and provide a series value as filter in text input field
    Then they should see one record matches to transferring body name and series name on browse page content.
    """
    mock_superuser(client)
    transferring_body = "fif"
    series = "fi"
    response = client.get(
        "/browse?transferring_body_filter="
        + transferring_body
        + "&series_filter="
        + series
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_transferring_body_and_date_from_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and select transferring body as filter from dropdown list
    and provide a date range with only date from value as filter in text input field
    Then they should see one record matches to transferring body name
    and date last transferred greater than or equal to date from filter value
    on browse page content.
    """
    mock_superuser(client)
    transferring_body = "fifth"
    day = "01"
    month = "09"
    year = "2023"
    response = client.get(
        "/browse?transferring_body_filter="
        + transferring_body
        + "&date_from_day="
        + day
        + "&date_from_month="
        + month
        + "&date_from_year="
        + year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_transferring_body_and_date_to_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and select transferring body as filter from dropdown list
    and provide a date range with only date to value as filter in text input field
    Then they should see one record matches to transferring body name
    and date last transferred less than or equal to date to filter value
    on browse page content.
    """
    mock_superuser(client)
    transferring_body = "fifth"
    day = "21"
    month = "09"
    year = "2023"
    response = client.get(
        "/browse?transferring_body_filter="
        + transferring_body
        + "&date_to_day="
        + day
        + "&date_to_month="
        + month
        + "&date_to_year="
        + year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_transferring_body_and_date_from_and_date_to_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and select transferring body as filter from dropdown list
    and provide a date range with date from and date to value as filter in text input field
    Then they should see two records matches to transferring body name
    and date last transferred between date from and date to filter value
    on browse page content.
    """
    mock_superuser(client)
    transferring_body = "f"
    date_from_day = "01"
    date_from_month = "08"
    date_from_year = "2023"
    date_to_day = "31"
    date_to_month = "10"
    date_to_year = "2023"
    response = client.get(
        "/browse?transferring_body_filter="
        + transferring_body
        + "&date_from_day="
        + date_from_day
        + "&date_from_month="
        + date_from_month
        + "&date_from_year="
        + date_from_year
        + "&date_to_day="
        + date_to_day
        + "&date_to_month="
        + date_to_month
        + "&date_to_year="
        + date_to_year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        [
            "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
            "'fourth_body', 'fourth_series', '03/08/2023', '6', '2'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_series_and_date_from_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and provide a series value as filter in text input field
    and provide a date range with only date from value as filter in text input field
    Then they should see one record matches to series name
    and date last transferred greater than or equal to date from filter value
    on browse page content.
    """
    mock_superuser(client)
    series = "fifth"
    day = "01"
    month = "09"
    year = "2023"
    response = client.get(
        "/browse?series_filter="
        + series
        + "&date_from_day="
        + day
        + "&date_from_month="
        + month
        + "&date_from_year="
        + year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_series_and_date_to_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and provide a series value as filter in text input field
    and provide a date range with only date to value as filter in text input field
    Then they should see one record matches to series name
    and date last transferred less than or equal to date to filter value
    on browse page content.
    """
    mock_superuser(client)
    series = "fifth"
    day = "21"
    month = "09"
    year = "2023"
    response = client.get(
        "/browse?series_filter="
        + series
        + "&date_to_day="
        + day
        + "&date_to_month="
        + month
        + "&date_to_year="
        + year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_series_and_date_from_and_date_to_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and provide a series value as filter in text input field
    and provide a date range with date from and date to value as filter in text input field
    Then they should see one record matches to series name
    and date last transferred between date from and date to filter value
    on browse page content.
    """
    mock_superuser(client)
    series = "fou"
    date_from_day = "01"
    date_from_month = "08"
    date_from_year = "2023"
    date_to_day = "31"
    date_to_month = "10"
    date_to_year = "2023"
    response = client.get(
        "/browse?series_filter="
        + series
        + "&date_from_day="
        + date_from_day
        + "&date_from_month="
        + date_from_month
        + "&date_from_year="
        + date_from_year
        + "&date_to_day="
        + date_to_day
        + "&date_to_month="
        + date_to_month
        + "&date_to_year="
        + date_to_year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        ["'fourth_body', 'fourth_series', '03/08/2023', '6', '2'"],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_transferring_body_and_series_and_date_from_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and select transferring body as filter from dropdown list
    and provide a series value as filter in text input field
    and provide a date range with only date from value as filter in text input field
    Then they should see one record matches to transferring body name, series_name
    and date last transferred greater than or equal to date from filter value
    on browse page content.
    """
    mock_superuser(client)
    transferring_body = "fi"
    series = "fifth"
    day = "01"
    month = "09"
    year = "2023"
    response = client.get(
        "/browse?transferring_body_filter="
        + transferring_body
        + "&series_filter="
        + series
        + "&date_from_day="
        + day
        + "&date_from_month="
        + month
        + "&date_from_year="
        + year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_transferring_body_and_series_and_date_to_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and select transferring body as filter from dropdown list
    and provide a series value as filter in text input field
    and provide a date range with only date to value as filter in text input field
    Then they should see one record matches to transferring body name, series_name
    and date last transferred less than or equal to date to filter value
    on browse page content.
    """
    mock_superuser(client)
    transferring_body = "fi"
    series = "fifth"
    day = "21"
    month = "09"
    year = "2023"
    response = client.get(
        "/browse?transferring_body_filter="
        + transferring_body
        + "&series_filter="
        + series
        + "&date_to_day="
        + day
        + "&date_to_month="
        + month
        + "&date_to_year="
        + year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        ["'fifth_body', 'fifth_series', '21/09/2023', '6', '2'"],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_get_with_transferring_body_and_series_and_date_from_and_date_to_filter(
    client: FlaskClient, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    and select transferring body as filter from dropdown list
    and provide a series value as filter in text input field
    and provide a date range with date from and date to value as filter in text input field
    Then they should see one record matches to transferring body name, series_name
    and date last transferred between date from and date to filter value
    on browse page content.
    """
    mock_superuser(client)
    transferring_body = "fo"
    series = "fou"
    date_from_day = "01"
    date_from_month = "08"
    date_from_year = "2023"
    date_to_day = "31"
    date_to_month = "10"
    date_to_year = "2023"
    response = client.get(
        "/browse?transferring_body_filter="
        + transferring_body
        + "&series_filter="
        + series
        + "&date_from_day="
        + date_from_day
        + "&date_from_month="
        + date_from_month
        + "&date_from_year="
        + date_from_year
        + "&date_to_day="
        + date_to_day
        + "&date_to_month="
        + date_to_month
        + "&date_to_year="
        + date_to_year
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        ["'fourth_body', 'fourth_series', '03/08/2023', '6', '2'"],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_display_first_page(
    client: FlaskClient, app, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    Then they should see first page with five records on browse page content
    (excluding previous and incl. next page option).
    """
    mock_superuser(client)

    app.config["DEFAULT_PAGE_SIZE"] = 2

    response = client.get("/browse?page=1")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data
    assert b'aria-label="Page 1"' in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")
    previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
    next_option = soup.find("div", {"class": "govuk-pagination__next"})

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        [
            "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
            "'first_body', 'first_series', '07/02/2023', '3', '2'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]
    assert not previous_option
    assert next_option.text.replace("\n", "").strip("") == "Nextpage"


def test_browse_display_middle_page(
    client: FlaskClient, app, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    Then they should see first page with five records on browse page content (incl. previous and next page options).
    """
    mock_superuser(client)

    app.config["DEFAULT_PAGE_SIZE"] = 2

    response = client.get("/browse?page=2")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data
    assert b'aria-label="Page 2"' in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")
    page_options = soup.find_all("span", class_="govuk-pagination__link-title")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        [
            "'fourth_body', 'fourth_series', '03/08/2023', '6', '2', "
            "'second_body', 'second_series', '26/04/2023', '7', '2'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]
    assert (
        " ".join(page_options[0].text.replace("\n", "").split())
        == "Previouspage"
    )
    assert (
        " ".join(page_options[1].text.replace("\n", "").split()) == "Nextpage"
    )


def test_browse_display_last_page(
    client: FlaskClient, app, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    Then they should see last page with n records on browse page content
    (incl. previous and excluding next page option).
    """
    mock_superuser(client)

    app.config["DEFAULT_PAGE_SIZE"] = 2

    response = client.get("/browse?page=3")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data
    assert b'aria-label="Page 3"' in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")
    previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
    next_option = soup.find("div", {"class": "govuk-pagination__next"})

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        [
            "'sixth_body', 'sixth_series', '14/10/2023', '2', '1', "
            "'third_body', 'third_series', '17/06/2023', '3', '2'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]
    assert (
        " ".join(previous_option.text.replace("\n", "").split())
        == "Previouspage"
    )
    assert not next_option


def test_browse_display_multiple_pages(
    client: FlaskClient, app, mock_superuser, browse_files
):
    """
    Given a superuser accessing the browse page
    When they make a GET request with page as a query string parameter
    Then they should see first page with five records on browse page content (incl. previous and next page options).
    """
    mock_superuser(client)

    app.config["DEFAULT_PAGE_SIZE"] = 2

    response = client.get("/browse?page=1")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Everything available to you" in response.data
    assert b'aria-label="Page 1"' in response.data
    assert b'aria-label="Page 2"' in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")
    # page_options = soup.find_all("span", class_="govuk-pagination__link-title")
    previous_option = soup.find("div", {"class": "govuk-pagination__prev"})
    next_option = soup.find("div", {"class": "govuk-pagination__next"})
    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        [
            "'fifth_body', 'fifth_series', '21/09/2023', '6', '2', "
            "'first_body', 'first_series', '07/02/2023', '3', '2'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]
    assert not previous_option
    assert next_option.text.replace("\n", "").strip("") == "Nextpage"


def test_browse_transferring_body(
    client: FlaskClient, mock_standard_user, browse_files
):
    """
    Given a user accessing the browse page
    When they make a GET request with a transferring body id
    Then they should see results based on transferring body filter on browse page content.
    """
    transferring_body_id = browse_files[0].consignment.series.body.BodyId

    mock_standard_user(client, browse_files[0].consignment.series.body.Name)

    response = client.get(
        f"/browse?transferring_body_id={transferring_body_id}"
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Records found 1" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Last record transferred",
            "Records held",
            "Consignments within series",
        ],
        ["'first_body', 'first_series', '07/02/2023', '3', '2'"],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_transferring_body_breadcrumb(
    client: FlaskClient, mock_standard_user, browse_files
):
    """
    Given a user accessing the browse page
    When they make a GET request with a transferring body id
    Then they should see results based on transferring body filter on browse page content.
    And breadcrumb should show 'Everything' > transferring body name
    """
    transferring_body_id = browse_files[0].consignment.series.body.BodyId

    mock_standard_user(client, browse_files[0].consignment.series.body.Name)

    response = client.get(
        f"/browse?transferring_body_id={transferring_body_id}"
    )

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Records found 1" in response.data

    html = response.data.decode()

    expected_breadcrumbs_html = f"""
    <div class="govuk-breadcrumbs">
        <ol class="govuk-breadcrumbs__list">
            <li class="govuk-breadcrumbs__list-item">
            <a class="govuk-breadcrumbs__link--record" href="/browse">Everything</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
            <p class="govuk-breadcrumbs__link--record">{browse_files[0].consignment.series.body.Name}</p>
            </li>
        </ol>
    </div>
    """

    assert_contains_html(
        expected_breadcrumbs_html,
        html,
        "div",
        {"class": "govuk-breadcrumbs"},
    )


def test_browse_series(client: FlaskClient, mock_standard_user, browse_files):
    """
    Given a user accessing the browse page
    When they make a GET request with a series id
    Then they should see results based on series filter on browse page content.
    """
    series_id = browse_files[0].consignment.series.SeriesId

    mock_standard_user(client, browse_files[0].consignment.series.body.Name)

    response = client.get(f"/browse?series_id={series_id}")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Records found 2" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Transferring body",
            "Series",
            "Consignment transferred",
            "Records in consignment",
            "Consignment reference",
        ],
        [
            "'first_body', 'first_series', '13/01/2023', '1', 'TDR-2023-FI1', "
            "'first_body', 'first_series', '07/02/2023', '2', 'TDR-2023-SE2'"
        ],
    ]

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_series_breadcrumb(
    client: FlaskClient, mock_standard_user, browse_files
):
    """
    Given a user accessing the browse page
    When they make a GET request with a series id
    Then they should see results based on series filter on browse page content.
    And breadcrumb should show 'Everything' > transferring body name > series name
    """
    series_id = browse_files[0].consignment.series.SeriesId

    mock_standard_user(client, browse_files[0].consignment.series.body.Name)

    response = client.get(f"/browse?series_id={series_id}")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data
    assert b"Records found 2" in response.data

    html = response.data.decode()

    expected_breadcrumbs_html = f"""
    <div class="govuk-breadcrumbs">
        <ol class="govuk-breadcrumbs__list">
            <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record" href="/browse">Everything</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record"
                    href="/browse?transferring_body_id={browse_files[0].consignment.series.body.BodyId}">{browse_files[0].consignment.series.body.Name}</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
                <p class="govuk-breadcrumbs__link--record">{browse_files[0].consignment.series.Name}</p>
            </li>
        </ol>
    </div>
    """

    assert_contains_html(
        expected_breadcrumbs_html,
        html,
        "div",
        {"class": "govuk-breadcrumbs"},
    )


def test_browse_consignment(
    client: FlaskClient, mock_standard_user, browse_consignment_files
):
    """
    Given a user accessing the browse page
    When they make a GET request with a consignment id
    Then they should see results based on consignment filter on browse page content.
    """
    consignment_id = browse_consignment_files[0].consignment.ConsignmentId

    mock_standard_user(
        client, browse_consignment_files[0].consignment.series.body.Name
    )

    response = client.get(f"/browse?consignment_id={consignment_id}")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data

    soup = BeautifulSoup(response.data, "html.parser")
    table = soup.find("table")
    headers = table.find_all("th")
    rows = table.find_all("td")

    expected_results_table = [
        [
            "Last modified",
            "Filename",
            "Status",
            "Closure start date",
            "Closure period",
        ],
        [
            "'20/05/2023', 'fifth_file.doc', 'Open', '-', '-', "
            "'25/02/2023', 'first_file.docx', 'Closed', '25/02/2023', '10 years', "
            "'12/04/2023', 'fourth_file.xls', 'Closed', '12/04/2023', '70 years', "
            "'15/01/2023', 'second_file.ppt', 'Open', '-', '-', "
            "'10/03/2023', 'third_file.docx', 'Closed', '10/03/2023', '25 years'"
        ],
    ]

    assert len(rows) == 25

    assert [
        header.text.replace("\n", " ").strip(" ") for header in headers
    ] == expected_results_table[0]
    row_data = ""
    for row_index, row in enumerate(rows):
        row_data = row_data + "'" + row.text.replace("\n", " ").strip(" ") + "'"
        if row_index < len(rows) - 1:
            row_data = row_data + ", "
    assert [row_data] == expected_results_table[1]


def test_browse_consignment_breadcrumb(
    client: FlaskClient, mock_standard_user, browse_consignment_files
):
    """
    Given a user accessing the browse page
    When they make a GET request with a consignment id
    Then they should see results based on consignment filter on browse page content.
    And breadcrumb should show 'Everything' > transferring body name > series name > consignment reference
    """
    consignment_id = browse_consignment_files[0].consignment.ConsignmentId

    mock_standard_user(
        client, browse_consignment_files[0].consignment.series.body.Name
    )

    response = client.get(f"/browse?consignment_id={consignment_id}")

    assert response.status_code == 200
    assert b"Search for digital records" in response.data
    assert b"You are viewing" in response.data

    html = response.data.decode()
    consignment_reference = browse_consignment_files[
        0
    ].consignment.ConsignmentReference
    expected_breadcrumbs_html = f"""
    <div class="govuk-breadcrumbs">
        <ol class="govuk-breadcrumbs__list">
            <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record" href="/browse">Everything</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record"
                    href="/browse?transferring_body_id={browse_consignment_files[0].consignment.series.body.BodyId}">{browse_consignment_files[0].consignment.series.body.Name}</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
                <a class="govuk-breadcrumbs__link--record"
                    href="/browse?series_id={browse_consignment_files[0].consignment.series.SeriesId}">{browse_consignment_files[0].consignment.series.Name}</a>
            </li>
            <li class="govuk-breadcrumbs__list-item">
                <p class="govuk-breadcrumbs__link--record">{consignment_reference}</p>
            </li>
        </ol>
    </div>
    """

    assert_contains_html(
        expected_breadcrumbs_html,
        html,
        "div",
        {"class": "govuk-breadcrumbs"},
    )
