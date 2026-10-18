# Architecture Decisions (ADRs)

## AD-001 — Backend-controlled progressive learning

The backend is the source of truth for L1/L2/L3, skill mastery, assessment evidence, and promotion rules. The LLM presents practice at the assigned level but does not advance a child. Promotion requires the configured skill prerequisites and evidence over time; missing evidence is not mastery.

## AD-002 — Backend-selected interaction mode

Supported modes: `learning`, `conversation`, `engagement`, `support`. The backend selects the mode using explicit intent, conversation state, and cautious text signals. A child's explicit stop/change request overrides lesson continuation. Emotional interpretation remains uncertain and temporary.

## AD-003 — One LLM call for each generative response

Known interactions use deterministic handlers. Otherwise, one provider call receives compact context, mode-specific guidance, SEL rules, and response constraints. There is no separate LLM call for mode routing and no automatic second LLM call when the first fails. A safe deterministic fallback is used on timeout/error.

## AD-004 — Durable personalization in PostgreSQL

PostgreSQL stores durable child learning progress and required session/history data. The system retrieves relevant context for each turn. Redis is optional for ephemeral state or measured performance improvements; it is not durable truth.

## AD-005 — Validated complete response before display

The MVP does not stream raw model tokens directly to the child. The complete candidate response must satisfy the response schema, length limits, and application safety checks before it is returned. Streaming may be considered later only with an explicit incremental validation design and separate acceptance tests.

## AD-006 — Latency SLO

Target P95 end-to-end completion latency < 2,000 ms under the workload defined in `docs/latency-budget.md`. The evaluation includes successful responses and fallbacks and separately reports model latency, errors, and fallback rate. The threshold is proven by measurement, not inferred from model marketing claims.

## AD-007 — Minimize child data

Collect only what is necessary for the learning service. Do not create a durable personality or mood profile. Use temporary state signals for current conversation handling and retain them only when there is a clear product need and approved retention rule. Parental consent, deletion, access control, and applicable legal review are release requirements.

## AD-008 — No unnecessary infrastructure on day one

Start without Redis, a vector database, multiple agents, or a task queue on the chat response path. Add infrastructure only for a documented need supported by measurements.

## AD-009 — Deterministic local safe fallbacks

When the external LLM provider times out (> 1,500 ms), returns HTTP 4xx/5xx, outputs malformed JSON, or fails deterministic safety filtering, the backend must immediately return an age-appropriate, pre-configured deterministic fallback string. No automated secondary LLM call or complex retry loop is permitted on the critical chat latency path. Every fallback turn must explicitly set `fallback_used: true` for auditability and SLO reporting.

## AD-010 — Idempotent turn submissions and abuse prevention

Interactive turn submissions (`POST /api/v1/chat/turn`) require client-supplied idempotency keys. Repeated transmissions of the same key within a 60-second window return the cached response, preventing duplicate assessment scoring, duplicate database writes, and runaway LLM costs. Endpoint payloads are capped at 2 KB and rate-limited to 30 requests/minute per session to mitigate denial-of-service risks.

