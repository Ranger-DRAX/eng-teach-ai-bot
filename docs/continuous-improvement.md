# Continuous Improvement & Ongoing Evaluation Policy

**Document Version:** 1.0.0  
**Phase:** 10 (Pilot and Continuous Improvement)  
**Governance Standard:** ISO 25010 / Safe Educational Software Lifecycle  

---

## 1. Release & Evaluation Lifecycle

Every code, model, prompt, or curriculum modification follows a reproducible verification cycle before production release:

```
┌─────────────────────────────────┐
│ Curriculum / Code / Prompt Edit │
└─────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Automated Unit & Phase Gates    │ ───> If fail: Reject release
└─────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Offline Safety Benchmark        │ ───> 12 adversarial scenarios (100% required)
└─────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Latency & Load SLO Verification │ ───> P95 < 2,000 ms check
└─────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Staging Canaries & Educator Sign│ ───> Human qualitative verification
└─────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Gradual Production Rollout      │
└─────────────────────────────────┘
```

---

## 2. Model & Prompt Version Management

- **Model ID as Configuration:** Model identifier (e.g. `gemini-2.0-flash`) is managed via environment variable `LLM_MODEL`. No model IDs are hard-coded in business logic.
- **Prompt Versioning:** The system prompt template in `ContextBuilder` carries an immutable `PROMPT_VERSION` constant.
- **Mandatory Regression Gates:** Changing the model version or prompt template mandates running:
  1. `python scripts/run_safety_eval.py --mode offline --check-thresholds`
  2. `python scripts/measure_latency.py --check-slo`
  3. Backend test suite: `pytest backend/tests`

---

## 3. Curriculum Evolution & Pedagogical Review

- Any addition to `L1_SKILLS`, `L2_SKILLS`, or `L3_SKILLS` requires formal sign-off by an accredited early-childhood educator.
- New vocabulary items must adhere to phonetic simplicity, cultural neutrality, and positive valence rules.
- Mastery thresholds (≥ 3 successful events across ≥ 2 distinct sessions) cannot be lowered to mask poor comprehension.

---

## 4. Privacy & Data Governance Audits

- **Quarterly Retention Audits:** Automated cron job identifies and purges inactive guest or abandoned demo sessions older than 30 days.
- **Immediate Data Deletion:** Guardian account deletion requests execute cascading deletions across all 6 database tables within 48 hours.
- **Privacy Review:** Log files are inspected monthly to ensure zero provider keys, auth tokens, or unnecessary full child conversation text are captured in standard telemetry.

---

## 5. Feedback Loop for Guardians and Educators

- **In-App Issue Flagging:** Guardians can flag a turn with a single click in the dashboard.
- **Privacy-Preserving Telemetry:** The feedback submission transmits only the `turn_id`, `mode`, `level`, and guardian feedback category, redacting any free-text child inputs.
- **Triage Cadence:** Weekly review of flagged turns by the Safeguarding Lead and Pedagogical Advisor.
