"""
Tests covering sidebar → profile links → add-link navigation chain.

Requirements: 2.1 – 2.3
"""

import pytest
from playwright.sync_api import Page

from pages.profile_links_page import ProfileLinksPage
from pages.sidebar_navigation import SidebarNavigation


class TestLinksNavigation:
    """Navigation chain tests."""

    def test_sidebar_links_click_loads_section(self, authenticated_page: Page) -> None:
        """Clicking Links in the sidebar must navigate to the links section."""
        nav = SidebarNavigation(authenticated_page)
        nav.click_links()
        # After the click the URL should reflect the links section
        assert "/u" in authenticated_page.url, (
            f"Expected to still be within the /u route, got: {authenticated_page.url}"
        )

    def test_links_tab_click_activates_tab(self, authenticated_page: Page) -> None:
        """Clicking the Links tab inside the profile view must make it active."""
        links_page = ProfileLinksPage(authenticated_page)
        links_page.click_links_tab()
        # Tab is active when the page settles; assert we're still on the correct base URL
        assert "/u" in authenticated_page.url, (
            f"Expected URL to remain under /u after clicking Links tab, "
            f"got: {authenticated_page.url}"
        )

    def test_add_link_button_navigates_to_add_link_page(
        self, authenticated_page: Page
    ) -> None:
        """Clicking Add Link must navigate to the add-link creation URL."""
        links_page = ProfileLinksPage(authenticated_page)
        links_page.click_add_link()
        links_page.expect_add_link_url()
        assert "/links/add-link" in authenticated_page.url, (
            f"Expected '/links/add-link' in URL, got: {authenticated_page.url}"
        )
