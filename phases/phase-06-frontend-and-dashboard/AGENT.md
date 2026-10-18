# Phase 06 Agent Instructions — Child chat, session experience, and learning dashboard

## Goal

Deliver a clear, age-appropriate, accessible text-only experience that reflects server truth.

## Required behavior

Read the root `AGENTS.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/DEFINITION_OF_DONE.md`, and any documents referenced below. Inspect the repository before editing. Implement **only Phase 06**. If prior-phase files are absent, report the missing prerequisite and create only the minimum current-phase deliverable that is safe; do not fake the gate result. Make changes in small increments and document assumptions.

## Implementation tasks

- Build the child-facing chat and responsive layout using Next.js App Router, TypeScript, Tailwind, and accessible primitives. Do not add voice input/output.
- Add straightforward loading/error states, a retry action that is idempotency-safe, concise child-readable error copy, and a way to stop/change activity. Avoid manipulative streaks, shame, pressure, or reward loops.
- Build the dashboard from backend progress APIs: current L1/L2/L3 level, skill-specific mastery, recent achievements, and recommended next activity. Clearly distinguish progress from unassessed skills.
- Use TanStack Query or the existing server-state pattern for requests and cache invalidation. Add Zustand only if measured state complexity requires it.
- Use optimistic updates only for reversible UI state; do not show level advancement/mastery as committed until the backend confirms it.
- Add parent/guardian-facing access/consent/data controls according to the agreed product requirements; do not expose administrative data to the child UI.
- Ensure all text content and interactive elements have keyboard access, appropriate labels, and readable contrast.

## Required tests and verification

- Run lint, type check, component tests, and production build.
- Add Playwright journey: new synthetic profile -> L1 chat -> activity evidence saved -> dashboard updated -> sign out/close -> resume and verify progress.
- Test conversation/engagement/support mode responses render without forcing a lesson UI.
- Test network error, empty response, fallback response, double-click submit, slow request, and session expiry.
- Run basic accessibility checks and verify no child identifiers or conversation history leak between accounts.

## Acceptance criteria

- [ ] The main child journey works end-to-end in a production-like environment.
- [ ] Dashboard values match committed backend state.
- [ ] No audio/voice features are present in scope.
- [ ] Frontend CI checks and required E2E test pass.

## Phase gate

Run from repository root:

```bash
python scripts/phase_gate.py --phase 6
```

The command must exit `0`; inspect the generated `artifacts/phase-gates/phase-06.json` report. If a check fails, fix the underlying issue and rerun it. Do not alter acceptance thresholds only to make the gate pass.

## Do not do

Do not rely on client-side level/mode values as authority; do not show uncommitted progress as final.

## Final report required from the coding agent

Return a concise report with: (1) files created/changed, (2) implementation summary, (3) exact test/gate commands and outcomes, (4) phase report path, (5) manual review still needed, and (6) known limitations. Never state that an unrun check passed.
