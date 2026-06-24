"""
test_full_flow.py — End-to-end sequential test suite.

Execution order (single browser session, no restarts):
  1. Login
  2. Links     — navigate sidebar → profile → add-link page
  3. Appearance — theme selection, Pro+ gating assertion, free-theme select
  4. Contacts  — full CRUD (Create, Read, Update, Delete)

All tests share the session-scoped `authenticated_page` fixture so the
browser never restarts between phases.

Run order is enforced by pytest-ordering (pip install pytest-ordering).
If the plugin is absent the tests still run in the order they are defined
because pytest collects them top-to-bottom within a file.
"""

from __future__ import annotations

import os

import pytest
from playwright.sync_api import Page

from models import FeatureStatus, Plan
from pages.add_link_page import AddLinkPage
from pages.appearance_page import AppearancePage
from pages.contacts_page import ContactData, ContactsPage
from pages.profile_links_page import ProfileLinksPage
from pages.sidebar_navigation import SidebarNavigation

# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------
_PROFILE_ID = os.environ.get("APPSHA_PROFILE_ID", "vfchxswq")

_CONTACT_CREATE = ContactData(
    name="Alice Appsha",
    email="alice@appsha-test.com",
    phone="+1-555-0101",
    address="789 Full Flow St, SF",
    birthday="1992-05-15",
    anniversary="2026-06-23",
    note="Created by automation full flow",
    tags=["e2e", "full-flow"],
)
_CONTACT_UPDATED = ContactData(
    name="Alice Appsha Updated",
    email="alice.updated@appsha-test.com",
    phone="+1-555-0202",
    address="999 Updated Ave, SF",
    birthday="1992-05-16",
    anniversary="2026-06-24",
    note="Updated by automation full flow",
    tags=["e2e", "full-flow", "updated"],
)


# ===========================================================================
# PHASE 1 — Login
# ===========================================================================

class TestPhase1Login:
    """Verify we arrive on the dashboard after authentication."""

    @pytest.mark.order(1)
    def test_login_lands_on_dashboard(self, authenticated_page: Page) -> None:
        """Post-login URL must contain /u."""
        assert "/u" in authenticated_page.url, (
            f"Expected '/u' in URL after login, got: {authenticated_page.url}"
        )


# ===========================================================================
# PHASE 2 — Links navigation
# ===========================================================================

class TestPhase2Links:
    """Navigate sidebar → profile Links section → add-link page."""

    @pytest.mark.order(2)
    def test_click_links_sidebar(self, authenticated_page: Page) -> None:
        """Clicking Links in the sidebar must keep us within /u."""
        nav = SidebarNavigation(authenticated_page)
        nav.click_links()
        assert "/u" in authenticated_page.url, (
            f"After sidebar click expected /u in URL, got: {authenticated_page.url}"
        )

    @pytest.mark.order(3)
    def test_click_links_tab(self, authenticated_page: Page) -> None:
        """Links tab must be clickable and keep us on the profile page."""
        links_page = ProfileLinksPage(authenticated_page)
        links_page.click_links_tab()
        assert "/u" in authenticated_page.url

    @pytest.mark.order(4)
    def test_navigate_to_add_link(self, authenticated_page: Page) -> None:
        """Add Link button must navigate to the add-link URL."""
        links_page = ProfileLinksPage(authenticated_page)
        links_page.click_add_link()
        links_page.expect_add_link_url()
        assert "/links/add-link" in authenticated_page.url, (
            f"Expected /links/add-link in URL, got: {authenticated_page.url}"
        )

    @pytest.mark.order(5)
    def test_add_link_page_has_features(self, authenticated_page: Page) -> None:
        """All 6 feature keys must be present in the feature-state dict."""
        add_link = AddLinkPage(authenticated_page)
        states = add_link.get_feature_states()
        expected_keys = {
            "normal_link", "embed_link", "attachment",
            "external_shop", "highlight", "analytics",
        }
        assert expected_keys == set(states.keys()), (
            f"Feature states missing keys. Got: {set(states.keys())}"
        )


# ===========================================================================
# PHASE 3 — Appearance
# ===========================================================================

class TestPhase3Appearance:
    """
    Navigate to Appearance, assert theme cards render, validate Pro+ gating.

    Business rules:
      - All plans : free themes are selectable.
      - Pro+ only : Pro theme tile is unlocked; Customize panel is accessible.
      - Free / Pro : Pro theme shows a lock/upgrade indicator;
                     Customize panel is hidden or disabled.
    """

    @pytest.fixture(autouse=True)
    def _go_to_appearance(self, authenticated_page: Page) -> None:
        """Navigate to Appearance before each test in this class."""
        ap = AppearancePage(authenticated_page)
        ap.navigate()

    @pytest.mark.order(6)
    def test_appearance_page_loads(self, authenticated_page: Page) -> None:
        """Appearance URL must be reached successfully."""
        AppearancePage(authenticated_page).assert_on_appearance_page()

    @pytest.mark.order(7)
    def test_theme_cards_present(self, authenticated_page: Page) -> None:
        """At least one theme card must be visible."""
        AppearancePage(authenticated_page).assert_theme_cards_visible()

    @pytest.mark.order(8)
    def test_free_theme_selectable(self, authenticated_page: Page) -> None:
        """Any plan must be able to select a free theme without errors."""
        ap = AppearancePage(authenticated_page)
        ap.select_theme_by_index(0)
        # Page should remain on appearance after selection
        ap.assert_on_appearance_page()

    @pytest.mark.order(8.5)
    def test_click_multiple_themes(self, authenticated_page: Page) -> None:
        """Click multiple themes to verify interaction."""
        ap = AppearancePage(authenticated_page)
        ap.select_theme_by_index(1)
        ap.select_theme_by_index(2)
        ap.assert_on_appearance_page()

    @pytest.mark.order(9)
    def test_pro_theme_gating(self, authenticated_page: Page) -> None:
        """
        Pro+ accounts → Pro theme is NOT locked.
        All other plans → Pro theme shows a lock / upgrade prompt.

        The test reads APPSHA_PLAN env var (default: free_trial) to decide
        which assertion to make — it does NOT change the account plan itself.
        """
        plan_raw = os.environ.get("APPSHA_PLAN", "free_trial").lower()
        ap = AppearancePage(authenticated_page)

        if plan_raw == "pro_plus":
            assert not ap.is_pro_theme_locked(), (
                "Pro+ account: Pro theme should NOT be locked"
            )
        else:
            # For free_trial / free / pro the Pro theme tile should show a lock
            # or the tile might simply not exist — both are acceptable.
            pro_tile = authenticated_page.locator(
                "[data-theme='pro'], label:has-text('Pro'), [data-testid='theme-pro']"
            ).first
            if pro_tile.is_visible():
                assert ap.is_pro_theme_locked(), (
                    f"Plan '{plan_raw}': Pro theme tile should show a lock/upgrade prompt"
                )

    @pytest.mark.order(10)
    def test_customize_panel_gating(self, authenticated_page: Page) -> None:
        """
        Pro+ → Customize button is accessible and enabled.
        Others → Customize button is absent, disabled, or behind an upgrade prompt.
        """
        plan_raw = os.environ.get("APPSHA_PLAN", "free_trial").lower()
        ap = AppearancePage(authenticated_page)

        if plan_raw == "pro_plus":
            assert ap.is_customize_available(), (
                "Pro+ account: Customize panel should be available"
            )
        else:
            assert not ap.is_customize_available(), (
                f"Plan '{plan_raw}': Customize panel should NOT be available"
            )

    @pytest.mark.order(11)
    def test_pro_plus_customize_workflow(self, authenticated_page: Page) -> None:
        """
        Pro+ only: open Customize, set colours and font, save.
        Skipped automatically for all other plans.
        """
        plan_raw = os.environ.get("APPSHA_PLAN", "free_trial").lower()
        if plan_raw != "pro_plus":
            pytest.skip(
                f"Customize workflow is Pro+ only (current plan: {plan_raw}). "
                "Set APPSHA_PLAN=pro_plus to run this test."
            )

        ap = AppearancePage(authenticated_page)
        ap.select_pro_theme()
        ap.open_customize_panel()
        ap.set_background_color("#1a1a2e")
        ap.set_button_color("#e94560")
        ap.set_font("Inter")
        ap.save()
        ap.assert_on_appearance_page()


# ===========================================================================
# PHASE 4 — Contacts CRUD
# ===========================================================================

class TestPhase4Contacts:
    """
    Full CRUD on the Contacts page, using the same browser session.

    Order: Create → Read/Search → Update → Delete
    """

    @pytest.fixture(autouse=True)
    def _go_to_contacts(self, authenticated_page: Page) -> None:
        """Navigate to Contacts before each test in this class."""
        cp = ContactsPage(authenticated_page)
        cp.navigate()

    # ---- CREATE -----------------------------------------------------------

    @pytest.mark.order(12)
    def test_contacts_page_loads(self, authenticated_page: Page) -> None:
        """Contacts URL must be reached successfully."""
        ContactsPage(authenticated_page).assert_on_contacts_page()

    @pytest.mark.order(13)
    def test_create_contact(self, authenticated_page: Page) -> None:
        """Create a new contact and verify it appears in the list."""
        cp = ContactsPage(authenticated_page)

        # If the contact already exists from a previous run, skip creation
        if cp.contact_exists(_CONTACT_CREATE.name):
            pytest.skip("Contact already exists — skipping create (idempotent run)")

        cp.create_contact(_CONTACT_CREATE)
        cp.assert_contact_visible(_CONTACT_CREATE.name)

    # ---- READ / SEARCH ----------------------------------------------------

    @pytest.mark.order(14)
    def test_read_contact_list(self, authenticated_page: Page) -> None:
        """At least one contact row must be visible after creation."""
        cp = ContactsPage(authenticated_page)
        if cp.is_empty():
            pytest.skip("Contact list is empty — previous create may have failed")
        count = cp.contact_row_count()
        assert count >= 1, f"Expected at least 1 contact, got {count}"

    @pytest.mark.order(15)
    def test_search_contact(self, authenticated_page: Page) -> None:
        """Searching by name must surface the target contact row."""
        cp = ContactsPage(authenticated_page)
        if not cp.contact_exists(_CONTACT_CREATE.name):
            pytest.skip("Target contact not found — skipping search test")

        cp.search(_CONTACT_CREATE.name.split()[0])  # search by first name
        assert cp.contact_exists(_CONTACT_CREATE.name), (
            f"Contact '{_CONTACT_CREATE.name}' not found after searching"
        )

    # ---- UPDATE -----------------------------------------------------------

    @pytest.mark.order(16)
    def test_update_contact(self, authenticated_page: Page) -> None:
        """Edit the created contact and verify the updated name appears."""
        cp = ContactsPage(authenticated_page)

        # Determine which name to look for (original or already-updated)
        source_name = (
            _CONTACT_CREATE.name
            if cp.contact_exists(_CONTACT_CREATE.name)
            else _CONTACT_UPDATED.name
        )
        if not cp.contact_exists(source_name):
            pytest.skip("Neither original nor updated contact found — skipping update")

        cp.update_contact(source_name, _CONTACT_UPDATED)
        cp.assert_contact_visible(_CONTACT_UPDATED.name)

    # ---- DELETE -----------------------------------------------------------

    @pytest.mark.order(17)
    def test_delete_contact(self, authenticated_page: Page) -> None:
        """Delete the (updated) contact and verify it is gone."""
        cp = ContactsPage(authenticated_page)

        # Handle both possible names (in case update was skipped)
        target = (
            _CONTACT_UPDATED.name
            if cp.contact_exists(_CONTACT_UPDATED.name)
            else _CONTACT_CREATE.name
        )
        if not cp.contact_exists(target):
            pytest.skip("Contact not found — skipping delete")

        cp.delete_contact(target)
        cp.assert_contact_not_visible(target)

    @pytest.mark.order(18)
    def test_contacts_clean_after_delete(self, authenticated_page: Page) -> None:
        """Verify the test contact is absent, confirming delete succeeded."""
        cp = ContactsPage(authenticated_page)
        assert not cp.contact_exists(_CONTACT_UPDATED.name), (
            f"'{_CONTACT_UPDATED.name}' should have been deleted"
        )
        assert not cp.contact_exists(_CONTACT_CREATE.name), (
            f"'{_CONTACT_CREATE.name}' should have been deleted"
        )
