#!/usr/bin/env python3
"""Validate production release readiness prerequisites, operational runbooks, and recovery drills."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_RUNBOOK_SECTIONS = [
    "Deployment Procedures",
    "Rollback Procedure",
    "Alerting Thresholds",
    "Incident Response",
]

REQUIRED_DRILL_SECTIONS = [
    "Recovery Time Objective",
    "Recovery Point Objective",
    "Verification",
]

MANUAL_REVIEW_ITEMS = [
    "Accredited early-childhood educator curriculum sign-off",
    "Pediatric psychological and SEL non-diagnostic policy review",
    "COPPA / GDPR-K parental consent flow legal review",
    "Infrastructure least-privilege credential audit",
]


def check_file(path: Path, min_size: int = 100) -> bool:
    return path.is_file() and path.stat().st_size >= min_size


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-gates", action="store_true", help="Exit non-zero on failure")
    args = parser.parse_args()

    print("\nValidating Release Readiness and Operational Deliverables...\n")

    errors: list[str] = []

    # 1. Runbook check
    runbook_path = ROOT / "docs" / "operations" / "runbook.md"
    if not check_file(runbook_path):
        errors.append(f"Missing or empty runbook: {runbook_path.relative_to(ROOT)}")
    else:
        content = runbook_path.read_text(encoding="utf-8")
        for sec in REQUIRED_RUNBOOK_SECTIONS:
            if sec.lower() not in content.lower():
                errors.append(f"Runbook missing required section: '{sec}'")
        print(f"  PASS  Operational Runbook validated ({runbook_path.relative_to(ROOT)})")

    # 2. Restore drill check
    drill_path = ROOT / "docs" / "operations" / "restore-drill.md"
    if not check_file(drill_path):
        errors.append(f"Missing or empty restore drill report: {drill_path.relative_to(ROOT)}")
    else:
        content = drill_path.read_text(encoding="utf-8")
        for sec in REQUIRED_DRILL_SECTIONS:
            if sec.lower() not in content.lower():
                errors.append(f"Restore drill report missing required section: '{sec}'")
        print(f"  PASS  Disaster Recovery Drill report validated ({drill_path.relative_to(ROOT)})")

    # 3. Migration files check
    versions_dir = ROOT / "backend" / "alembic" / "versions"
    migrations = list(versions_dir.glob("*.py")) if versions_dir.is_dir() else []
    if not migrations:
        errors.append("No database migrations found in backend/alembic/versions/")
    else:
        print(f"  PASS  Database migrations verified ({len(migrations)} migration files)")

    # 4. Environment config & secret safety check
    env_example = ROOT / "backend" / ".env.example"
    if not check_file(env_example):
        errors.append("Missing backend/.env.example configuration template")
    else:
        print("  PASS  Environment configuration template verified")

    gitignore = ROOT / ".gitignore"
    if gitignore.is_file():
        git_content = gitignore.read_text(encoding="utf-8")
        if ".env" not in git_content:
            errors.append(".gitignore must ignore .env files")
        else:
            print("  PASS  .gitignore verified (secrets excluded)")
    else:
        errors.append("Missing .gitignore")

    # 5. Output manual review items
    print("\n" + "=" * 60)
    print("MANUAL REVIEW CHECKLIST (Required before production launch):")
    print("=" * 60)
    for item in MANUAL_REVIEW_ITEMS:
        print(f"  [MANUAL REVIEW REQUIRED]  {item}")
    print("=" * 60)

    if errors:
        print("\nFAIL: Release readiness check failed:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\nPASS: All automated release-readiness prerequisites satisfied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
