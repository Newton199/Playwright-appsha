"""
Tests covering subscription-tier feature gating on the add-link page.

Requirements: 4.1 – 4.5
"""

import os

import pytest
from playwright.sync_api import Page

from models import FeatureStatus, Plan
from pages.add_link_page import AddLinkPage
from validators.subscription_validator import SubscriptionValidator


def _current_plan() -> Plan:
    """Return the active plan from APPSHA_PLAN env var, defaulting to FREE_TRIAL."""
    raw = os.environ.get("APPSHA_PLAN", "free_trial").lower()
    mapping = {
        "free_trial": Plan.FREE_TRIAL,
        "free": Plan.FREE,
        "pro": Plan.PRO,
        "pro_plus": Plan.PRO_PLUS,
    }
    return mapping.get(raw, Plan.FREE_TRIAL)


class TestSubscriptionGating:
    """Subscription-tier gating tests.

    These tests validate the actual staging account against the plan
    configured via APPSHA_PLAN (default: FREE_TRIAL).
    """

    @pytest.fixture(autouse=True)
    def navigate_to_add_link(self, authenticated_page: Page) -> None:
        """Ensure we are on the add-link page before each test."""
        profile_id = os.environ.get("APPSHA_PROFILE_ID", "vfchxswq")
        if "/links/add-link" not in authenticated_page.url:
            authenticated_page.goto(
                f"https://staging.appsha.com/u/profiles/{profile_id}/links/add-link"
            )
            authenticated_page.wait_for_url("**/links/add-link", timeout=15000)

    # ------------------------------------------------------------------
    # Free Trial assertions
    # ------------------------------------------------------------------

    @pytest.mark.subscription
    def test_free_trial_all_features_enabled(self, authenticated_page: Page) -> None:
        """Free trial: all 6 features must be ENABLED."""
        add_link = AddLinkPage(authenticated_page)
        states = add_link.get_feature_states()
        validator = SubscriptionValidator()
        result = validator.validate(Plan.FREE_TRIAL, states)
        assert result.passed, _format_failures(result)

    # ------------------------------------------------------------------
    # Free Plan assertions (run when APPSHA_PLAN=free)
    # ------------------------------------------------------------------

    @pytest.mark.subscription
    def test_free_plan_normal_link_enabled(self, authenticated_page: Page) -> None:
        """Free plan: normal_link must remain ENABLED."""
        add_link = AddLinkPage(authenticated_page)
        states = add_link.get_feature_states()
        state = states["normal_link"]
        assert state.status == FeatureStatus.ENABLED, (
            f"normal_link expected ENABLED on Free plan, got {state.status}"
        )

    @pytest.mark.subscription
    def test_free_plan_premium_features_gated(self, authenticated_page: Page) -> None:
        """Free plan: embed, attachment, highlight must be gated (DISABLED or UPGRADE_PROMPT)."""
        add_link = AddLinkPage(authenticated_page)
        states = add_link.get_feature_states()
        gated = ["embed_link", "attachment", "highlight"]
        allowed_gated = {FeatureStatus.DISABLED, FeatureStatus.UPGRADE_PROMPT, FeatureStatus.HIDDEN}

        for feature in gated:
            state = states[feature]
            # Only assert gating when the account is actually on the Free plan
            if _current_plan() == Plan.FREE:
                assert state.status in allowed_gated, (
                    f"{feature} should be gated on Free plan, got {state.status}"
                )

    @pytest.mark.subscription
    def test_free_plan_shop_and_analytics_hidden(
        self, authenticated_page: Page
    ) -> None:
        """Free plan: external_shop and analytics must be gated."""
        add_link = AddLinkPage(authenticated_page)
        states = add_link.get_feature_states()
        hidden_features = ["external_shop", "analytics"]
        allowed_gated = {FeatureStatus.HIDDEN, FeatureStatus.UPGRADE_PROMPT, FeatureStatus.DISABLED}

        if _current_plan() == Plan.FREE:
            for feature in hidden_features:
                state = states[feature]
                assert state.status in allowed_gated, (
                    f"{feature} should be hidden/gated on Free plan, got {state.status}"
                )

    # ------------------------------------------------------------------
    # Pro Plan assertions (run when APPSHA_PLAN=pro)
    # ------------------------------------------------------------------

    @pytest.mark.subscription
    def test_pro_plan_core_features_enabled(self, authenticated_page: Page) -> None:
        """Pro plan: normal_link, embed, attachment, highlight, analytics must be ENABLED."""
        if _current_plan() != Plan.PRO:
            pytest.skip("Skipped: account is not on Pro plan (set APPSHA_PLAN=pro)")
        add_link = AddLinkPage(authenticated_page)
        states = add_link.get_feature_states()
        should_be_enabled = ["normal_link", "embed_link", "attachment", "highlight", "analytics"]
        for feature in should_be_enabled:
            assert states[feature].status == FeatureStatus.ENABLED, (
                f"{feature} expected ENABLED on Pro plan, got {states[feature].status}"
            )

    @pytest.mark.subscription
    def test_pro_plan_shop_gated(self, authenticated_page: Page) -> None:
        """Pro plan: external_shop must still be gated."""
        if _current_plan() != Plan.PRO:
            pytest.skip("Skipped: account is not on Pro plan (set APPSHA_PLAN=pro)")
        add_link = AddLinkPage(authenticated_page)
        states = add_link.get_feature_states()
        allowed_gated = {FeatureStatus.HIDDEN, FeatureStatus.UPGRADE_PROMPT, FeatureStatus.DISABLED}
        assert states["external_shop"].status in allowed_gated, (
            f"external_shop must be gated on Pro plan, got {states['external_shop'].status}"
        )

    # ------------------------------------------------------------------
    # Pro+ Plan assertions (run when APPSHA_PLAN=pro_plus)
    # ------------------------------------------------------------------

    @pytest.mark.subscription
    def test_pro_plus_all_features_enabled(self, authenticated_page: Page) -> None:
        """Pro+ plan: all 6 features must be ENABLED."""
        if _current_plan() != Plan.PRO_PLUS:
            pytest.skip("Skipped: account is not on Pro+ plan (set APPSHA_PLAN=pro_plus)")
        add_link = AddLinkPage(authenticated_page)
        states = add_link.get_feature_states()
        validator = SubscriptionValidator()
        result = validator.validate(Plan.PRO_PLUS, states)
        assert result.passed, _format_failures(result)

    # ------------------------------------------------------------------
    # Upgrade prompt validation
    # ------------------------------------------------------------------

    @pytest.mark.subscription
    def test_upgrade_prompt_present_for_gated_feature(
        self, authenticated_page: Page
    ) -> None:
        """For a known gated feature on Free plan, upgrade prompt must be visible."""
        if _current_plan() != Plan.FREE:
            pytest.skip("Skipped: upgrade prompts only apply on Free plan (set APPSHA_PLAN=free)")
        add_link = AddLinkPage(authenticated_page)
        # embed_link is gated on the Free plan
        assert add_link.has_upgrade_prompt("embed_link"), (
            "Expected an upgrade prompt for 'embed_link' on the Free plan"
        )

    # ------------------------------------------------------------------
    # Dynamic plan validation (uses APPSHA_PLAN env var)
    # ------------------------------------------------------------------

    @pytest.mark.subscription
    def test_current_plan_matches_expectations(self, authenticated_page: Page) -> None:
        """Validate all features against the plan set in APPSHA_PLAN (default: FREE_TRIAL)."""
        plan = _current_plan()
        add_link = AddLinkPage(authenticated_page)
        states = add_link.get_feature_states()
        validator = SubscriptionValidator()
        result = validator.validate(plan, states)
        assert result.passed, _format_failures(result)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _format_failures(result) -> str:  # type: ignore[no-untyped-def]
    lines = [f"Subscription validation FAILED for plan: {result.plan.value}"]
    for f in result.failures:
        lines.append(
            f"  {f.feature}: expected {f.expected.status.value}, "
            f"got {f.actual.status.value}"
        )
    return "\n".join(lines)
