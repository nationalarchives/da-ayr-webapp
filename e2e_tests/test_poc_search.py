from playwright.sync_api import Page, expect


def test_poc_search_end_to_end(authenticated_page: Page):
    """
    Given a user on the search page
    When they interact with the search form and submit a query
    Then the table should contain the expected headers and entries.
    """
    authenticated_page.goto("/poc-search")

    expect(authenticated_page.get_by_text("Search design PoC")).to_be_visible()
    expect(
        authenticated_page.locator("text=Search for digital records")
    ).to_be_visible()

    # Interact with the search form and submit a query
    authenticated_page.fill("#searchInput", "Test description")
    expect(authenticated_page.locator("#searchInput")).to_have_value(
        "Test description"
    )
    authenticated_page.get_by_role("button").get_by_text("Search").click()

    expect(authenticated_page.locator("#searchInput")).not_to_have_value(
        "Test description"
    )

    table = authenticated_page.locator("table")
    # Use JavaScript to extract the text of header elements (th) within the table
    header_texts = table.evaluate(
        '(table) => Array.from(table.querySelectorAll("th")).map(th => th.textContent)'
    )
    # List of expected header values
    expected_headers = [
        "Transferring Body",
        "Series",
        "Consignment Reference",
        "File Name",
    ]
    for expected_header in expected_headers:
        assert expected_header in header_texts

    # Use JavaScript to extract the text of table cell elements (td) within the table
    cell_texts = table.evaluate(
        '(table) => Array.from(table.querySelectorAll("td")).map(td => td.textContent)'
    )

    expected_entries = [
        "Testing A",
        "TSTA 1",
        "TDR-2023-H2QS",
        "file-a1.txt",
        "Testing A",
        "TSTA 1",
        "TDR-2023-H2QS",
        "file-a2.txt",
    ]
    assert expected_entries == cell_texts
