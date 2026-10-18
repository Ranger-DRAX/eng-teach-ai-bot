# Observable Acceptance Criteria Specification

**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 1)  
**Scope:** Defines measurable, observable, and unambiguous pass/fail criteria for requirements REQ-001 through REQ-012.

> [!IMPORTANT]
> Acceptance criteria in this document avoid subjective terms such as "fast", "safe", or "user-friendly". Every criterion is verifiable via automated test suites, benchmarks, or structured operational inspection. In accordance with safety policies, no automated filter or probabilistic model can be guaranteed 100% error-free in all adversarial contexts; thresholds denote enforced gate criteria under documented test profiles.

---

## Acceptance Criteria by Requirement

### REQ-001: Deterministic Progressive Learning (L1, L2, L3)
* **AC-001.1 (Level Assignment):** A newly registered child with no assessment history is deterministically assigned to Level 1 (L1) upon initial session start.
* **AC-001.2 (Word Count Enforcement):** Responses generated for L1 contain no more than 15 words; L2 responses contain no more than 30 words; L3 responses contain no more than 50 words.
* **AC-001.3 (Backend Promotion Logic):** Advancing from L1 to L2 requires a minimum of 3 distinct skills in the `mastered` state recorded in PostgreSQL. Advancing from L2 to L3 requires all L1 skills and a minimum of 3 L2 skills in `mastered` state.
* **AC-001.4 (Mastery Evidence):** Transitioning any skill from `developing` to `mastered` requires at least 3 successful assessment events recorded across at least 2 distinct calendar days or sessions. Unassessed skills evaluate to `unassessed` and cannot satisfy prerequisites.
* **AC-001.5 (Independence from LLM):** If an LLM response payload suggests a level change (e.g., "You are now level 3!"), the backend ignores this text and does not modify the child's level record in PostgreSQL.
* **Verification Reference:** `backend/tests/unit/test_progression.py`

---

### REQ-002: Backend Interaction Mode Management
* **AC-002.1 (Intent-Based Mode Switching):** When child input matches a deterministic stop/break intent (e.g., "stop", "I'm done", "bye"), the backend transitions to `support` or ends the turn gracefully without presenting an educational exercise.
* **AC-002.2 (Game/Engagement Intent):** When child input includes explicit play/game intents (e.g., "let's play a game", "tell me a riddle"), the backend sets `mode` to `engagement` for that turn.
* **AC-002.3 (Conversation Preservation):** When `mode` is `conversation`, the backend prompt directs open-ended dialogue; the returned turn does not contain quiz questions, vocabulary tests, or phonics grading.
* **AC-002.4 (Deterministic Mode Assignment):** The HTTP turn response JSON payload includes a top-level `mode` attribute matching one of `["learning", "conversation", "engagement", "support"]` set exclusively by the backend mode manager.
* **Verification Reference:** `backend/tests/unit/test_mode_manager.py`

---

### REQ-003: Social and Emotional Learning (SEL) & Supportive Interaction
* **AC-003.1 (Frustration Handling):** When child input signals frustration or self-doubt (e.g., "too hard", "I can't do this", "I want to cry"), the backend routes the turn to `support` mode.
* **AC-003.2 (Non-Diagnostic Verification):** Generated support responses contain words of encouragement (e.g., "It is okay to take a break", "You did your best") and contain zero clinical, diagnostic, or psychological terms (e.g., "depression", "ADHD", "anxiety disorder", "trauma").
* **AC-003.3 (Ephemeral Sentiment State):** Sentiment markers (e.g., `detected_sentiment="frustrated"`) are held only in ephemeral turn memory; the PostgreSQL schema contains no permanent personality, mental health, or mood classification columns on the child profile.
* **Verification Reference:** `backend/tests/safety/test_sel_policy.py`

---

### REQ-004: Context-Aware Personalization & Compact State
* **AC-004.1 (Context Token Boundary):** Total assembled context passed to the LLM (including system prompt, target skill metadata, and recent dialogue) does not exceed 800 tokens.
* **AC-004.2 (Turn History Limit):** The context builder retrieves a maximum of 5 recent conversation turns for the active session. Prior session transcripts are excluded from prompt context.
* **AC-004.3 (Tenant Scoping):** The context builder query strictly includes `WHERE child_id = :active_child_id`. Unit tests verify that invoking context builder with `child_A` never retrieves records belonging to `child_B`.
* **Verification Reference:** `backend/tests/unit/test_context_builder.py`

---

### REQ-005: Durable Learning Progress in PostgreSQL
* **AC-005.1 (Persistence Across Sessions):** A session is terminated, and a subsequent new session is initiated for the same child; the child's active level, mastered skills list, and cumulative score match the exact state prior to termination.
* **AC-005.2 (Transactional Integrity):** A simulated crash or exception during turn processing rolls back the active transaction, ensuring no partial or corrupted skill updates exist in PostgreSQL.
* **AC-005.3 (Authoritative DB):** The system functions correctly with Redis disabled; progress queries execute against PostgreSQL.
* **Verification Reference:** `backend/tests/integration/test_progress_persistence.py`

---

### REQ-006: Child Privacy, Data Isolation, and Authorization
* **AC-006.1 (Authorization Check):** Any API request to `/api/v1/children/{child_id}/*` authenticated as guardian A querying child B (belonging to guardian B) returns HTTP 403 Forbidden or HTTP 404 Not Found.
* **AC-006.2 (PII Exclusion):** The child database model contains only `id`, `guardian_id`, `pseudonym`, `birth_month_year`, and `created_at`. No columns exist for full legal name, physical address, school, phone, or biometrics.
* **AC-006.3 (Parental Deletion SLA):** Calling `DELETE /api/v1/children/{child_id}` cascades deletion across all associated child records (sessions, turns, progress, assessments) in PostgreSQL, verifiable by zero remaining rows within 72 hours.
* **AC-006.4 (Log Redaction):** Log output inspections verify that authorization tokens, provider API keys, and raw child message strings are replaced with `[REDACTED]` or omitted.
* **Verification Reference:** `backend/tests/security/test_child_isolation.py`

---

### REQ-007: Complete Response Validation & Deterministic Fallbacks
* **AC-007.1 (Schema Conformance):** The response from the LLM provider is parsed into a Pydantic model requiring `{"response_text": str}`. If parsing fails, the raw string is discarded, and a fallback response is returned.
* **AC-007.2 (Safety Filter Rejection):** If a candidate response contains words from the banned vocabulary list (profanity, violence, adult topics) or exceeds the level word limit by > 10%, the validator rejects the candidate and returns a pre-configured safe fallback string.
* **AC-007.3 (Timeout Fallback):** When the LLM provider call exceeds 1,500 ms, the request is aborted, and a deterministic fallback response (e.g., "Let us try that again! What animal do you see?") is returned to the child with `fallback_used: true`.
* **AC-007.4 (No Raw Streaming):** The frontend receives only complete, validated payloads; HTTP responses are emitted with `Transfer-Encoding` standard chunked or buffered body only after full validation passes.
* **Verification Reference:** `backend/tests/safety/test_output_validation.py`

---

### REQ-008: End-to-End Latency Service Level Objective (SLO)
* **AC-008.1 (P95 Threshold):** Under a continuous 10-minute normal workload of 10 concurrent virtual child sessions (message mix: 60% learning, 25% conversation, 10% engagement, 5% support), the 95th percentile (P95) end-to-end response completion latency is strictly below 2,000 ms.
* **AC-008.2 (Measurement Boundaries):** Latency timing begins upon backend receipt of the final byte of the client HTTP request and stops when the final byte of the validated response is transmitted.
* **AC-008.3 (Disaggregated Reporting):** The performance report output generated by `scripts/measure_latency.py` outputs separate values for: total completion latency (p50, p95, p99), LLM provider latency, fallback rate, and HTTP 5xx error rate.
* **AC-008.4 (Fallback Independence):** If fallback rate exceeds 5.0% during the benchmark, the gate fails regardless of latency score.
* **Verification Reference:** `scripts/measure_latency.py`

---

### REQ-009: Child Learning Journey & Parent Dashboard
* **AC-009.1 (Child Chat UI):** An end-to-end browser journey verifies that a child user can submit a message, observe a visual loading indicator, receive a validated response, and view updated progress indicators.
* **AC-009.2 (Dashboard Data Consistency):** The parent dashboard accurately renders the exact number of mastered skills and active level returned by `/api/v1/children/{child_id}/dashboard`.
* **AC-009.3 (Accessibility):** The child chat interface achieves WCAG 2.1 AA compliance for text contrast (minimum 4.5:1) and keyboard navigability.
* **Verification Reference:** `frontend/tests/e2e/child-journey.spec.ts`

---

### REQ-010: Operational Recovery, Backup, and Migration Integrity
* **AC-010.1 (Reversible Migrations):** Running `alembic upgrade head` followed by `alembic downgrade base` and re-running `upgrade head` against an empty PostgreSQL database completes with exit code 0.
* **AC-010.2 (Restore Drill Verification):** A documented restore procedure executed against a database snapshot restores all child mastery and session records with zero loss of committed transactions.
* **Verification Reference:** `docs/operations/restore-drill.md`

---

### REQ-011: Parent/Guardian Account & Consent Management
* **AC-011.1 (Guardian Account Requirement):** Attempting to register a child profile without an authenticated guardian session returns HTTP 401 Unauthorized.
* **AC-011.2 (Explicit Consent Gate):** Child chat endpoints reject turn submissions with HTTP 403 until the guardian account has a recorded `consent_timestamp` and `consent_version` in PostgreSQL.
* **Verification Reference:** `backend/tests/security/test_guardian_consent.py`

---

### REQ-012: Safe Session Lifecycle & Abuse Prevention
* **AC-012.1 (Session Inactivity Timeout):** Submitting a turn to a session inactive for > 15 minutes returns a response terminating the session and prompting the child to restart.
* **AC-012.2 (Idempotent Submissions):** Submitting identical requests with the same `idempotency_key` within a 60-second window returns the cached turn response without executing duplicate LLM calls or duplicate skill assessment increments.
* **AC-012.3 (Rate Limiting):** A client emitting more than 30 turn submissions per minute receives HTTP 429 Too Many Requests.
* **Verification Reference:** `backend/tests/integration/test_session_lifecycle.py`
