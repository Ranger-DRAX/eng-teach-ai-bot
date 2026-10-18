# Phase 03 Agent Instructions — Project foundation, CI, API skeleton, and PostgreSQL schema

## Goal

Create a maintainable monorepo and reliable durable data layer before implementing full chatbot behavior.

## Required behavior

Read the root `AGENTS.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/DEFINITION_OF_DONE.md`, and any documents referenced below. Inspect the repository before editing. Implement **only Phase 03**. If prior-phase files are absent, report the missing prerequisite and create only the minimum current-phase deliverable that is safe; do not fake the gate result. Make changes in small increments and document assumptions.

## Implementation tasks

- Create `backend/` FastAPI application and `frontend/` Next.js App Router application with reproducible lockfiles and documented local setup.
- Configure Pydantic settings from environment variables, a safe `.env.example`, structured logs with correlation IDs, health/readiness endpoints, and clear error handling.
- Set up SQLAlchemy 2 async and Alembic migrations. Model the minimum necessary child/guardian relationship, learning progress, skill mastery, curriculum items, sessions, assessment evidence, and conversation turn metadata. Choose exact tables after the Phase 1 data inventory.
- Enforce child/session ownership at the repository/service boundary; do not rely on opaque IDs alone. Include timestamps and schema constraints where useful.
- Add unit/integration test configuration and GitHub Actions workflow. LLM calls must be mocked in CI.
- Add minimal API contracts for session creation/resume, sending a turn, reading progress, and parent-controlled data access/deletion. Do not expose child data through public unauthenticated endpoints.
- Use a disposable PostgreSQL test database for integration tests. Redis must remain optional at this phase.

## Required tests and verification

- Run the full backend lint, format, type-check, and test commands.
- Run frontend lint, type-check, unit tests, and production build.
- Run Alembic upgrade from an empty database and verify schema constraints; test migration forward from the previous revision when one exists.
- Test authorization with two synthetic child accounts and verify that cross-child reads/writes fail.
- Check `.gitignore` excludes local environment files, secrets, test outputs, and coverage artifacts.

## Acceptance criteria

- [ ] Fresh checkout instructions work without machine-specific paths or committed secrets.
- [ ] CI automatically runs relevant quality checks on push/pull request.
- [ ] Migrations apply to a disposable PostgreSQL database; integration tests do not use production data.
- [ ] All foundational quality checks pass.

## Phase gate

Run from repository root:

```bash
python scripts/phase_gate.py --phase 3
```

The command must exit `0`; inspect the generated `artifacts/phase-gates/phase-03.json` report. If a check fails, fix the underlying issue and rerun it. Do not alter acceptance thresholds only to make the gate pass.

## Do not do

Do not place long-running LLM calls inside database transactions or cache durable progress only in Redis.

## Final report required from the coding agent

Return a concise report with: (1) files created/changed, (2) implementation summary, (3) exact test/gate commands and outcomes, (4) phase report path, (5) manual review still needed, and (6) known limitations. Never state that an unrun check passed.
