#!/usr/bin/env python3
"""Phase deliverable gate: check required artifacts, run phase checks, save a JSON report."""
from __future__ import annotations
import argparse
import datetime as dt
import glob
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

PHASES = {
  1: {
    "title": "Requirements and acceptance criteria",
    "paths": ["docs/requirements.md", "docs/acceptance-criteria.md", "docs/data-retention.md", "docs/threat-model.md", "docs/latency-budget.md", "docs/requirements-traceability.csv"],
    "commands": [{"cwd": ".", "args": [PY, "scripts/check_requirement_traceability.py"]}],
  },
  2: {
    "title": "Curriculum and policy specification",
    "paths": ["docs/curriculum.md", "docs/progression-rules.md", "docs/mode-policy.md", "backend/tests/fixtures/progression_cases.json", "backend/tests/fixtures/mode_cases.json", "scripts/check_curriculum_spec.py"],
    "commands": [{"cwd": ".", "args": [PY, "scripts/check_curriculum_spec.py"]}],
  },
  3: {
    "title": "Project foundation and data layer",
    "paths": ["backend/app/main.py", "backend/pyproject.toml", "backend/alembic.ini", "backend/alembic/versions/*.py", "frontend/package.json", "frontend/package-lock.json", ".github/workflows/quality.yml"],
    "commands": [
      {"cwd": "backend", "args": [PY, "-m", "ruff", "check", "."]},
      {"cwd": "backend", "args": [PY, "-m", "ruff", "format", "--check", "."]},
      {"cwd": "backend", "args": [PY, "-m", "mypy", "app"]},
      {"cwd": "backend", "args": [PY, "-m", "alembic", "upgrade", "head"]},
      {"cwd": ".", "args": [PY, "-m", "pytest", "backend/tests", "-q"]},
      {"cwd": "frontend", "args": ["npm", "run", "lint"]},
      {"cwd": "frontend", "args": ["npm", "run", "typecheck"]},
      {"cwd": "frontend", "args": ["npm", "run", "test:ci"]},
      {"cwd": "frontend", "args": ["npm", "run", "build"]},
    ],
  },
  4: {
    "title": "Progression and mode engine",
    "paths": ["backend/app/learning/progression.py", "backend/app/orchestrator/mode_manager.py", "backend/tests/unit/test_progression.py", "backend/tests/unit/test_mode_manager.py"],
    "commands": [{"cwd": ".", "args": [PY, "-m", "pytest", "backend/tests/unit/test_progression.py", "backend/tests/unit/test_mode_manager.py", "-q"]}],
  },
  5: {
    "title": "LLM context and safety integration",
    "paths": ["backend/app/llm/provider.py", "backend/app/llm/response_service.py", "backend/app/context/context_builder.py", "backend/app/safety/output_validator.py", "backend/tests/unit/test_context_builder.py", "backend/tests/unit/test_llm_response_service.py"],
    "commands": [{"cwd": ".", "args": [PY, "-m", "pytest", "backend/tests/unit/test_context_builder.py", "backend/tests/unit/test_llm_response_service.py", "-q"]}],
  },
  6: {
    "title": "Frontend and dashboard",
    "paths": ["frontend/src/app/chat/page.tsx", "frontend/src/app/dashboard/page.tsx", "frontend/tests/e2e/child-journey.spec.ts", "frontend/playwright.config.ts"],
    "commands": [
      {"cwd": "frontend", "args": ["npm", "run", "lint"]},
      {"cwd": "frontend", "args": ["npm", "run", "typecheck"]},
      {"cwd": "frontend", "args": ["npm", "run", "test:ci"]},
      {"cwd": "frontend", "args": ["npm", "run", "build"]},
      {"cwd": "frontend", "args": ["npm", "run", "test:e2e"]},
    ],
  },
  7: {
    "title": "Comprehensive quality and safety",
    "paths": ["backend/tests/safety/test_policy_eval.py", "backend/tests/safety/scenarios.jsonl", "docs/safety-evaluation.md", "scripts/run_safety_eval.py"],
    "commands": [
      {"cwd": ".", "args": [PY, "-m", "pytest", "backend/tests", "-q"]},
      {"cwd": ".", "args": [PY, "scripts/run_safety_eval.py", "--mode", "offline", "--check-thresholds"]},
    ],
  },
  8: {
    "title": "Latency and load",
    "paths": ["scripts/measure_latency.py", "docs/performance/latency-report.md"],
    "commands": [{"cwd": ".", "args": [PY, "scripts/measure_latency.py", "--check-slo"]}],
  },
  9: {
    "title": "Deployment and operations",
    "paths": ["scripts/check_release_readiness.py", "docs/operations/runbook.md", "docs/operations/restore-drill.md"],
    "commands": [{"cwd": ".", "args": [PY, "scripts/check_release_readiness.py", "--check-gates"]}],
  },
  10: {
    "title": "Pilot and continuous improvement",
    "paths": ["scripts/evaluate_pilot.py", "docs/pilot/evaluation-report.md", "docs/continuous-improvement.md"],
    "commands": [{"cwd": ".", "args": [PY, "scripts/evaluate_pilot.py", "--check-gates"]}],
  },
}


def path_exists(pattern: str) -> bool:
    p = ROOT / pattern
    if any(ch in pattern for ch in "*?[]"):
        return bool(glob.glob(str(p), recursive=True))
    return p.exists()


def redact(s: str) -> str:
    # Redact common secret-shaped values if a subprocess happens to print one.
    import re
    s = re.sub(r"(?i)(api[_-]?key|token|secret|password|authorization)(\s*[=:]\s*)[^\s,;]+", r"\1\2[REDACTED]", s)
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", type=int, help="Phase number 1–10")
    parser.add_argument("--list", action="store_true", help="List all phase gates")
    args = parser.parse_args()
    if args.list:
        for n, spec in PHASES.items():
            print(f"{n:02d}  {spec['title']}")
        return 0
    if args.phase not in PHASES:
        parser.error("provide --phase 1..10, or use --list")

    n = args.phase
    spec = PHASES[n]
    started = time.monotonic()
    started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    missing = [p for p in spec["paths"] if not path_exists(p)]
    results = []
    print(f"\nPHASE {n:02d}: {spec['title']}")
    print("=" * (len(spec['title']) + 9))
    if missing:
        print("Missing required deliverables:")
        for p in missing:
            print(f"  FAIL  {p}")
    else:
        print("Required deliverables: PASS")

    if missing:
        print("\nCommands not run because required deliverables are missing.")
    else:
        for item in spec["commands"]:
            cmd = item["args"]
            cwd = ROOT / item.get("cwd", ".")
            display = " ".join(shlex.quote(str(x)) for x in cmd)
            print(f"\n$ (cd {cwd.relative_to(ROOT)} && {display})")
            command_start = time.monotonic()
            try:
                proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=900)
                output = redact(proc.stdout or "")
                err = redact(proc.stderr or "")
                if output:
                    print(output[-10000:])
                if err:
                    print(err[-10000:], file=sys.stderr)
                status = "PASS" if proc.returncode == 0 else "FAIL"
                results.append({"command": display, "cwd": item.get("cwd", "."), "exit_code": proc.returncode, "status": status, "duration_seconds": round(time.monotonic() - command_start, 3)})
                print(f"{status}: exit code {proc.returncode}")
            except subprocess.TimeoutExpired:
                results.append({"command": display, "cwd": item.get("cwd", "."), "exit_code": None, "status": "FAIL", "error": "timeout after 900 seconds", "duration_seconds": round(time.monotonic() - command_start, 3)})
                print("FAIL: command timed out after 900 seconds", file=sys.stderr)
            except FileNotFoundError as exc:
                results.append({"command": display, "cwd": item.get("cwd", "."), "exit_code": None, "status": "FAIL", "error": str(exc), "duration_seconds": round(time.monotonic() - command_start, 3)})
                print(f"FAIL: command could not start: {exc}", file=sys.stderr)

    command_failures = [r for r in results if r["status"] != "PASS"]
    passed = not missing and not command_failures
    report = {
        "phase": n,
        "title": spec["title"],
        "status": "PASS" if passed else "FAIL",
        "started_at_utc": started_utc,
        "duration_seconds": round(time.monotonic() - started, 3),
        "missing_paths": missing,
        "commands": results,
        "note": "This report verifies configured files and commands only; human safety/privacy/educational review may still be required."
    }
    report_dir = ROOT / "artifacts" / "phase-gates"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"phase-{n:02d}.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nPHASE GATE: {'PASS' if passed else 'FAIL'}")
    print(f"Report: {report_path.relative_to(ROOT)}")
    if not passed:
        print("Do not mark this phase complete. Fix failures and rerun the gate.")
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
