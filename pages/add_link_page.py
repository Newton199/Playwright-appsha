"""
AddLinkPage page object for the Appsha staging site.

Encapsulates all interactions and state inspection on the add-link page at
.../profiles/{id}/links/add-link, exposing per-feature visibility, enabled,
and upgrade-prompt checks, as well as a bulk feature-state collection method.

No time.sleep() calls are used — all waits are expressed via Playwright APIs.
"""

from playwright.sync_api import Page

from appsha_selectors import FEATURE_SELECTORS, UPGRADE_PROMPT_SELECTORS
from models import FeatureState, FeatureStatus

FEATURES = [
    "normal_link",
    "embed_link",
    "attachment",
    "external_shop",
    "highlight",
    "analytics",
]


class AddLinkPage:
    """Page object for the Appsha add-link page."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def is_feature_visible(self, feature: str) -> bool:
        """Return True if the feature element is visible on the page."""
        return self.page.locator(FEATURE_SELECTORS[feature]).first.is_visible()

    def is_feature_enabled(self, feature: str) -> bool:
        """Return True if the feature element is enabled (interactable).

        Returns False immediately if the element is not visible.
        """
        if not self.is_feature_visible(feature):
            return False
        return self.page.locator(FEATURE_SELECTORS[feature]).first.is_enabled()

    def has_upgrade_prompt(self, feature: str) -> bool:
        """Return True if an upgrade/upsell prompt is visible for the feature."""
        return self.page.locator(UPGRADE_PROMPT_SELECTORS[feature]).first.is_visible()

    def get_feature_states(self) -> dict[str, FeatureState]:
        """Collect and return the observable state for all 6 features."""
        states: dict[str, FeatureState] = {}

        for feature in FEATURES:
            visible = self.is_feature_visible(feature)
            enabled = self.is_feature_enabled(feature)
            has_upgrade = self.has_upgrade_prompt(feature)

            if not visible:
                status = FeatureStatus.HIDDEN
            elif has_upgrade:
                status = FeatureStatus.UPGRADE_PROMPT
            elif not enabled:
                status = FeatureStatus.DISABLED
            else:
                status = FeatureStatus.ENABLED

            states[feature] = FeatureState(
                status=status,
                visible=visible,
                enabled=enabled,
                has_upgrade_prompt=has_upgrade,
            )

        assert len(states) == 6, f"Expected 6 feature states, got {len(states)}"
        return states
