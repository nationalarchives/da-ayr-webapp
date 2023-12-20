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
    authenticated_page.goto("/poc-search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )
    assert (
        authenticated_page.locator(
            ".govuk-pagination__link-title"
        ).first.inner_text()
        == "Next page"
    )


def test_pagination_check_only_one_page_returned(authenticated_page: Page):
    authenticated_page.goto("/poc-search")
    authenticated_page.is_visible("text='Pagination'")
    authenticated_page.fill("#searchInput", "Test description")
    expect(authenticated_page.locator("#searchInput")).to_have_value(
        "Test description"
    )
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )
    assert (
        authenticated_page.locator(".govuk-pagination__prev").first.inner_text()
        == ""
    )
    assert (
        authenticated_page.locator(".govuk-pagination__next").first.inner_text()
        == ""
    )


def test_pagination_get_first_page(authenticated_page: Page):
    authenticated_page.goto("/poc-search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )
    url = "/poc-search?page=1&query=testing+a"
    assert (
        authenticated_page.locator(
            ".govuk-pagination__link"
        ).first.get_attribute("href")
        == url
    )
    links = authenticated_page.locator(".govuk-pagination__link-title").all()
    assert links[0].inner_text() == "Next page"
    expect(authenticated_page.get_by_text("5 record(s) found"))
    rows = authenticated_page.locator(".govuk-table__row").all()
    assert len(rows) == 6  # including header row


def test_pagination_get_previous_page(authenticated_page: Page):
    authenticated_page.goto("/poc-search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    page_links = authenticated_page.locator(".govuk-pagination__link").all()
    if len(page_links) > 1:
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
    assert links[0].inner_text() == "Previous page"


def test_pagination_click_previous_link(authenticated_page: Page):
    authenticated_page.goto("/poc-search")
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
    assert links[0].inner_text() == "Previous page"

    print(authenticated_page.url)
    url = "/poc-search?page=1&query=testing+a"
    authenticated_page.expect_response(url)
    # expect(authenticated_page.expect_response(url))


def test_pagination_get_next_page(authenticated_page: Page):
    authenticated_page.goto("/poc-search")
    authenticated_page.fill("#searchInput", "Testing A")
    authenticated_page.get_by_role("button").get_by_text("Search").click()
    assert (
        authenticated_page.locator(".govuk-pagination").first.get_attribute(
            "aria-label"
        )
        == "Pagination"
    )
    url = "/poc-search?page=1&query=testing+a"
    assert (
        authenticated_page.locator(
            ".govuk-pagination__link"
        ).first.get_attribute("href")
        == url
    )
    authenticated_page.get_by_role("link").get_by_text(" 2 ").click()
    links = authenticated_page.locator(".govuk-pagination__link-title").all()
    assert links[0].inner_text() == "Previous page"
    if len(links) > 1:
        assert links[1].inner_text() == "Next page"


def test_pagination_get_ellipses_page(authenticated_page: Page):
    authenticated_page.goto("/poc-search")
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
    assert ellipsis_link[0].inner_text() == "⋯"
    links = authenticated_page.locator(".govuk-pagination__link-title").all()
    assert links[0].inner_text() == "Next page"


def test_pagination_get_last_page(authenticated_page: Page):
    authenticated_page.goto("/poc-search")
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
    assert links[0].inner_text() == "Previous page"
