# Phase 04 Agent Instructions — Progression engine and interaction mode manager

## Goal

Implement the deterministic core that chooses learning difficulty and the interaction mode.

## Required behavior

Read the root `AGENTS.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/DEFINITION_OF_DONE.md`, and any documents referenced below. Inspect the repository before editing. Implement **only Phase 04**. If prior-phase files are absent, report the missing prerequisite and create only the minimum current-phase deliverable that is safe; do not fake the gate result. Make changes in small increments and document assumptions.

## Implementation tasks

- Implement the progression domain in `backend/app/learning/`. Load versioned curriculum rules and calculate eligibility from stored assessment evidence, required skills, and consistency criteria.
- Implement the mode manager in `backend/app/orchestrator/`. Prioritize explicit child intent, session context, current activity, and safe support/stop behavior.
- Use deterministic handlers for greetings, exercise answer checking, known commands, breaks, and predictable curriculum activities.
- For uncertain intent/mode, choose a safe and non-coercive default. Do not add a second LLM call for routing. Do not persist inferred mood as a stable child attribute.
- Emit a structured decision object explaining the rule/reason code internally (not hidden chain-of-thought), selected mode, current level, intended skill, and whether an LLM is needed.
- Ensure assessment scoring uses validated activity evidence and is idempotent. A repeated client request must not double-count a result.

## Required tests and verification

- Run unit tests from the progression and mode manager test modules.
- Parameterize tests from the Phase 2 fixture cases; test every transition and every listed mode case.
- Test explicit request to stop/change topic, missing history, ambiguous emotion, invalid input, duplicate submission, and level-skip attempts.
- Test that the decision object cannot mutate database progress until a valid assessment event is processed.

## Acceptance criteria

- [ ] Progression and mode selection can run without an LLM or network access.
- [ ] LLM output cannot set level/mode or mark a skill mastered.
- [ ] All required progression/mode fixtures pass and edge cases have regression coverage.
- [ ] The phase gate passes.

## Phase gate

Run from repository root:

```bash
python scripts/phase_gate.py --phase 4
```

The command must exit `0`; inspect the generated `artifacts/phase-gates/phase-04.json` report. If a check fails, fix the underlying issue and rerun it. Do not alter acceptance thresholds only to make the gate pass.

## Do not do

Do not make every user message a lesson; do not treat a single wrong answer or uncertain text sentiment as a durable diagnosis.

## Final report required from the coding agent

Return a concise report with: (1) files created/changed, (2) implementation summary, (3) exact test/gate commands and outcomes, (4) phase report path, (5) manual review still needed, and (6) known limitations. Never state that an unrun check passed.
