"""
Tests covering the authentication flow.

Requirements: 1.1 – 1.4
"""

import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage


class TestLogin:
    """Authentication tests."""

    def test_login_page_loads(self, unauthenticated_page: Page) -> None:
        """The login URL must be reachable and the page must load without error."""
        login = LoginPage(unauthenticated_page)
        login.navigate()
        assert "login" in unauthenticated_page.url, (
            f"Expected 'login' in URL after navigation, got: {unauthenticated_page.url}"
        )

    def test_login_redirects_to_dashboard(self, authenticated_page: Page) -> None:
        """After successful login the URL must contain '/u'."""
        assert "/u" in authenticated_page.url, (
            f"Expected '/u' in URL after authentication, got: {authenticated_page.url}"
        )
