# Global Agent Instructions — English Learning Chatbot

## 1. Product mission

Build a text-only English-learning chatbot for children under 7. It supports progressive English learning (L1/L2/L3), four interaction modes (Learning, Conversation, Engagement, Support), age-appropriate social and emotional learning (SEL), context-aware personalization, a learning dashboard, and a target P95 end-to-end response latency below 2 seconds under a documented normal workload.

## 2. Mandatory architectural decisions

1. **Backend owns progression.** L1/L2/L3, skill mastery, assessment rules, and level transitions are deterministic application logic. The LLM must never independently set a child's level, mark skills mastered, or write assessment results.
2. **Backend owns mode selection.** The mode manager selects `learning`, `conversation`, `engagement`, or `support` from explicit child intent, recent conversation context, and cautious text-based signals. A detected feeling is a tentative signal—not a diagnosis or permanent personality label.
3. **LLM generates language.** Use one LLM call for a generative response. Deterministic handlers should answer predictable tasks without an LLM call. Do not make a second LLM call for routing or automatic fallback on the latency-critical path.
4. **PostgreSQL is the source of truth.** Store progress, assessment evidence, curriculum references, session metadata, and only the conversation data needed for product functionality. Redis is optional and must not become the only copy of durable learning progress.
5. **Context is compact.** Retrieve only relevant skill data and recent conversation context; never send the child's entire history by default.
6. **Validate before display.** Parse/validate the model output, enforce length and content rules, then return it. Do not stream unvalidated model output to the child. The default MVP returns a complete validated response.
7. **Latency is an SLO, not an assumption.** Target P95 end-to-end latency below 2,000 ms under a defined normal workload. Report completion latency, time to first token if measured, error rate, timeout rate, and fallback rate separately.
8. **Safety and privacy are first-class requirements.** Require an adult/parent-consent design, data minimization, authorization checks per child record, retention/deletion controls, and safe fallbacks. Do not use real child data in development fixtures, CI, logs, or demos.

## 3. Technology baseline

- Frontend: Next.js App Router, React, TypeScript, Tailwind CSS; accessible UI primitives; TanStack Query where server-state caching helps. Add Zustand only if real shared client state requires it. Start with ordinary HTTP request/response; add text streaming only after measuring the UX benefit and designing safe incremental validation.
- Backend: supported Python 3.11+ runtime, FastAPI, Pydantic v2, SQLAlchemy 2 async, Alembic, Uvicorn.
- Data: supported managed PostgreSQL. Redis, task queues, vector databases, and multi-agent designs are optional future optimizations, not MVP dependencies.
- LLM: provider adapter around the official SDK; model ID is configuration (`LLM_MODEL` or provider-specific environment setting), not hard-coded in business logic. Use mock providers for deterministic CI tests.
- Testing: pytest/pytest-asyncio/httpx for backend; Ruff and type checking; Vitest/React Testing Library and TypeScript checks for frontend; Playwright for end-to-end flows. Use the tools already in the repository if equivalent and maintained; document substitutions.

## 4. Required engineering behavior

- Inspect the repository, current tests, and existing conventions before editing.
- Implement only the selected phase. Do not silently skip future-phase dependencies; write down blockers and continue with the smallest safe implementation for the current phase.
- Prefer small, typed modules and explicit domain models over a giant chat handler.
- Keep prompts, model adapters, progression logic, mode management, safety policy, and persistence separated.
- Use migrations for schema changes. Never silently modify production data or destructive database state.
- Use timeouts on network calls, bounded retries only for safe/idempotent operations, and request idempotency for turn submission where appropriate.
- Never log provider keys, auth tokens, raw consent documents, or unnecessary full child messages. Logs should use pseudonymous IDs and record redacted metadata.
- Validate ownership/authorization for every child/session/progress request. Do not trust IDs supplied by the client alone.
- Do not use child emotion or behavior labels for advertising, ranking, or unrelated profiling.
- No hard-coded secrets. Keep `.env` out of version control and maintain a safe `.env.example`.
- Do not mark TODOs, skipped tests, mocked model tests, or unexecuted staging checks as passed.

## 5. Default response contract

Keep the external API contract small and versioned. A successful chat turn should expose only necessary fields, e.g. `turn_id`, `response_text`, `mode`, `level`, `session_id`, `fallback_used`, and a server-side latency measurement. The backend—not the LLM—sets `mode`, `level`, and `fallback_used`.

The model should return a constrained response payload such as `{ "response_text": "..." }`. Reject malformed output. Do not let model output directly invoke tools, run code, change the database, modify the mode, advance a level, or bypass application policies.

## 6. Test and phase-gate rules

- Every behavioral change requires tests in the same change.
- Run the narrow test for the changed module, then run the selected phase gate:

  ```bash
  python scripts/phase_gate.py --phase N
  ```

- After Phase 3, the standard local checks should include backend lint/format/type checks/tests, frontend lint/type checks/tests/build, migrations against a disposable test database, and any phase-specific check.
- Unit tests must not call a paid external LLM. Mock the provider. Live provider evaluation is a separate, explicitly configured staging step.
- Add regression tests for every bug fix.
- Tests must be deterministic, use synthetic data, and clean up created state.
- The gate is failed if a required file/test is absent, a command fails, or a required manual evidence item is missing. Never change a threshold simply to make a failing test green; document and justify threshold changes.
- Do not suppress a failing check with `skip`, `xfail`, broad exceptions, disabled type checking, or weakening assertions without documenting and reviewing the reason.

## 7. Performance requirements

- Measure from the backend receiving a complete user message until the validated complete response is available to the frontend.
- The Phase 1 requirements must define normal workload (concurrency, message mix, warm/cold start treatment, region, and test duration). A sample staging profile is not a guarantee of global performance.
- P95 must be below 2,000 ms on the defined profile. Report p50/p95/p99, error rate, timeout rate, fallback rate, and successful-response rate.
- A fast fallback must not hide slow model calls: report model latency and fallback rate separately.
- Keep responses short enough for the educational context; avoid sequential calls, unnecessary RAG, and unnecessary database round trips.

## 8. Definition of done for any phase

A phase is complete only when:
1. Its phase-specific acceptance criteria are implemented.
2. Automated tests are added and pass.
3. The phase gate passes and its JSON report is inspected.
4. Security/privacy implications are reviewed.
5. Documentation and environment variables are updated.
6. The agent lists files changed, commands actually run, test outcomes, remaining risks, and any manual verification still required.

A successful build alone is not phase completion.
