# Phase 07 Agent Instructions — Comprehensive reliability, security, and child-safety evaluation

## Goal

Exercise failures and misuse deliberately before performance and deployment sign-off.

## Required behavior

Read the root `AGENTS.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/DEFINITION_OF_DONE.md`, and any documents referenced below. Inspect the repository before editing. Implement **only Phase 07**. If prior-phase files are absent, report the missing prerequisite and create only the minimum current-phase deliverable that is safe; do not fake the gate result. Make changes in small increments and document assumptions.

## Implementation tasks

- Consolidate unit, integration, E2E, security, and model-evaluation suites. Add a versioned synthetic safety scenario set and a reproducible offline safety-evaluation runner.
- Cover prompt injection, attempts to elicit sensitive data, unsafe/off-topic content, inappropriate attachment or pasted content if supported, coercive/overly dependent language, and attempts to override parent/guardian rules.
- Add rate limiting, input size limits, safe error responses, timeouts, idempotency behavior, dependency/security checks, and verified authorization rules.
- Create an evaluation report that separates automated checks from human review. Do not claim automated moderation is perfect; document residual risks and mitigation.
- Add data deletion/retention tests across PostgreSQL and any cache. Confirm logs are redacted and test fixtures are synthetic.
- Enforce test coverage target from `docs/DEFINITION_OF_DONE.md` and ensure critical progression/authorization/mode scenarios have explicit tests.

## Required tests and verification

- Run full backend and frontend suites, E2E tests, coverage, and offline safety evaluations.
- Run dependency and secret scanning; triage findings and fix critical/high issues.
- Run authorization/isolation tests, deletion tests, malformed input tests, and provider/database failure tests.
- Have a qualified adult reviewer assess a documented sample of SEL and child-directed outputs before any child pilot.
- Keep live LLM safety evaluation opt-in, synthetic, rate-limited, and protected by staging credentials.

## Acceptance criteria

- [ ] No unresolved critical/high security issues at the release gate.
- [ ] All automated tests pass; required coverage and scenario thresholds pass.
- [ ] Human review is recorded for child-safety, SEL, privacy, and educational content.
- [ ] Failures produce a safe result and no corrupted or cross-child data.

## Phase gate

Run from repository root:

```bash
python scripts/phase_gate.py --phase 7
```

The command must exit `0`; inspect the generated `artifacts/phase-gates/phase-07.json` report. If a check fails, fix the underlying issue and rerun it. Do not alter acceptance thresholds only to make the gate pass.

## Do not do

Do not use the green status from a mocked LLM test as proof that all live model responses are safe.

## Final report required from the coding agent

Return a concise report with: (1) files created/changed, (2) implementation summary, (3) exact test/gate commands and outcomes, (4) phase report path, (5) manual review still needed, and (6) known limitations. Never state that an unrun check passed.
