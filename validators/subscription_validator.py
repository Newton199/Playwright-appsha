"""
SubscriptionValidator: compares observed feature states against
plan-specific expectations and reports mismatches.
"""

from __future__ import annotations

from models import FeatureFailure, FeatureState, FeatureStatus, Plan, ValidationResult

# ---------------------------------------------------------------------------
# Shared FeatureState constants
# ---------------------------------------------------------------------------
_ENABLED = FeatureState(
    status=FeatureStatus.ENABLED,
    visible=True,
    enabled=True,
    has_upgrade_prompt=False,
)
_UPGRADE_PROMPT = FeatureState(
    status=FeatureStatus.UPGRADE_PROMPT,
    visible=True,
    enabled=False,
    has_upgrade_prompt=True,
)
_HIDDEN = FeatureState(
    status=FeatureStatus.HIDDEN,
    visible=False,
    enabled=False,
    has_upgrade_prompt=False,
)

# ---------------------------------------------------------------------------
# Plan expectations matrix
# Maps each Plan to the expected FeatureState for every feature key.
#
# | Feature       | FREE_TRIAL | FREE            | PRO    | PRO_PLUS |
# |---------------|------------|-----------------|--------|----------|
# | normal_link   | ENABLED    | ENABLED         | ENABLED| ENABLED  |
# | embed_link    | ENABLED    | UPGRADE_PROMPT  | ENABLED| ENABLED  |
# | attachment    | ENABLED    | UPGRADE_PROMPT  | ENABLED| ENABLED  |
# | external_shop | ENABLED    | HIDDEN          | HIDDEN | ENABLED  |
# | highlight     | ENABLED    | UPGRADE_PROMPT  | ENABLED| ENABLED  |
# | analytics     | ENABLED    | HIDDEN          | ENABLED| ENABLED  |
# ---------------------------------------------------------------------------
PLAN_EXPECTATIONS: dict[Plan, dict[str, FeatureState]] = {
    Plan.FREE_TRIAL: {
        "normal_link":   _ENABLED,
        "embed_link":    _ENABLED,
        "attachment":    _ENABLED,
        "external_shop": _ENABLED,
        "highlight":     _ENABLED,
        "analytics":     _ENABLED,
    },
    Plan.FREE: {
        "normal_link":   _ENABLED,
        "embed_link":    _UPGRADE_PROMPT,
        "attachment":    _UPGRADE_PROMPT,
        "external_shop": _HIDDEN,
        "highlight":     _UPGRADE_PROMPT,
        "analytics":     _HIDDEN,
    },
    Plan.PRO: {
        "normal_link":   _ENABLED,
        "embed_link":    _ENABLED,
        "attachment":    _ENABLED,
        "external_shop": _HIDDEN,
        "highlight":     _ENABLED,
        "analytics":     _ENABLED,
    },
    Plan.PRO_PLUS: {
        "normal_link":   _ENABLED,
        "embed_link":    _ENABLED,
        "attachment":    _ENABLED,
        "external_shop": _ENABLED,
        "highlight":     _ENABLED,
        "analytics":     _ENABLED,
    },
}


class SubscriptionValidator:
    """Validates that observed feature states match plan-level expectations."""

    def get_expected_states(self, plan: Plan) -> dict[str, FeatureState]:
        """Return the expected FeatureState per feature for the given plan.

        Args:
            plan: The subscription plan to look up.

        Returns:
            A dict mapping each feature key to its expected ``FeatureState``.
        """
        return PLAN_EXPECTATIONS[plan]

    def validate(
        self,
        plan: Plan,
        feature_states: dict[str, FeatureState],
    ) -> ValidationResult:
        """Compare actual feature states against expectations for *plan*.

        Iterates over every entry in *feature_states*, compares the actual
        ``status`` to the expected ``status`` for the given plan, and
        collects any mismatches into a ``failures`` list.

        Args:
            plan: The subscription plan to validate against.
            feature_states: Observed states from ``AddLinkPage.get_feature_states()``.

        Returns:
            A ``ValidationResult`` with ``passed=True`` iff every feature
            matches its expected status.
        """
        expected = self.get_expected_states(plan)
        failures: list[FeatureFailure] = []

        for feature, actual in feature_states.items():
            expected_state = expected.get(feature)
            if expected_state is None:
                continue  # unknown feature — skip rather than hard-fail
            if actual.status != expected_state.status:
                failures.append(
                    FeatureFailure(
                        feature=feature,
                        expected=expected_state,
                        actual=actual,
                    )
                )

        return ValidationResult(
            passed=len(failures) == 0,
            plan=plan,
            failures=failures,
        )
