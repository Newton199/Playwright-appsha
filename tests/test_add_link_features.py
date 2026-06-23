"""
Tests covering feature visibility and state on the add-link page.

Requirements: 3.1 – 3.6, 4.1
"""

import os
import pytest
from playwright.sync_api import Page

from models import FeatureStatus
from pages.add_link_page import AddLinkPage


class TestAddLinkFeatures:
    """Add-link page feature-detection tests."""

    @pytest.fixture(autouse=True)
    def navigate_to_add_link(self, authenticated_page: Page) -> None:
        """Ensure the browser is on the add-link page before each test."""
        profile_id = os.environ.get("APPSHA_PROFILE_ID", "vfchxswq")
        if "/links/add-link" not in authenticated_page.url:
            authenticated_page.goto(
                f"https://staging.appsha.com/u/profiles/{profile_id}/links/add-link"
            )
            authenticated_page.wait_for_url("**/links/add-link", timeout=15000)

    def test_normal_link_feature_visible_and_enabled(
        self, authenticated_page: Page
    ) -> None:
        """The normal link feature must be visible and in ENABLED state."""
        page = AddLinkPage(authenticated_page)
        states = page.get_feature_states()
        assert states["normal_link"].visible, "normal_link must be visible"
        assert states["normal_link"].status == FeatureStatus.ENABLED, (
            f"normal_link expected ENABLED, got {states['normal_link'].status}"
        )

    def test_embed_link_feature_present(self, authenticated_page: Page) -> None:
        """The embed_link feature state must be detectable (not unknown)."""
        page = AddLinkPage(authenticated_page)
        states = page.get_feature_states()
        assert "embed_link" in states, "embed_link must be present in feature states"

    def test_attachment_feature_present(self, authenticated_page: Page) -> None:
        """The attachment feature state must be detectable."""
        page = AddLinkPage(authenticated_page)
        states = page.get_feature_states()
        assert "attachment" in states, "attachment must be present in feature states"

    def test_external_shop_feature_present(self, authenticated_page: Page) -> None:
        """The external_shop feature state must be detectable."""
        page = AddLinkPage(authenticated_page)
        states = page.get_feature_states()
        assert "external_shop" in states, (
            "external_shop must be present in feature states"
        )

    def test_highlight_feature_present(self, authenticated_page: Page) -> None:
        """The highlight feature state must be detectable."""
        page = AddLinkPage(authenticated_page)
        states = page.get_feature_states()
        assert "highlight" in states, "highlight must be present in feature states"

    def test_analytics_feature_present(self, authenticated_page: Page) -> None:
        """The analytics feature state must be detectable."""
        page = AddLinkPage(authenticated_page)
        states = page.get_feature_states()
        assert "analytics" in states, "analytics must be present in feature states"

    def test_all_features_enabled_on_free_trial(
        self, authenticated_page: Page
    ) -> None:
        """During free trial all 6 features must be ENABLED with no upgrade prompts."""
        page = AddLinkPage(authenticated_page)
        states = page.get_feature_states()

        for feature, state in states.items():
            assert state.visible, (
                f"Feature '{feature}' must be visible during free trial"
            )
            assert state.status == FeatureStatus.ENABLED, (
                f"Feature '{feature}' expected ENABLED on free trial, got {state.status}"
            )
            assert not state.has_upgrade_prompt, (
                f"Feature '{feature}' must NOT show an upgrade prompt during free trial"
            )
