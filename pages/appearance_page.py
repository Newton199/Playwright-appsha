"""
AppearancePage — page object for the Appsha profile appearance editor.

URL: https://staging.appsha.com/u/profiles/{profile_id}/appearance

Business rules enforced here:
  - Any plan: can browse and select free themes.
  - Pro+ only: can select the "Pro" theme and open the Customize panel
    (background colour, button colour, font). Non-Pro+ users see a lock
    icon or upgrade prompt on those controls.

No time.sleep() — all waits use Playwright APIs.
"""

from __future__ import annotations

import os

from playwright.sync_api import Page

from appsha_selectors import (
    APPEARANCE_BG_COLOR,
    APPEARANCE_BTN_COLOR,
    APPEARANCE_CUSTOMIZE_BTN,
    APPEARANCE_CUSTOMIZE_PANEL,
    APPEARANCE_FONT_SELECT,
    APPEARANCE_FREE_THEME,
    APPEARANCE_PRO_LOCK,
    APPEARANCE_PRO_THEME,
    APPEARANCE_SAVE_BTN,
    APPEARANCE_THEME_CARDS,
)

_PROFILE_ID = os.environ.get("APPSHA_PROFILE_ID", "vfchxswq")
APPEARANCE_URL = f"https://staging.appsha.com/u/profiles/{_PROFILE_ID}/appearance"


class AppearancePage:
    """Encapsulates all interactions on the profile appearance page."""

    def __init__(self, page: Page) -> None:
        self.page = page

    # ------------------------------------------------------------------
    # Navigation helpers
    # ------------------------------------------------------------------

    def navigate(self) -> None:
        """Go directly to the appearance URL if not already there."""
        if "/appearance" not in self.page.url:
            self.page.goto(APPEARANCE_URL, wait_until="networkidle")
            self.page.wait_for_url("**/appearance", timeout=15_000)
        
        # Ensure theme cards are visible
        self.page.locator(S.APPEARANCE_THEME_CARDS).first.wait_for(
            state="visible", timeout=10_000
        )

    def navigate_via_tab(self) -> None:
        """Click the Appearance tab in the profile tab bar (already on profile page)."""
        from appsha_selectors import APPEARANCE_TAB
        tab = self.page.locator(APPEARANCE_TAB).first
        tab.wait_for(state="visible", timeout=10_000)
        tab.click()
        self.page.wait_for_url("**/appearance", timeout=15_000)
        self.page.wait_for_load_state("domcontentloaded")

    # ------------------------------------------------------------------
    # Theme selection
    # ------------------------------------------------------------------

    def theme_cards_count(self) -> int:
        """Return the number of theme cards visible on the page."""
        self.page.locator(APPEARANCE_THEME_CARDS).first.wait_for(
            state="visible", timeout=10_000
        )
        return self.page.locator(APPEARANCE_THEME_CARDS).count()

    def select_free_theme(self) -> None:
        """Select the first available free theme (works on any plan)."""
        theme = self.page.locator(APPEARANCE_FREE_THEME).first
        theme.wait_for(state="visible", timeout=10_000)
        theme.click()
        # Wait briefly for selection state to apply
        self.page.wait_for_load_state("domcontentloaded")

    def is_pro_theme_locked(self) -> bool:
        """Return True when the Pro theme tile shows a lock / upgrade prompt."""
        lock = self.page.locator(APPEARANCE_PRO_LOCK).first
        return lock.is_visible()

    def select_pro_theme(self) -> None:
        """Click the Pro theme tile.  Only succeeds for Pro+ accounts."""
        pro = self.page.locator(APPEARANCE_PRO_THEME).first
        pro.wait_for(state="visible", timeout=10_000)
        pro.click()
        self.page.wait_for_load_state("domcontentloaded")

    # ------------------------------------------------------------------
    # Customize panel (Pro+ only)
    # ------------------------------------------------------------------

    def is_customize_available(self) -> bool:
        """Return True if the Customize button/panel is accessible (not locked)."""
        btn = self.page.locator(APPEARANCE_CUSTOMIZE_BTN).first
        if not btn.is_visible():
            return False
        # If the button is disabled it means it's locked for this plan
        return btn.is_enabled()

    def open_customize_panel(self) -> None:
        """Click Customize and wait for the panel to appear."""
        btn = self.page.locator(APPEARANCE_CUSTOMIZE_BTN).first
        btn.wait_for(state="visible", timeout=10_000)
        btn.click()
        self.page.locator(APPEARANCE_CUSTOMIZE_PANEL).first.wait_for(
            state="visible", timeout=10_000
        )

    def set_background_color(self, hex_color: str) -> None:
        """Set the background colour picker value (Pro+ only)."""
        picker = self.page.locator(APPEARANCE_BG_COLOR).first
        picker.wait_for(state="visible", timeout=8_000)
        picker.fill(hex_color)

    def set_button_color(self, hex_color: str) -> None:
        """Set the button colour picker value (Pro+ only)."""
        picker = self.page.locator(APPEARANCE_BTN_COLOR).first
        picker.wait_for(state="visible", timeout=8_000)
        picker.fill(hex_color)

    def set_font(self, font_value: str) -> None:
        """Select a font from the font dropdown (Pro+ only)."""
        select = self.page.locator(APPEARANCE_FONT_SELECT).first
        select.wait_for(state="visible", timeout=8_000)
        select.select_option(font_value)

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Click the Save / Apply button and wait for the page to settle."""
        btn = self.page.locator(APPEARANCE_SAVE_BTN).first
        btn.wait_for(state="visible", timeout=8_000)
        btn.click()
        self.page.wait_for_load_state("networkidle")

    # ------------------------------------------------------------------
    # Assertion helpers
    # ------------------------------------------------------------------

    def assert_on_appearance_page(self) -> None:
        assert "appearance" in self.page.url, (
            f"Expected URL to contain 'appearance', got: {self.page.url}"
        )

    def assert_theme_cards_visible(self) -> None:
        count = self.theme_cards_count()
        assert count > 0, "Expected at least one theme card to be visible on the Appearance page"
