"""
SidebarNavigation page object for the Appsha staging site.

Encapsulates sidebar navigation interactions, specifically clicking the
Links item in the left sidebar and waiting for the resulting section to load.

No time.sleep() calls are used — all waits are expressed via Playwright APIs.
"""

from playwright.sync_api import Page

from appsha_selectors import SIDEBAR_LINKS


class SidebarNavigation:
    """Page object for the Appsha sidebar navigation."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def click_links(self) -> None:
        """Wait for the sidebar Links item to be visible, click it, then wait for the page to settle."""
        self.page.locator(SIDEBAR_LINKS).wait_for(state="visible")
        self.page.locator(SIDEBAR_LINKS).click()
        self.page.wait_for_load_state("networkidle")
