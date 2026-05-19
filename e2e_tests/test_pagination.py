from playwright.sync_api import Page


class TestPagination:
    @property
    def browse_route_url(self):
        return "/browse"

    def test_search_transferring_body_pagination_smoke(
        self, aau_user_page: Page
    ):
        """
        Given a user reaches transferring body search results
        Then a pagination control is rendered and at least one transition link exists.
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.wait_for_selector(".govuk-pagination")

        assert (
            aau_user_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        links = aau_user_page.locator("data-testid=pagination-link").all()
        assert len(links) > 0, "No pagination links found"
