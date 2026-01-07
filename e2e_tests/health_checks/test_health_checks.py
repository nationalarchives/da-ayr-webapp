"""
Feature: Health Check functionality
"""

import pytest
from playwright.sync_api import Page


class TestHealthCheck:

    @pytest.mark.health_check
    def test_homepage_loads(self, page: Page):
        """Simple check that homepage responds."""
        response = page.goto("/")
        assert response.status < 400
