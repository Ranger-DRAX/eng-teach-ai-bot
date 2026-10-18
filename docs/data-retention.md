# Child Data Privacy, Inventory & Data Retention Policy

**Document Version:** 1.0.0  
**Status:** Approved for Baseline (Phase 1)  
**Target Group:** Children under 7 years old & Legal Guardians  
**Classification:** Internal Architectural Policy & Privacy Specification

> [!CAUTION]
> **Legal Review Notice:** This document specifies the technical design, data lifecycle, and data minimization mechanisms planned for the English Learning Chatbot platform. **It does not constitute legal advice or formal certification of compliance.** Jurisdiction-specific privacy statutes (including the US Children’s Online Privacy Protection Act [COPPA], EU General Data Protection Regulation Article 8 [GDPR-K], and the UK Age Appropriate Design Code / Children's Code) require formal review by qualified legal counsel prior to any public pilot or production launch.

---

## 1. Principles of Child Data Protection

Because the application serves children under 7 years of age, all architecture and data handling decisions follow four core principles:
1. **Strict Data Minimization:** Collect only the bare minimum technical and educational attributes necessary to deliver progressive English instruction.
2. **Zero Secondary Use:** Child data, interaction history, and tentative emotional cues are never used for targeted advertising, marketing, third-party profiling, or behavioral ranking.
3. **Parental Authority & Transparency:** Authorized parents/guardians retain absolute visibility, control, portability, and deletion authority over their child's profile and learning records.
4. **Non-Diagnostic Sentiment Handling:** Text-based emotional signals (e.g., frustration, excitement) are fleeting conversational cues used solely to adjust immediate response tone. They are never recorded as permanent psychological or behavioral profiles.

---

## 2. Comprehensive Data Inventory

| Data Category | Specific Elements | Business & Educational Purpose | Storage Mechanism | Retention Period | Deletion Trigger / Lifecycle |
|---|---|---|---|---|---|
| **Parent/Guardian Credentials** | Email address, password hash (Argon2id), parent ID, verified consent timestamp & version | Authentication, account management, consent tracking, legal authorization | PostgreSQL (`guardians` table) | Duration of active parent account | Deleted immediately upon guardian account closure |
| **Child Profile Metadata** | Pseudonymous display name (e.g. "Little Panda"), birth month & year (for curriculum age bracket) | Personalizing chat greetings and establishing age-appropriate vocabulary limits | PostgreSQL (`children` table) | Duration of active child profile | Deleted within 72 hours of parent deletion request |
| **Curriculum Progress** | Current level (L1/L2/L3), skill mastery status (`unassessed`, `developing`, `mastered`), cumulative score | Backend-owned progression engine; determining practice exercises across sessions | PostgreSQL (`child_skills`, `learning_progress`) | Duration of active child profile | Deleted within 72 hours of parent profile deletion |
| **Assessment Evidence** | Skill ID, assessment outcome (`pass`/`retry`), timestamp, session ID | Evaluating promotion criteria over time; auditable educational progression | PostgreSQL (`assessment_events`) | Duration of active child profile | Deleted within 72 hours of parent profile deletion |
| **Session Metadata** | Session ID, start time, end time, active mode, turn count | Session lifecycle management, 15-minute inactivity timeout, screen-time monitoring | PostgreSQL (`chat_sessions`) | 30 days | Automated background job purges sessions older than 30 days |
| **Chat Transcripts** | Child input text, validated bot response, turn latency, fallback flag | Context assembly (last 5 turns) and parental review dashboard | PostgreSQL (`chat_turns`) | 30 days | Automated background job purges turns older than 30 days; instant deletion on parent request |
| **Operational & Audit Logs** | Correlation ID, endpoint path, status code, latency (ms), pseudonymous child ID | Reliability monitoring, SLO latency verification, security audit trail | Structured log store / stdout | 14 days | Automated log rotation and purge after 14 days; zero raw child text in logs |

---

## 3. Explicit Prohibited Data (What Will NEVER Be Collected)

The system is architecturally designed to prohibit the collection, ingestion, or storage of:
* **Child Full Legal Name:** Only child-selected pseudonyms or nicknames are permitted.
* **Physical Addresses & Geolocation:** No GPS coordinates, street addresses, postal codes, or IP-derived precise physical locations.
* **Biometric & Audio/Video Data:** The MVP is strictly text-only; no voice recordings, audio streams, camera feeds, facial recognition data, or biometric templates.
* **Contact Information:** No child email addresses, phone numbers, or social media handles.
* **School & Institutional Identifiers:** No school names, classroom IDs, or government student IDs.
* **Health & Psychological Diagnostics:** No medical records, psychological assessments, disability diagnoses, or permanent emotional condition tracking.
* **Financial Data:** Payment details are handled by third-party PCI-DSS compliant gateways; child profiles have zero access to billing instruments.

---

## 4. Deletion Mechanics & Workflows

### 4.1 Parent-Initiated On-Demand Deletion
* **API Route:** `DELETE /api/v1/children/{child_id}`
* **Authorization:** Verified against authenticated parent session cookie or bearer token.
* **Cascading Purge:** The deletion transaction executes a cascade across:
  * `children`
  * `chat_sessions`
  * `chat_turns`
  * `child_skills`
  * `assessment_events`
* **SLA:** Complete removal from primary PostgreSQL tables is immediate (synchronous transaction). Ephemeral caches (if configured) are evicted immediately. Offsite database backup snapshots expire within standard rolling retention (max 14 days).

### 4.2 Automated Age-Off Purge
* A scheduled backend maintenance cron job executes daily:
  * Permanently deletes `chat_turns` and `chat_sessions` older than 30 days.
  * Ensures compliance with data minimization by eliminating long-term conversational archives while retaining high-level aggregate skill mastery for educational continuity.

---

## 5. Parent/Guardian Access & Portability

Under REQ-006 and REQ-011, legal guardians possess direct self-service tools within the Parent Dashboard:
1. **Inspection:** Parents can view the complete active transcript history (up to 30 days) and detailed skill progression for each linked child profile.
2. **Export / Portability:** Parents can trigger a machine-readable JSON/CSV export of their child's learning history and assessment logs via `GET /api/v1/children/{child_id}/export`.
3. **Revocation of Consent:** Parents can revoke consent at any time, which halts all conversational sessions and disables child chat endpoints until consent is renewed.

---

## 6. Technical Safeguards & Isolation

* **Tenant Isolation:** Foreign-key constraints and backend authorization middleware enforce that all queries for child data validate `child.guardian_id == authenticated_guardian.id`.
* **Encryption Standards:**
  * In Transit: TLS 1.3 enforced for all client-to-backend and backend-to-provider communications.
  * At Rest: AES-256 encryption on PostgreSQL storage volumes and backup snapshots.
* **Redaction in CI and Telemetry:**
  * CI test fixtures and seed data use synthetic, mocked child profiles (e.g. `child_test_001`). Real child data is never loaded into development, testing, or staging environments.
  * Subprocess and log redaction filters replace common secret and token patterns with `[REDACTED]`.
