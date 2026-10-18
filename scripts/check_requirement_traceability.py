#!/usr/bin/env python3
"""Validate Phase 1 requirement traceability CSV without third-party dependencies."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "docs" / "requirements-traceability.csv"
REQUIRED_HEADERS = ["requirement_id", "requirement", "acceptance_criteria", "test_reference", "status", "notes"]
ALLOWED_STATUS = {"planned", "implemented", "verified", "blocked", "manual-review-required"}


def main() -> int:
    if not CSV_PATH.is_file():
        print(f"FAIL: missing {CSV_PATH.relative_to(ROOT)}")
        return 1
    try:
        with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []
            if headers != REQUIRED_HEADERS:
                print(f"FAIL: CSV headers must be exactly: {', '.join(REQUIRED_HEADERS)}")
                print(f"Found: {', '.join(headers)}")
                return 1
            rows = list(reader)
    except (OSError, csv.Error) as exc:
        print(f"FAIL: cannot read traceability CSV: {exc}")
        return 1

    errors = []
    if not rows:
        errors.append("CSV contains no requirement rows")
    seen = set()
    for index, row in enumerate(rows, start=2):
        rid = (row.get("requirement_id") or "").strip()
        if not rid:
            errors.append(f"line {index}: requirement_id is empty")
        elif rid in seen:
            errors.append(f"line {index}: duplicate requirement_id {rid}")
        seen.add(rid)
        for field in ("requirement", "acceptance_criteria", "test_reference", "status"):
            if not (row.get(field) or "").strip():
                errors.append(f"line {index}: {field} is empty")
        status = (row.get("status") or "").strip().lower()
        if status and status not in ALLOWED_STATUS:
            errors.append(f"line {index}: unsupported status {status!r}")
        test_ref = (row.get("test_reference") or "").strip().lower()
        if test_ref in {"tbd", "todo", "none", "n/a"}:
            errors.append(f"line {index}: test_reference must identify planned or existing test/evidence")

    required_ids = {f"REQ-{i:03d}" for i in range(1, 11)}
    missing_ids = sorted(required_ids - seen)
    if missing_ids:
        errors.append("missing baseline IDs: " + ", ".join(missing_ids))

    if errors:
        print("FAIL: requirement traceability validation")
        for error in errors:
            print(f" - {error}")
        return 1
    print(f"PASS: {len(rows)} unique requirements; traceability fields and baseline IDs verified")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
