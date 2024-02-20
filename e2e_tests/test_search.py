from playwright.sync_api import Page, expect


def test_search_end_to_end(authenticated_page: Page):
    """
    Given a user on the search page
    When they interact with the search form and submit a query
    Then the table should contain the expected headers and entries.
    """
    authenticated_page.goto("/search")

    expect(
        authenticated_page.get_by_role("heading").get_by_text(
            "Search", exact=True
        )
    ).to_be_visible()
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
        "Transferring body",
        "Series",
        "Consignment reference",
        "File name",
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


def test_pagination_available(authenticated_page: Page):
    authenticated_page.goto("/search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )


def test_pagination_check_only_one_page_returned(authenticated_page: Page):
    authenticated_page.goto("/search")
    authenticated_page.fill("#searchInput", "Test description")
    expect(authenticated_page.locator("#searchInput")).to_have_value(
        "Test description"
    )
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    pagination_element = authenticated_page.query_selector(
        "nav.govuk-pagination"
    )
    assert not pagination_element


def test_pagination_get_first_page(authenticated_page: Page):
    authenticated_page.goto("/search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )
    url = "/search?page=1&query=testing+a"
    assert (
        authenticated_page.locator(
            ".govuk-pagination__link"
        ).first.get_attribute("href")
        == url
    )
    links = authenticated_page.locator(".govuk-pagination__link-title").all()
    assert links[0].inner_text() == "Nextpage"
    expect(authenticated_page.get_by_text("Records found 5"))
    rows = authenticated_page.locator(".govuk-table__row").all()
    assert len(rows) == 6  # including header row


def test_pagination_get_previous_page(authenticated_page: Page):
    authenticated_page.goto("/search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    page_links = authenticated_page.locator(".govuk-pagination__link").all()
    authenticated_page.get_by_role("link").get_by_text(
        page_links[1].inner_text()
    ).click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )
    links = authenticated_page.locator(".govuk-pagination__link-title").all()
    assert links[0].inner_text() == "Previouspage"


def test_pagination_get_next_page(authenticated_page: Page):
    authenticated_page.goto("/search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )
    url = "/search?page=1&query=testing+a"
    assert (
        authenticated_page.locator(
            ".govuk-pagination__link"
        ).first.get_attribute("href")
        == url
    )
    authenticated_page.get_by_role("link").get_by_text(" 2 ").click()
    links = authenticated_page.locator(".govuk-pagination__link-title").all()
    assert links[0].inner_text() == "Previouspage"
    if len(links) > 1:
        assert links[1].inner_text() == "Nextpage"


def test_pagination_get_ellipses_page(authenticated_page: Page):
    authenticated_page.goto("/search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )
    page_links = authenticated_page.locator(".govuk-pagination__link").all()
    last_page = page_links[len(page_links) - 1].inner_text()
    assert page_links[0].inner_text() == "1"
    assert page_links[1].inner_text() == "2"
    assert page_links[3].inner_text() == last_page
    ellipsis_link = authenticated_page.locator(
        ".govuk-pagination__item--ellipses"
    ).all()
    assert ellipsis_link[0].inner_text() == "…"
    links = authenticated_page.locator(".govuk-pagination__link-title").all()
    assert links[0].inner_text() == "Nextpage"


def test_pagination_click_previous_link(authenticated_page: Page):
    authenticated_page.goto("/search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )

    authenticated_page.get_by_role("link").get_by_text(" 2 ").click()

    links = authenticated_page.locator(".govuk-pagination__link-title").all()
    assert links[0].inner_text() == "Previouspage"

    url = "/search?page=1&query=testing+a"
    authenticated_page.expect_response(url)


def test_pagination_click_next_link(authenticated_page: Page):
    authenticated_page.goto("/search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )

    authenticated_page.get_by_role("link").get_by_text(" 1 ").click()

    links = authenticated_page.locator(".govuk-pagination__link-title").all()
    assert links[0].inner_text() == "Nextpage"

    url = "/search?page=2&query=testing+a"
    authenticated_page.expect_response(url)


def test_pagination_get_last_page(authenticated_page: Page):
    authenticated_page.goto("/search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )
    page_links = authenticated_page.locator(".govuk-pagination__link").all()
    last_page = page_links[len(page_links) - 1].inner_text()
    authenticated_page.get_by_role("link").get_by_text(last_page).click()
    links = authenticated_page.locator(".govuk-pagination__link-title").all()
    assert links[0].inner_text() == "Previouspage"
