#!/usr/bin/env python3
"""Validate the Phase 2 synthetic progression and mode scenario fixtures."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROGRESSION_PATH = ROOT / "backend" / "tests" / "fixtures" / "progression_cases.json"
MODE_PATH = ROOT / "backend" / "tests" / "fixtures" / "mode_cases.json"
EXPECTED_PROGRESSION = {
    "new_child_starts_l1",
    "insufficient_evidence_stays_level",
    "advance_l1_to_l2",
    "advance_l2_to_l3",
    "missing_prerequisite_blocks_advance",
    "cannot_skip_levels",
    "unassessed_is_not_mastered",
    "repeated_mistakes_offer_review",
}
EXPECTED_MODES = {
    "explicit_learning_request",
    "topic_share_is_conversation",
    "explicit_game_request",
    "explicit_break_request",
    "possible_frustration_supportive_not_diagnostic",
    "ambiguous_mood_not_stored_as_fact",
    "change_topic_overrides_lesson",
    "ordinary_message_not_forced_into_quiz",
}
VALID_LEVELS = {"L1", "L2", "L3"}
VALID_MODES = {"learning", "conversation", "engagement", "support"}


def load_cases(path: Path):
    if not path.is_file():
        raise ValueError(f"Missing fixture: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise ValueError(f"{path.relative_to(ROOT)} must be a non-empty JSON array")
    seen = set()
    for idx, case in enumerate(data):
        if not isinstance(case, dict):
            raise ValueError(f"{path.name}[{idx}] must be an object")
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"{path.name}[{idx}] has no case_id")
        if case_id in seen:
            raise ValueError(f"{path.name}: duplicate case_id {case_id}")
        seen.add(case_id)
        for key in ("description", "input", "expected"):
            if key not in case:
                raise ValueError(f"{path.name}[{idx}] missing key {key}")
    return data, seen


def main() -> int:
    try:
        progression, p_ids = load_cases(PROGRESSION_PATH)
        modes, m_ids = load_cases(MODE_PATH)
        missing_p = sorted(EXPECTED_PROGRESSION - p_ids)
        missing_m = sorted(EXPECTED_MODES - m_ids)
        errors = []
        if missing_p:
            errors.append("Missing progression scenario IDs: " + ", ".join(missing_p))
        if missing_m:
            errors.append("Missing mode scenario IDs: " + ", ".join(missing_m))
        for case in progression:
            expected = case["expected"]
            if isinstance(expected, dict) and "level" in expected and expected["level"] not in VALID_LEVELS:
                errors.append(f"{case['case_id']}: invalid expected level {expected['level']!r}")
        for case in modes:
            expected = case["expected"]
            if isinstance(expected, dict) and "mode" in expected and expected["mode"] not in VALID_MODES:
                errors.append(f"{case['case_id']}: invalid expected mode {expected['mode']!r}")
        for doc in (ROOT / "docs/curriculum.md", ROOT / "docs/progression-rules.md", ROOT / "docs/mode-policy.md"):
            if not doc.is_file() or doc.stat().st_size < 100:
                errors.append(f"Missing or incomplete document: {doc.relative_to(ROOT)}")
        if errors:
            print("FAIL: curriculum specification validation")
            for error in errors:
                print(f" - {error}")
            return 1
        print(f"PASS: {len(progression)} progression cases and {len(modes)} mode cases validated")
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
