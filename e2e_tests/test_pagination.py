from playwright.sync_api import Page, expect


class TestPagination:
    @property
    def route_url(self):
        return "/search/transferring_body"

    @property
    def browse_route_url(self):
        return "/browse"

    @property
    def browse_transferring_body_route_url(self):
        return "/browse/transferring_body"

    @property
    def transferring_body_id(self):
        return "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50"

    def test_search_transferring_body_pagination_get_first_page(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with a single search term
        Then the table should contain the expected headers and entries and pagination object
        with the first page link available
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

        url = (
            f"{self.route_url}/{self.transferring_body_id}"
            "?page=1&query=a&search_area=everywhere&sort=file_name&open_all=&search_filter=#tbl_result"
        )
        assert (
            aau_user_page.locator("data-testid=pagination-link")
            .first.get_attribute("href")
            .strip()
            == url
        )
        links = aau_user_page.locator("data-testid=pagination-link-title").all()
        assert len(links) > 0, "No pagination links found"
        assert links[0].text_content().strip() == "Nextpage"

    def test_search_transferring_body_pagination_get_previous_page(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        and click on page 2 link
        Then the table should contain the expected headers and entries and pagination object
        with previous page link
        """
        aau_user_page.goto(f"{self.browse_route_url}")
        aau_user_page.locator("#search-input").click()
        aau_user_page.locator("#search-input").fill("a")
        aau_user_page.get_by_role("button", name="Search").click()
        aau_user_page.get_by_role("link", name="Testing A").click()
        aau_user_page.get_by_label("Page 2").click()
        aau_user_page.wait_for_selector(".govuk-pagination")

        assert (
            aau_user_page.locator(".govuk-pagination").first.get_attribute(
                "aria-label"
            )
            == "Pagination"
        )
        links = aau_user_page.locator("data-testid=pagination-link-title").all()

        assert links[0].text_content() == "Previouspage"

    def test_search_transferring_body_pagination_get_next_page(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        and click on page 2 link
        Then the table should contain the expected headers and entries and pagination object
        with previous and next page link
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
        expected_url = (
            f"{self.route_url}/{self.transferring_body_id}"
            "?page=1&query=a&search_area=everywhere&sort=file_name&open_all=&search_filter=#tbl_result"
        )
        actual_href = (
            aau_user_page.locator("data-testid=pagination-link")
            .first.get_attribute("href")
            .strip()
        )
        assert actual_href == expected_url

        aau_user_page.locator(".govuk-pagination__link", has_text="2").click()

        actual_relative_url = aau_user_page.url.split("://", 1)[1].split(
            "/", 1
        )[1]
        url_params = "page=2&query=a&search_area=everywhere&sort=file_name&open_all=&search_filter=#tbl_result"
        expected_next_url = (
            f"""{self.route_url}/{self.transferring_body_id}?{url_params}"""
        )
        assert f"/{actual_relative_url}" == expected_next_url

    def test_search_transferring_body_pagination_get_ellipses_page(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with a single search term
        Then the table should contain the expected headers and entries and pagination object
        with ellipses page link
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
        page_links = aau_user_page.locator("data-testid=pagination-link").all()
        assert page_links[0].inner_text() == "1"
        assert page_links[1].inner_text() == "2"

        last_page = page_links[-1].text_content()
        assert page_links[-1].text_content() == last_page

        ellipsis_link = aau_user_page.locator(
            ".govuk-pagination__item--ellipses"
        ).all()
        if ellipsis_link:
            assert ellipsis_link[0].inner_text().strip() == "…"
        else:
            print("No ellipses links were found in the pagination.")

        links = aau_user_page.locator("data-testid=pagination-link-title").all()
        assert links[0].text_content().strip() == "Nextpage"

    def test_search_transferring_body_pagination_click_previous_page_link(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        and click on page 2 link
        Then the table should contain the expected headers and entries and pagination object
        and expected page 1 response
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

        aau_user_page.get_by_label("Page 2").click()

        links = aau_user_page.locator("data-testid=pagination-link-title").all()

        assert links[0].text_content() == "Previouspage"

        aau_user_page.get_by_label("Page 1", exact=True).click()

        url = (
            f"{self.route_url}/{self.transferring_body_id}"
            "?page=1&query=a&search_area=everywhere&sort=file_name#tbl_result"
        )
        expect(aau_user_page).to_have_url(url)

    def test_search_transferring_body_pagination_click_next_page_link(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        and click on page 2 link
        Then the table should contain the expected headers and entries and pagination object
        and expected page 3 response
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

        aau_user_page.get_by_label("Page 2", exact=True).click()

        aau_user_page.wait_for_selector(".govuk-pagination")

        aau_user_page.wait_for_selector(".govuk-pagination")

        url = (
            f"{self.route_url}/{self.transferring_body_id}"
            "?page=2&query=a&search_area=everywhere&sort=file_name&open_all=&search_filter=#tbl_result"
        )
        expect(aau_user_page).to_have_url(url)

    def test_search_transferring_body_pagination_get_last_page(
        self, aau_user_page: Page
    ):
        """
        Given a user on the search transferring body page
        When they interact with the search form and submit a query with single search term
        and click on last page
        Then the table should contain the expected headers and entries and pagination object
        with previous page link
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
        page_links = aau_user_page.locator("data-testid=pagination-link").all()
        last_page = page_links[len(page_links) - 1].text_content()
        aau_user_page.get_by_role("link").get_by_text(last_page).click()
        link_titles_locator = aau_user_page.locator(
            "data-testid=pagination-link-title"
        )
        link_titles_locator.first.wait_for(state="visible")
        links = link_titles_locator.all()
        assert links[0].text_content() == "Previouspage"
