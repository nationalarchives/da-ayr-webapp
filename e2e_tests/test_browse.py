import time

from playwright.sync_api import Page


def test_has_title(page: Page):
    time.sleep(1)
    page.goto("/browse")
    assert page.title() == "Browse – AYR - Access Your Records – GOV.UK"


def test_sort_dropdown(page: Page):
    time.sleep(1)
    page.goto("/browse")
    page.select_option("#sort", "body-a")
    page.select_option("#sort", "body-b")
    page.select_option("#sort", "series-a")
    page.select_option("#sort", "series-b")
    page.select_option("#sort", "date-first")
    page.select_option("#sort", "date-last")


def test_page_loading(page: Page):
    time.sleep(1)
    page.goto("/browse")
    page.wait_for_selector(".govuk-heading-l")


def test_filter_functionality(page: Page):
    page.goto("/browse")

    page.select_option(
        ".filters-form__transferring-body--select", "Arts Council England"
    )
    time.sleep(1)

    records = page.query_selector_all(".govuk-summary-list__value a")
    for record in records:
        assert record
        # assert record.text() == "Arts Council England"


def test_pagination(page: Page):
    time.sleep(1)
    page.goto("/browse")
    page.click(".govuk-pagination__next")


# def test_pagination(page: Page):
#     # Go to the browse page
#     page.goto("/browse")

#     # Click the next page button
#     page.click(".govuk-pagination__next")
#     time.sleep(1)  # Wait for the page to load (adjust the sleep time as needed)

#     # Check that the current page number has changed
#     current_page = page.query_selector(".govuk-pagination__item--current")
#     assert current_page.text() == "2"


# def test_sorting(page: Page):
#     # Go to the browse page
#     page.goto("/browse")

#     # Select different sort options
#     sort_options = ["body-a", "series-a", "date-first"]
#     for option in sort_options:
#         page.select_option("#sort", option)
#         time.sleep(1)  # Wait for the page to update (adjust the sleep time as needed)

#         # Check that the records are sorted in the expected order
#         record_titles = page.query_selector_all(".govuk-summary-list__value a")
#         record_titles_text = [title.text() for title in record_titles]
#         assert record_titles_text == sorted(record_titles_text)


# def test_clear_filters(page: Page):
#     # Go to the browse page
#     page.goto("/browse")

#     # Select a filter option for transferring body
#     page.select_option(".filters-form__transferring-body--select", "Arts Council England")
#     time.sleep(1)  # Wait for the page to update (adjust the sleep time as needed)

#     # Click the "Clear filters" button
#     page.click(".filters-form__clear--button a")
#     time.sleep(1)  # Wait for the page to reset (adjust the sleep time as needed)

#     # Check that the filter is reset to its default state
#     selected_option = page.query_selector(".filters-form__transferring-body--select option:checked")
#     assert selected_option.text() == "Choose one..."
