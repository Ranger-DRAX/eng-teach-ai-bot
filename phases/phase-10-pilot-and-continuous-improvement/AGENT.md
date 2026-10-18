# Phase 10 Agent Instructions — Controlled pilot, educational evaluation, and sustainable improvement

## Goal

Validate educational usefulness and establish a safe ongoing release/evaluation cycle.

## Required behavior

Read the root `AGENTS.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/DEFINITION_OF_DONE.md`, and any documents referenced below. Inspect the repository before editing. Implement **only Phase 10**. If prior-phase files are absent, report the missing prerequisite and create only the minimum current-phase deliverable that is safe; do not fake the gate result. Make changes in small increments and document assumptions.

## Implementation tasks

- Create a pilot plan defining cohort boundaries, guardian consent, supervision, data-minimization, support/escalation, stop criteria, and incident reporting. Obtain applicable privacy/legal/educational review before involving children.
- Begin with synthetic scenarios and adult-led walkthroughs. Any child pilot must be approved and consented; do not recruit or collect child data as part of ordinary development.
- Create an evaluation report measuring pre/post skill evidence where appropriate, level-transition accuracy, mode selection, response quality, latency, failure rate, fallback rate, and cost. Avoid unsupported causal claims from a tiny sample.
- Build a feedback loop where educators/guardians can report a problem without exposing unnecessary child conversation data.
- Create `docs/continuous-improvement.md` describing versioned curriculum/prompt/model changes, regression gates, dependency updates, issue triage, deprecation, and data export/deletion.
- Implement `scripts/evaluate_pilot.py --check-gates` to validate that the report includes the agreed metrics, sample limitations, approvals, unresolved issues, and go/no-go decision.
- Only tune thresholds or prompts through reviewed changes. Every production model/prompt update reruns the relevant regression, safety, and latency evaluations.

## Required tests and verification

- Run all CI and phase-gate checks for Phases 1–9 at the candidate release commit.
- Validate the pilot report structure and that privacy/safety approvals are present before an actual pilot is marked ready.
- Run a final synthetic full journey, data deletion check, latency benchmark, and restore/rollback evidence review.
- Have humans review educational quality, SEL behavior, safeguarding, and whether evaluation limitations are communicated accurately.

## Acceptance criteria

- [ ] Pilot evaluation is documented and separates measured findings from assumptions.
- [ ] No child pilot begins without the required approvals and parental/guardian process.
- [ ] Go/no-go is explicit with unresolved risks, owners, and follow-up dates.
- [ ] The continuous-improvement process can reproduce evaluations for future releases.

## Phase gate

Run from repository root:

```bash
python scripts/phase_gate.py --phase 10
```

The command must exit `0`; inspect the generated `artifacts/phase-gates/phase-10.json` report. If a check fails, fix the underlying issue and rerun it. Do not alter acceptance thresholds only to make the gate pass.

## Do not do

Do not equate engagement or time-in-app with English learning gains, or use child data beyond the documented purpose.

## Final report required from the coding agent

Return a concise report with: (1) files created/changed, (2) implementation summary, (3) exact test/gate commands and outcomes, (4) phase report path, (5) manual review still needed, and (6) known limitations. Never state that an unrun check passed.
