import pytest
from playwright.sync_api import Page, expect


@pytest.fixture
def page_context(page):
    page.goto("http://localhost:5000/poc-search-view")
    return page


def test_poc_search_end_to_end(page_context):
    """
    Given a user on the search page
    When they interact with the search form and submit a query
    Then the table should contain the expected headers and entries.
    """
    page: Page = page_context

    expect(page.get_by_text("Search design PoC")).to_be_visible()
    expect(page.locator("text=Search for digital records")).to_be_visible()

    # Interact with the search form and submit a query
    page.fill("#searchInput", "Test description")
    expect(page.locator("#searchInput")).to_have_value("Test description")
    page.get_by_role("button").get_by_text("Search").click()

    expect(page.locator("#searchInput")).not_to_have_value("Test description")

    table = page.locator("table")
    # Use JavaScript to extract the text of header elements (th) within the table
    header_texts = table.evaluate(
        '(table) => Array.from(table.querySelectorAll("th")).map(th => th.textContent)'
    )
    # List of expected header values
    expected_headers = [
        "Title",
        "Description",
        "Last modified",
        "Status",
        "Closure period (years)",
    ]
    for expected_header in expected_headers:
        assert expected_header in header_texts

    # Use JavaScript to extract the text of table cell elements (td) within the table
    cell_texts = table.evaluate(
        '(table) => Array.from(table.querySelectorAll("td")).map(td => td.textContent)'
    )
    # List of expected entry values
    expected_entries = [
        "",
        "",
        "",
        "",
        "",
        "file-a1.txt",
        "Test description",
        "2023-02-27T12:28:08",
        "Public Record(s)",
        "50",
        "file-a2.txt",
        "Test description 2",
        "2023-02-27T12:28:13",
        "Public Record(s)",
        "100",
    ]
    for expected_entry in expected_entries:
        assert expected_entry in cell_texts
