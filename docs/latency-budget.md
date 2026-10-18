# Latency Budget & Performance Service Level Objective (SLO)

**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 1)  
**Target SLO:** P95 End-to-End Completion Latency < 2,000 ms  
**Scope:** Interactive Chat Turn Path  

> [!IMPORTANT]
> **Workload Assumptions Status:** The workload parameters and infrastructure topology defined in this document represent the engineering baseline for Phase 1. They are marked as **provisional assumptions pending formal stakeholder sign-off** prior to Phase 8 staging load execution (tracked under [OQ-01](file:///k:/Job_Prep/Company%20test/Brim/proj-2/english_learning_chatbot_agent_pack/docs/open-questions.md)).

---

## 1. Latency SLO Definition & Measurement Boundaries

* **Target Objective:** Under the documented normal workload profile, the 95th percentile (P95) end-to-end response completion latency must remain strictly below **2,000 ms**.
* **Measurement Start:** The exact timestamp when the backend gateway completes receipt of the final byte of the client HTTP request (`POST /api/v1/chat/turn`).
* **Measurement End:** The exact timestamp when the backend completes transmitting the final byte of the complete, validated response payload (`{"turn_id": "...", "response_text": "...", "mode": "...", "level": "...", ...}`) to the client network connection.
* **Why TTFT Is Insufficient:** In an educational application for children under 7, unvalidated tokens must never be streamed directly to the child. The child interface renders the complete validated sentence or phrase once safety and length rules pass. Therefore, Time-to-First-Token (TTFT) does not reflect actual user experience; **complete validated response availability** is the sole determinant of SLO compliance.

---

## 2. End-to-End Latency Budget Allocation

The 2,000 ms ceiling is allocated across the sequential stages of a single conversational turn:

| Stage | Operation Description | Target Allocation (ms) | Hard Limit / Timeout (ms) | Failure Strategy |
|---|---|---|---|---|
| **1. Ingress & Security** | Ingress routing, TLS handshake termination, token-bucket rate limiting | 40 ms | 100 ms | HTTP 429 if rate exceeded |
| **2. Auth & Tenant Check** | Guardian session verification, child-ownership lookup | 40 ms | 80 ms | HTTP 401 / 403 on authorization failure |
| **3. Context Retrieval** | PostgreSQL query: child active level, target skill, last 5 chat turns | 50 ms | 120 ms | Local default context if query times out |
| **4. Prompt Assembly** | Formulate system prompt, insert compact context, validate token budget (< 800 tokens) | 20 ms | 40 ms | Fail turn / fallback |
| **5. LLM Inference & Transit** | Secure HTTPS POST to hosted LLM provider; generation of candidate response JSON | 1,450 ms | **1,500 ms** (Client Timeout) | Abort request; activate deterministic fallback |
| **6. Output Validation** | JSON parsing, Pydantic schema validation, banned phrase check, word count ceiling | 40 ms | 80 ms | Discard candidate; activate deterministic fallback |
| **7. Durable Persistence** | PostgreSQL transactional write: append chat turn, update assessment events, commit progress | 60 ms | 150 ms | Asynchronous queue or retry buffer |
| **8. Egress & Serialization** | JSON payload formatting, HTTP header construction, transmission to socket | 30 ms | 60 ms | Network socket error log |
| **9. Safety Buffer** | Unallocated contingency for network jitter and process scheduling | 270 ms | N/A | Absorbs transient spikes |
| **Total End-to-End Budget** | **Complete request receipt to complete response dispatch** | **2,000 ms** | **2,000 ms (P95 Ceiling)** | **SLO Breach if P95 >= 2,000 ms** |

---

## 3. Documented Normal Workload Profile

The latency SLO must be validated against a formal, reproducible load profile executed by `scripts/measure_latency.py`:

* **Concurrent Virtual Users (VU):** 10 concurrent active child sessions issuing requests continuously.
* **Pacing / Think Time:** Simulated pause of 8 to 12 seconds between child turn submissions (reflecting young child reading and response time).
* **Aggregate Throughput:** Approximately 0.8 to 1.2 completed turns per second across the cluster.
* **Test Duration:** 10 continuous minutes of steady-state execution.
* **Message Mix Distribution:**
  * **60% Learning Mode:** Single-word answers or short vocabulary selections (e.g., "apple", "the dog", "blue", 1–4 words).
  * **25% Conversation Mode:** Short conversational statements (e.g., "I like playing with my cat", 3–8 words).
  * **10% Engagement Mode:** Simple game/play inputs (e.g., "let's play a game", "rhyme with ball", 2–6 words).
  * **5% Support Mode:** Expressions of confusion or fatigue (e.g., "I don't know", "too hard", "stop", 1–4 words).
* **Payload Size:** Request payloads average 150–300 bytes (child text < 50 characters).

---

## 4. Warm vs. Cold Start Treatment

* **Steady-State (Warm) Execution:**
  * The SLO strictly applies to steady-state operations where backend containers are initialized, SQLAlchemy database connection pools are warmed, and provider HTTPS connection keep-alives are established.
  * Benchmark measurements begin after a 60-second warm-up ramp.
* **Cold Starts:**
  * Container cold starts (e.g., during auto-scaling or instance replacement) and initial database pool creations are monitored separately as operational health indicators.
  * Cold start events are disaggregated in reporting and do not skew steady-state user experience evaluation.

---

## 5. Deployment Environment & Regional Topology

To meet the 1,500 ms provider round-trip limit:
* **Cloud Region Co-Location:** The backend application servers and managed PostgreSQL database must be deployed in the same cloud region (or direct low-latency peering zone) as the hosted LLM provider API endpoint (e.g., AWS `us-east-1` or GCP `us-central1`).
* **Intra-VPC Latency:** Database ping times between backend compute instances and PostgreSQL must not exceed 2.0 ms.
* **Public WAN Latency:** Testing harnesses in CI/staging must measure network transit from realistic client edge locations or account for public internet RTT.

---

## 6. Disaggregated Reporting & Anti-Masking Policy

> [!WARNING]
> **Anti-Masking Rule:** Deterministic fallbacks execute locally in ~150 ms. Under no circumstances may high fallback rates be used to artificially satisfy the P95 latency threshold when the underlying LLM provider is lagging or timing out.

All automated performance reports (`artifacts/phase-gates/phase-08.json` and `docs/performance/latency-report.md`) must output independent measurements for:
1. **Total Completion Latency:** p50, p90, p95, and p99 percentiles.
2. **LLM Provider Round-Trip Latency:** p50, p90, p95, and p99 percentiles for non-fallback turns.
3. **Fallback Rate:** Percentage of total requests resolved via fallback (Gate threshold: must be **< 5.0%**).
4. **Provider Timeout Rate:** Percentage of provider calls aborted by the 1,500 ms ceiling (Gate threshold: must be **< 1.0%**).
5. **System Error Rate:** Percentage of turns resulting in HTTP 5xx responses (Gate threshold: must be **0.0%**).
6. **Time to First Token (TTFT):** Recorded for informational purposes if experimental streaming handlers are tested in future phases.
