"""Unit tests for the deterministic progression engine.

Parameterized against backend/tests/fixtures/progression_cases.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.learning.curriculum import ALL_SKILLS, L1_SKILLS, L2_SKILLS
from app.learning.progression import ProgressionDecision, ProgressionEngine

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "progression_cases.json"


def load_progression_fixtures():
    with open(FIXTURE_PATH, encoding="utf-8") as f:
        cases = json.load(f)
    return [(case["case_id"], case) for case in cases]


@pytest.mark.parametrize("case_id,case", load_progression_fixtures())
def test_progression_fixture_cases(case_id: str, case: dict):
    inp = case["input"]
    expected = case["expected"]

    decision = ProgressionEngine.evaluate(
        current_level=inp.get("current_level"),
        skills=inp.get("skills", {}),
        assessment_events=inp.get("assessment_events", []),
        target_level=inp.get("target_level"),
    )

    assert decision.level == expected["level"], f"{case_id}: expected level {expected['level']}, got {decision.level}"
    assert decision.can_advance == expected["can_advance"], f"{case_id}: expected can_advance {expected['can_advance']}"
    assert decision.reason == expected["reason"], f"{case_id}: expected reason {expected['reason']}, got {decision.reason}"

    if "skill_state_change" in expected:
        assert decision.skill_state_change == expected["skill_state_change"]

    if "max_advance_to" in expected:
        assert decision.max_advance_to == expected["max_advance_to"]


def test_level_skipping_strictly_prohibited():
    """Ensure a child at L1 cannot jump directly to L3 even with many skills."""
    mock_skills = {skill: {"state": "mastered", "successful_events": 10, "sessions_with_success": 5} for skill in L1_SKILLS}
    decision = ProgressionEngine.evaluate(current_level="L1", skills=mock_skills, target_level="L3")
    assert decision.level == "L2"
    assert decision.max_advance_to == "L2"
    assert decision.can_advance is True


def test_unassessed_skills_never_count_as_mastered():
    """Ensure skills in 'unassessed' state are never counted toward promotion criteria."""
    skills = {
        "l1_colors": {"state": "mastered", "successful_events": 3, "sessions_with_success": 2},
        "l1_animals": {"state": "mastered", "successful_events": 3, "sessions_with_success": 2},
        "l1_numbers": {"state": "unassessed", "successful_events": 0, "sessions_with_success": 0},
    }
    decision = ProgressionEngine.evaluate(current_level="L1", skills=skills)
    assert decision.level == "L1"
    assert decision.can_advance is False
    assert decision.reason == "unassessed_skills_cannot_satisfy_prerequisites"


def test_consecutive_mistakes_trigger_review_state():
    """Ensure 3 consecutive failures trigger review."""
    events = [
        {"skill_id": "l1_colors", "result": "retry"},
        {"skill_id": "l1_colors", "result": "retry"},
        {"skill_id": "l1_colors", "result": "retry"},
    ]
    decision = ProgressionEngine.evaluate(
        current_level="L2",
        skills={"l1_colors": {"state": "mastered"}},
        assessment_events=events,
    )
    assert decision.can_advance is False
    assert decision.skill_state_change == {"l1_colors": "review"}
    assert decision.reason == "consecutive_failures_trigger_review"


def test_decision_is_pure_function_without_side_effects():
    """Ensure ProgressionEngine.evaluate does not mutate input dictionaries."""
    skills = {"l1_colors": {"state": "developing", "successful_events": 2, "sessions_with_success": 1}}
    skills_copy = json.loads(json.dumps(skills))
    decision = ProgressionEngine.evaluate(current_level="L1", skills=skills)
    assert isinstance(decision, ProgressionDecision)
    assert skills == skills_copy
