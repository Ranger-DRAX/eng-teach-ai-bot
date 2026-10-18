"""Unit tests for the deterministic interaction mode manager.

Parameterized against backend/tests/fixtures/mode_cases.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.orchestrator.mode_manager import ModeDecision, ModeManager

FIXTURE_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "mode_cases.json"


def load_mode_fixtures():
    with open(FIXTURE_PATH, encoding="utf-8") as f:
        cases = json.load(f)
    return [(case["case_id"], case) for case in cases]


@pytest.mark.parametrize("case_id,case", load_mode_fixtures())
def test_mode_fixture_cases(case_id: str, case: dict):
    inp = case["input"]
    expected = case["expected"]

    decision = ModeManager.select_mode(
        child_message=inp["child_message"],
        current_mode=inp.get("current_mode", "learning"),
        session_context=inp.get("session_context", {}),
    )

    assert decision.mode == expected["mode"], f"{case_id}: expected mode {expected['mode']}, got {decision.mode}"
    assert decision.reason == expected["reason"], f"{case_id}: expected reason {expected['reason']}, got {decision.reason}"
    assert decision.llm_needed == expected["llm_needed"], f"{case_id}: expected llm_needed {expected['llm_needed']}"

    # Verify banned diagnostic words in responses
    if "response_must_not_contain" in expected and decision.deterministic_response:
        for forbidden in expected["response_must_not_contain"]:
            assert forbidden.lower() not in decision.deterministic_response.lower(), (
                f"Forbidden diagnostic word '{forbidden}' found in response: {decision.deterministic_response}"
            )

    # Verify sentiment persistence safety rule
    if expected.get("sentiment_stored_permanently") is False:
        assert decision.metadata.get("sentiment_stored_permanently", False) is False


def test_explicit_stop_always_overrides_ongoing_exercise():
    """Child autonomy rule: Stop/break request must immediately exit to support mode."""
    decision = ModeManager.select_mode(
        child_message="I want to stop now please",
        current_mode="learning",
        session_context={"active_exercise": True, "turn_count": 15},
    )
    assert decision.mode == "support"
    assert decision.llm_needed is False
    assert decision.reason == "explicit_stop_request"


def test_support_mode_never_contains_diagnostic_language():
    """Ensure supportive responses never diagnose children with clinical terms."""
    decision = ModeManager.select_mode(
        child_message="I'm so frustrated, this is too hard!",
        current_mode="learning",
        session_context={"active_exercise": True},
    )
    assert decision.mode == "support"
    assert decision.deterministic_response is not None
    resp = decision.deterministic_response.lower()
    for forbidden in ["anxiety", "depression", "adhd", "disorder", "diagnosis", "pathology"]:
        assert forbidden not in resp
