# Definition of Done and Release Gates

## Automated checks

### Backend

- `python -m ruff check .`
- `python -m ruff format --check .`
- `python -m mypy app`
- `python -m pytest -q` (coverage reporting configured by the project)
- Alembic migrations apply cleanly to a disposable PostgreSQL test database.

### Frontend

- `npm run lint`
- `npm run typecheck`
- `npm run test:ci`
- `npm run build`
- `npm run test:e2e` after the frontend phase introduces Playwright.

### Phase-specific

- Run `python scripts/phase_gate.py --phase N`.
- Inspect `artifacts/phase-gates/phase-NN.json`.
- For Phase 8, run the benchmark against the designated staging environment; local unit tests do not prove the latency SLO.
- For Phase 9, complete an evidenced backup/restore drill and rollback rehearsal.
- For Phase 10, require a signed-off evaluation report and approved pilot/privacy procedures.

## Quality policies

- Overall unit/integration test coverage target: at least 80% once Phase 7 is reached. Critical authorization, progression, and mode-transition paths must have explicit scenario coverage even if aggregate coverage is higher.
- Tests must use synthetic accounts and deterministic fake LLM responses unless a live model evaluation is explicitly requested and run in a protected staging environment.
- No critical/high unresolved security findings at release. Document accepted medium/low findings with an owner and deadline.
- No credentials or raw sensitive child data in logs, fixtures, screenshots, issue reports, or CI artifacts.
- Every bug fix gets a regression test.
- Human-reviewed evidence remains required for child safety, SEL quality, privacy/legal readiness, and educational outcomes.

## Phase status

A status report must distinguish `PASS`, `FAIL`, and `MANUAL REVIEW REQUIRED`. Do not relabel a manual item as passed because a unit test is green.
