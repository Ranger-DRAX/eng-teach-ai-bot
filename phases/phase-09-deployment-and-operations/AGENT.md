# Phase 09 Agent Instructions — Production deployment, monitoring, backup recovery, and rollback

## Goal

Make releases observable, recoverable, secure, and maintainable.

## Required behavior

Read the root `AGENTS.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/DEFINITION_OF_DONE.md`, and any documents referenced below. Inspect the repository before editing. Implement **only Phase 09**. If prior-phase files are absent, report the missing prerequisite and create only the minimum current-phase deliverable that is safe; do not fake the gate result. Make changes in small increments and document assumptions.

## Implementation tasks

- Create `docs/operations/runbook.md` for deployment, alerts, incident triage, provider outage, database outage, key rotation, data deletion, and escalation.
- Create documented readiness checks for environment configuration, secret handling, TLS, access controls, rate limits, backups, log redaction, monitoring, and rollback.
- Implement health/readiness checks, request IDs, structured metrics, dashboard/alert definitions for latency/error/fallback rates and provider spend.
- Configure least-privilege runtime credentials, separate dev/staging/prod projects, and no production credentials in CI pull requests.
- Create `scripts/check_release_readiness.py` that checks machine-verifiable release prerequisites and reports manual items as `MANUAL REVIEW REQUIRED` rather than passing silently.
- Create `docs/operations/restore-drill.md` and record a real restore drill against a disposable/staging dataset. Document recovery time and data-loss window objectives approved by the project owner.
- Use a gradual rollout/rollback plan; database migrations must be backward-compatible with the application during the rollout or have an explicit coordinated deploy plan.

## Required tests and verification

- Run automated release-readiness checks.
- Perform a database backup restore drill and verify progress/session integrity using synthetic data.
- Rehearse rollback to the prior application version and test health/alert behavior during a controlled outage.
- Verify secrets do not appear in logs, client bundles, source maps, or CI artifacts.
- Check that alert thresholds have been exercised with synthetic incidents, not merely created.

## Acceptance criteria

- [ ] Runbooks and evidence exist; backup recovery and rollback were actually rehearsed.
- [ ] Monitoring distinguishes latency, errors, provider failures, fallback rate, and cost.
- [ ] No critical/high security finding remains and all required manual reviews are signed off.
- [ ] The phase gate passes without treating missing operational evidence as success.

## Phase gate

Run from repository root:

```bash
python scripts/phase_gate.py --phase 9
```

The command must exit `0`; inspect the generated `artifacts/phase-gates/phase-09.json` report. If a check fails, fix the underlying issue and rerun it. Do not alter acceptance thresholds only to make the gate pass.

## Do not do

Do not claim a backup is recoverable merely because a scheduled backup job reports success.

## Final report required from the coding agent

Return a concise report with: (1) files created/changed, (2) implementation summary, (3) exact test/gate commands and outcomes, (4) phase report path, (5) manual review still needed, and (6) known limitations. Never state that an unrun check passed.
