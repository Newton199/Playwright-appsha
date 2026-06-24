"""
ProfileLinksPage page object for the Appsha Playwright automation suite.

Encapsulates interactions with the Profiles → Links view, including
clicking the Links tab, clicking the Add Link button, and verifying
navigation to the add-link URL.

No time.sleep() calls are used — all waits are expressed via Playwright APIs.
"""

from playwright.sync_api import Page

from appsha_selectors import ADD_LINK_BTN, LINKS_TAB


class ProfileLinksPage:
    """Page object representing the profile links section."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def click_links_tab(self) -> None:
        """Wait for the Links tab to be visible, click it, and wait for the DOM."""
        tab = self.page.locator(LINKS_TAB).first
        tab.wait_for(state="attached", timeout=10_000)
        tab.scroll_into_view_if_needed()
        tab.click(force=True)
        self.page.wait_for_load_state("networkidle")

    def click_add_link(self) -> None:
        """Wait for the Add Link button to be visible, then click it (first match)."""
        locator = self.page.locator(ADD_LINK_BTN).first
        locator.wait_for(state="visible")
        locator.click()

    def expect_add_link_url(self) -> None:
        """Wait for navigation to the add-link URL and assert the current URL."""
        self.page.wait_for_url("**/links/add-link", timeout=10000)
        assert "/links/add-link" in self.page.url, (
            f"Expected URL to contain '/links/add-link', got: {self.page.url}"
        )
