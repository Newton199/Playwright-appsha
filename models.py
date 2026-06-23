"""
Data models for the Appsha Playwright automation suite.

Defines enums and dataclasses used across page objects, validators,
and test files to represent feature states, subscription plans, and
validation results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class FeatureStatus(Enum):
    """Represents the observable status of a feature on the add-link page."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    HIDDEN = "hidden"
    UPGRADE_PROMPT = "upgrade_prompt"


class Plan(Enum):
    """Represents the available subscription plans for an Appsha account."""

    FREE_TRIAL = "free_trial"
    FREE = "free"
    PRO = "pro"
    PRO_PLUS = "pro_plus"


@dataclass
class FeatureState:
    """Captures the complete observable state of a single feature on the add-link page.

    Attributes:
        status: The high-level status derived from visibility, enabled state,
                and presence of an upgrade prompt.
        visible: Whether the feature element is present and visible in the DOM.
        enabled: Whether the feature element is interactable (not disabled).
        has_upgrade_prompt: Whether an upgrade/upsell prompt is displayed for
                            this feature.
    """

    status: FeatureStatus
    visible: bool
    enabled: bool
    has_upgrade_prompt: bool


@dataclass
class FeatureFailure:
    """Describes a mismatch between the expected and actual state of a feature.

    Attributes:
        feature: The feature key (e.g. ``"embed_link"``, ``"analytics"``).
        expected: The expected ``FeatureState`` for the plan under test.
        actual: The ``FeatureState`` observed on the page.
    """

    feature: str
    expected: FeatureState
    actual: FeatureState


@dataclass
class ValidationResult:
    """The outcome of a subscription-gating validation run.

    Attributes:
        passed: ``True`` if every feature matched its expected state;
                ``False`` if one or more mismatches were found.
        plan: The ``Plan`` that was validated against.
        failures: List of ``FeatureFailure`` instances describing each
                  mismatch. Empty when ``passed`` is ``True``.
    """

    passed: bool
    plan: Plan
    failures: list[FeatureFailure] = field(default_factory=list)
