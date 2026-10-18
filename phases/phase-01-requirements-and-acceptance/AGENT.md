# Phase 01 Agent Instructions — Requirements, acceptance criteria, privacy, and architecture

## Goal

Create a testable contract for the application before substantial feature code is written.

## Required behavior

Read the root `AGENTS.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/DEFINITION_OF_DONE.md`, and any documents referenced below. Inspect the repository before editing. Implement **only Phase 01**. If prior-phase files are absent, report the missing prerequisite and create only the minimum current-phase deliverable that is safe; do not fake the gate result. Make changes in small increments and document assumptions.

## Implementation tasks

- Create `docs/requirements.md` with functional requirements: L1/L2/L3 learning, four interaction modes, SEL, contextual personalization, dashboard, parent/guardian controls, and safe session behavior.
- Create `docs/acceptance-criteria.md` with observable acceptance criteria and requirement IDs REQ-001 through REQ-010 (add IDs where needed). Avoid vague criteria such as “fast” or “safe”.
- Create `docs/data-retention.md`: data inventory, purpose, minimum retention, deletion behavior, parent/guardian access, and what will not be collected. Flag jurisdiction-specific privacy/legal review instead of claiming compliance.
- Create `docs/threat-model.md` covering child-data isolation, account/session abuse, prompt injection, unsafe model output, credential exposure, logging, provider outage, and denial-of-service/rate limits.
- Create `docs/latency-budget.md` defining measurement start/end, normal workload, concurrency, message mix, warm/cold behavior, environment/region, reporting, and P95 < 2000 ms. Mark workload assumptions for stakeholder approval.
- Create `docs/requirements-traceability.csv` using the supplied template, ensuring every requirement has measurable criteria and a test/evidence reference.
- Create/update `docs/ARCHITECTURE_DECISIONS.md` with any project-specific architecture decision records. Keep the backend as the source of truth for level and mode.
- List assumptions and unresolved decisions in `docs/open-questions.md`; make safe provisional choices instead of blocking the phase on nonessential questions.

## Required tests and verification

- Run `python scripts/check_requirement_traceability.py`.
- Check IDs are unique, fields are populated, status values are valid, each row names a test/evidence reference, and privacy/latency criteria are explicit.
- Human review: confirm the normal-load definition and the child-data/consent plan before claiming requirements are approved.

## Acceptance criteria

- [ ] All required documents exist and cross-reference the same requirement IDs.
- [ ] Latency is defined as complete validated response availability, not merely time-to-first-token.
- [ ] No document promises perfect safety, guaranteed LLM latency, or legal compliance without review.
- [ ] The traceability checker exits 0 and the phase gate report says PASS.

## Phase gate

Run from repository root:

```bash
python scripts/phase_gate.py --phase 1
```

The command must exit `0`; inspect the generated `artifacts/phase-gates/phase-01.json` report. If a check fails, fix the underlying issue and rerun it. Do not alter acceptance thresholds only to make the gate pass.

## Do not do

Do not build the whole application, introduce a vector database, or allow the LLM to control progress/mode.

## Final report required from the coding agent

Return a concise report with: (1) files created/changed, (2) implementation summary, (3) exact test/gate commands and outcomes, (4) phase report path, (5) manual review still needed, and (6) known limitations. Never state that an unrun check passed.
