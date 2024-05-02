from playwright.sync_api import Page


class TestRoutes:
    def test_route_accessibility(self, standard_user_page: Page):
        response = standard_user_page.goto("/accessibility")
        assert response.ok
        assert response.status_code == 200

    def test_route_cookies(self, standard_user_page: Page):
        response = standard_user_page.goto("/cookies")
        assert response.ok
        assert response.status_code == 200

    def test_route_privacy(self, standard_user_page: Page):
        response = standard_user_page.goto("/privacy")
        assert response.ok
        assert response.status_code == 200

    def test_route_how_to_use(self, standard_user_page: Page):
        response = standard_user_page.goto("/how-to-use-this-service")
        assert response.ok
        assert response.status_code == 200

    def test_route_terms_of_use(self, standard_user_page: Page):
        response = standard_user_page.goto("/terms-of-use")
        assert response.ok
        assert response.status_code == 200
