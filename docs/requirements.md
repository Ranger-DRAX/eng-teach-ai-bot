# Functional & Non-Functional Requirements Specification

**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 1)  
**Target Audience:** Children under 7 years old (and authorized parents/guardians)  
**Product Mission:** A text-only, conversational English-learning chatbot providing progressive language acquisition (L1/L2/L3), four interaction modes (Learning, Conversation, Engagement, Support), age-appropriate Social and Emotional Learning (SEL), context-aware personalization, and parent dashboard visibility, operating within an end-to-end P95 latency SLO below 2,000 ms.

---

## 1. System Overview & Core Principles

The English Learning Chatbot is an educational platform designed specifically for young learners acquiring English as a primary or secondary language. The system adheres to strict architectural boundaries:
1. **Deterministic Backend Authority:** The backend application logic—never the LLM—is the sole authority for curriculum progression, skill mastery scoring, level transitions, and interaction mode selection.
2. **Generative Language with Guardrails:** The Large Language Model (LLM) is used strictly as a stateless natural language generator for conversational turns. Outputs are validated deterministically before display.
3. **Data Minimization & Child Protection:** Strict isolation of child records, zero collection of unnecessary personal identifiers, parent-controlled consent and deletion workflows, and non-diagnostic SEL handling.
4. **Latency as an SLO:** End-to-end completion latency must remain under 2,000 ms at P95 under standard operating workloads.

---

## 2. Functional Requirements

### REQ-001: Deterministic Progressive English Learning (L1, L2, L3)
* **Description:** The system must structure English language acquisition across three explicit, progressive proficiency levels:
  * **Level 1 (L1 - Early Beginner):** Focuses on single words, letter-sound phonics, and core vocabulary (colors, animals, family, numbers 1–10). Prompts are short (1–5 words) and responses are capped at 15 words.
  * **Level 2 (L2 - Emerging Beginner):** Focuses on 2–3 word phrases, simple subject-verb-object sentences, common verbs, and familiar daily objects. Prompts average 3–8 words and responses are capped at 30 words.
  * **Level 3 (L3 - Early Communicator):** Focuses on multi-turn dialogue, compound sentences, descriptive adjectives, basic storytelling, and open-ended questions. Responses are capped at 50 words.
* **Mastery & Progression Rules:**
  * Progression between levels is strictly governed by deterministic backend logic based on accumulated skill assessment evidence stored in PostgreSQL.
  * A skill must transition through explicit states: `unassessed` -> `developing` -> `mastered`.
  * Advancing to a higher level requires meeting prerequisite skill thresholds across multiple separate sessions; unassessed skills are never treated as mastered.
  * The LLM must not promote a child, downgrade a child, or declare mastery independently.

### REQ-002: Backend Interaction Mode Management
* **Description:** The backend mode manager must dynamically select one of four interaction modes for each conversational turn:
  1. **`learning`:** Explicit pedagogical practice, vocabulary drills, and guided question-answer interactions.
  2. **`conversation`:** Open conversational English about child-friendly topics (pets, games, favorite foods) without forcing pedagogical exercises into every turn.
  3. **`engagement`:** Interactive games, rhymes, roleplay, word association, and playful curiosity prompts.
  4. **`support`:** Comfort, reassurance, encouragement, and calming responses when the child expresses confusion, frustration, or hesitation.
* **Mode Selection Policy:**
  * Mode selection is computed deterministically by the backend using explicit child intent (e.g., "let's play", "stop", "I need help"), session state, and cautious sentiment cues.
  * Explicit child instructions (e.g., "stop", "I want to talk", "no more quiz") immediately override lesson progression.
  * The LLM does not perform mode routing or self-select modes.

### REQ-003: Social and Emotional Learning (SEL) & Supportive Interaction
* **Description:** The system must integrate age-appropriate SEL principles aligned with early childhood developmental frameworks (self-awareness, self-management, social awareness, and relationship skills).
* **Non-Diagnostic Boundaries:**
  * Emotional cues detected from child input (e.g., "I'm sad", "this is hard", "I can't do it") are treated solely as tentative, transient conversational signals to trigger supportive responses.
  * The system must never assign a diagnostic, psychological, or behavioral label to a child.
  * Emotional signals must never be stored as permanent personality traits or shared for profiling, advertising, or ranking.
  * SEL interactions are supportive and encouraging; the chatbot is an educational companion, not a therapist, medical device, or crisis counselor.

### REQ-004: Context-Aware Personalization & Compact State
* **Description:** Generative prompts must be enriched with compact, child-scoped context without exceeding latency or token budgets.
* **Context Assembly Rules:**
  * Injected context is strictly limited to: active level (L1/L2/L3), current target skill, child display name / chosen topic interest, and the last 3–5 dialogue turns.
  * The child's full historical transcript is never loaded into LLM prompts.
  * Retrieval is isolated to the authenticated child profile; cross-tenant or cross-child context contamination is prohibited.

### REQ-005: Durable Learning Progress in PostgreSQL
* **Description:** PostgreSQL is the single authoritative source of truth for all durable system state.
* **Persistence Requirements:**
  * Learning progress, skill mastery records, assessment events, session state, and parent account bindings must be transactionally persisted.
  * A child returning in a new session must resume seamlessly from their persisted level and skill status.
  * Ephemeral caching layers (e.g., Redis) are optional optimizations and must never hold the sole copy of learning progress.

### REQ-006: Child Privacy, Data Isolation, and Authorization
* **Description:** The architecture must enforce strict multi-tenant authorization, tenant isolation, and data minimization.
* **Privacy Specifications:**
  * Every request accessing child data must be verified against an authenticated parent/guardian account. Direct child-ID spoofing must be blocked (HTTP 403/404).
  * No unnecessary Personally Identifiable Information (PII) is collected: no child real full names, physical addresses, school names, phone numbers, precise geolocation, or audio/video recordings.
  * Parents must have self-service access to view, export, and permanently delete their child's data within 72 hours.
  * System logs and metrics must use pseudonymous IDs and redacted metadata; provider keys, auth tokens, and raw child input must never appear in application logs.

### REQ-007: Complete Response Validation & Deterministic Fallbacks
* **Description:** All LLM candidate responses must undergo deterministic schema validation and safety filtering before being returned to the client.
* **Validation Specifications:**
  * Responses must conform to the strict JSON schema: `{"response_text": "..."}`.
  * Text length must adhere to level limits (L1 <= 15 words, L2 <= 30 words, L3 <= 50 words).
  * Responses must pass content safety filters (banning inappropriate words, adult themes, scary topics, or complex vocabulary exceeding the child's level).
  * If the model output fails schema validation, exceeds length limits, triggers a safety filter, or times out, the backend immediately returns a safe, pre-written deterministic fallback response.
  * Raw, unvalidated model output is never streamed or returned to the child.

### REQ-008: End-to-End Latency Service Level Objective (SLO)
* **Description:** The system must deliver a P95 end-to-end response completion latency of less than 2,000 ms under documented normal workloads.
* **SLO Measurement Criteria:**
  * Latency is measured from complete receipt of the client HTTP turn submission to the final delivery of the complete validated response payload.
  * TTFT (Time to First Token) does not satisfy the completion SLO.
  * Performance reports must separate completion latency, model provider latency, fallback rate, and error rate to prevent fast fallbacks from masking slow LLM responses.

### REQ-009: Child Learning Journey & Parent Dashboard
* **Description:** The client interface must support an accessible child chat experience and a comprehensive parent/guardian dashboard.
* **Dashboard Specifications:**
  * Child interface: High-contrast, early-reader friendly text layout with clear visual turn indicators and engaging feedback.
  * Dashboard interface: Displays verified backend metrics—active level, mastered skills, skills in progress, total practice sessions, and recent session summaries.
  * The dashboard reads only committed PostgreSQL progress; unverified or optimistic client states are prohibited.

### REQ-010: Operational Recovery, Backup, and Migration Integrity
* **Description:** The backend data store and application deployment must support automated recovery and schema evolution.
* **Operational Specifications:**
  * Relational migrations (via Alembic) must be deterministic, reversible, and tested against disposable test databases.
  * The database must support automated point-in-time recovery with verified restore drill runbooks.
  * Database or external provider outages must fail safely without corrupting stored child mastery records.

### REQ-011: Parent/Guardian Account & Verified Consent Workflow
* **Description:** All child profiles must be provisioned and managed under an adult guardian account.
* **Consent Management:**
  * An adult must complete account creation and provide explicit consent prior to initiating child chat sessions.
  * The consent model must support regulatory privacy standards (e.g., COPPA, GDPR-K), flagged for jurisdictional legal review prior to production launch.

### REQ-012: Safe Session Lifecycle & Abuse Prevention
* **Description:** The chat interaction lifecycle must implement safeguards against session fatigue, replay attacks, and endpoint abuse.
* **Lifecycle Rules:**
  * Sessions automatically expire after 15 minutes of inactivity; maximum cumulative daily session duration recommendations are surfaced to parents.
  * Turn submissions must support client-provided idempotency keys to prevent duplicate scoring or duplicate turn processing from network retransmissions.
  * Ingress endpoints must enforce IP and session-level rate limiting.

---

## 3. Non-Functional Requirements Summary

| Category | Requirement ID | Target Metric / Standard |
|---|---|---|
| **Latency** | REQ-008 | P95 < 2,000 ms end-to-end completion under normal workload |
| **Availability** | REQ-010 | 99.9% uptime for core API; graceful degradation on provider outage |
| **Data Isolation** | REQ-006 | Zero cross-tenant data leakage; 100% authorization check coverage |
| **Security** | REQ-006, REQ-012 | Zero plaintext secrets; rate limiting on all public routes |
| **Output Integrity** | REQ-007 | 100% validation check pass rate on delivered responses |
| **Data Retention** | REQ-006 | Hard deletion within 72 hours of parent request |
