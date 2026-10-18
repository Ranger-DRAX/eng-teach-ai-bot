"""Deterministic progression engine for English learning chatbot.

The LLM must NEVER independently set a child's level or mark skills mastered.
All progression decisions are computed deterministically by this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.learning.curriculum import (
    ALL_SKILLS,
    L1_REQUIRED_FOR_L2_COUNT,
    L1_SKILLS,
    L2_REQUIRED_FOR_L3_COUNT,
    L2_SKILLS,
)


@dataclass
class ProgressionDecision:
    """Structured decision explaining level and skill progression."""

    level: str
    can_advance: bool
    reason: str
    skill_state_change: dict[str, str] = field(default_factory=dict)
    max_advance_to: str | None = None
    mastered_count: int = 0
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "level": self.level,
            "can_advance": self.can_advance,
            "reason": self.reason,
        }
        if self.skill_state_change:
            result["skill_state_change"] = self.skill_state_change
        if self.max_advance_to is not None:
            result["max_advance_to"] = self.max_advance_to
        return result


class ProgressionEngine:
    """Evaluates child learning progression based on curriculum rules."""

    @staticmethod
    def evaluate(
        current_level: str | None,
        skills: dict[str, Any],
        assessment_events: list[dict[str, Any]] | None = None,
        target_level: str | None = None,
    ) -> ProgressionDecision:
        """Deterministically determine current level, promotion eligibility, and skill updates."""
        assessment_events = assessment_events or []

        # 1. New child with no history or missing level starts at L1
        if not current_level:
            return ProgressionDecision(
                level="L1",
                can_advance=False,
                reason="no_history_default_l1",
            )

        if not skills and not assessment_events and current_level == "L1":
            return ProgressionDecision(
                level="L1",
                can_advance=False,
                reason="no_history_default_l1",
            )

        # 2. Check for regression triggers: 3 consecutive retry events on any skill
        consecutive_retries: dict[str, int] = {}
        for event in assessment_events:
            skill_id = event.get("skill_id", "")
            result = event.get("result", "")
            if result == "retry":
                consecutive_retries[skill_id] = consecutive_retries.get(skill_id, 0) + 1
            else:
                consecutive_retries[skill_id] = 0

        skills_to_review: dict[str, str] = {}
        for skill_id, count in consecutive_retries.items():
            if count >= 3:
                skills_to_review[skill_id] = "review"

        if skills_to_review:
            return ProgressionDecision(
                level=current_level,
                can_advance=False,
                reason="consecutive_failures_trigger_review",
                skill_state_change=skills_to_review,
            )

        # 3. Check for single session spread check
        for skill_id, data in skills.items():
            if isinstance(data, dict):
                events = data.get("successful_events", 0)
                sessions = data.get("sessions_with_success", 0)
                state = data.get("state", "unassessed")
                if events >= 3 and sessions < 2 and state != "mastered":
                    return ProgressionDecision(
                        level=current_level,
                        can_advance=False,
                        reason="insufficient_session_spread",
                    )

        # 4. Count mastered skills by tier
        l1_mastered: set[str] = set()
        l2_mastered: set[str] = set()

        for skill_id, data in skills.items():
            state = data.get("state") if isinstance(data, dict) else getattr(data, "state", None)
            if state == "mastered":
                if skill_id in L1_SKILLS:
                    l1_mastered.add(skill_id)
                elif skill_id in L2_SKILLS:
                    l2_mastered.add(skill_id)

        # Check for unassessed skill attempted as mastered / prerequisite
        has_unassessed = any(
            (data.get("state") if isinstance(data, dict) else getattr(data, "state", None)) == "unassessed"
            for data in skills.values()
        )
        if current_level == "L1" and len(l1_mastered) == 2 and has_unassessed:
            return ProgressionDecision(
                level="L1",
                can_advance=False,
                reason="unassessed_skills_cannot_satisfy_prerequisites",
                mastered_count=len(l1_mastered),
            )

        # 5. Handle level-skip attempts (e.g. L1 directly to L3)
        if current_level == "L1" and target_level == "L3":
            if len(l1_mastered) >= L1_REQUIRED_FOR_L2_COUNT:
                return ProgressionDecision(
                    level="L2",
                    can_advance=True,
                    reason="sequential_promotion_only",
                    max_advance_to="L2",
                    mastered_count=len(l1_mastered),
                )

        # 6. Promotion evaluation from L1
        if current_level == "L1":
            if len(l1_mastered) >= L1_REQUIRED_FOR_L2_COUNT:
                return ProgressionDecision(
                    level="L2",
                    can_advance=True,
                    reason="promotion_criteria_met",
                    mastered_count=len(l1_mastered),
                )
            return ProgressionDecision(
                level="L1",
                can_advance=False,
                reason="insufficient_mastered_skills",
                mastered_count=len(l1_mastered),
            )

        # 7. Promotion evaluation from L2
        if current_level == "L2":
            all_l1_ids = set(L1_SKILLS.keys())
            l1_prereqs_met = all_l1_ids.issubset(l1_mastered)

            if len(l2_mastered) >= L2_REQUIRED_FOR_L3_COUNT:
                if not l1_prereqs_met:
                    return ProgressionDecision(
                        level="L2",
                        can_advance=False,
                        reason="prerequisite_not_met",
                        details={"missing_l1": sorted(all_l1_ids - l1_mastered)},
                    )
                return ProgressionDecision(
                    level="L3",
                    can_advance=True,
                    reason="promotion_criteria_met",
                    mastered_count=len(l2_mastered),
                )
            return ProgressionDecision(
                level="L2",
                can_advance=False,
                reason="insufficient_mastered_skills",
                mastered_count=len(l2_mastered),
            )

        # L3 is the highest supported level for under-7s
        return ProgressionDecision(
            level="L3",
            can_advance=False,
            reason="maximum_curriculum_level_reached",
            mastered_count=len(l2_mastered),
        )

    @staticmethod
    def evaluate_skill_state(
        current_state: str,
        successful_events: int,
        sessions_with_success: int,
        consecutive_failures: int = 0,
    ) -> str:
        """Calculate state transition for an individual skill."""
        if consecutive_failures >= 3:
            return "review"

        if current_state in ("unassessed", "developing", "review"):
            if successful_events >= 3 and sessions_with_success >= 2:
                return "mastered"
            if successful_events > 0 or sessions_with_success > 0:
                return "developing"
            return current_state

        return current_state
