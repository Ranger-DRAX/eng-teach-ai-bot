# Open Questions / Decisions to Confirm

Use this file to track decisions, owner, due date, and status. Do not block implementation on questions that are not needed for the current phase; document a safe provisional assumption.

| ID | Decision | Default / Provisional Assumption | Owner | Status | Evidence / Due Date |
|---|---|---|---|---|---|
| **OQ-01** | Target deployment region and normal-load profile | Defined in `docs/latency-budget.md`: 10 concurrent VUs, message mix (60% learn, 25% conv, 10% engage, 5% support), cloud co-location in `us-east-1` / `us-central1`. Pending formal stakeholder sign-off prior to Phase 8 load testing. | Project Owner | Provisional baseline set | `docs/latency-budget.md` (Sign-off by Phase 8) |
| **OQ-02** | Applicable privacy jurisdictions and consent requirements | Architecture follows COPPA and GDPR-K minimum principles (parental consent gate, no PII, 72h deletion). Formal legal/privacy counsel review required before public pilot. | Legal & Privacy Owner | Blocked for pilot; provisional architecture approved | Formal review required before Phase 10 |
| **OQ-03** | Parent/guardian account and child profile workflow | Child profiles are strictly subordinate to authenticated guardian accounts (`child.guardian_id == guardian.id`). Specified in `docs/threat-model.md` and `docs/acceptance-criteria.md`. | Product Owner | Provisional baseline set | `backend/tests/security/test_child_isolation.py` (Phase 3/6) |
| **OQ-04** | Curriculum validation reviewer | Educational objectives for L1/L2/L3 specified in Phase 2 must undergo accredited early-childhood educator review before deployment. | Education Lead | Pending Phase 2 specification | Sign-off required prior to Phase 10 |
| **OQ-05** | Exact hosted model and fallback response policy | Model ID is decoupled as an environment configuration (`LLM_MODEL`). Staging uses cloud provider with 1,500 ms timeout and deterministic local fallback strings. | Technical Owner | Provisional baseline set | `docs/ARCHITECTURE_DECISIONS.md#AD-009` |
| **OQ-06** | Data retention duration for message history | Set to 30 days maximum for active chat turns and sessions, with automated age-off purge and immediate deletion on parent request, documented in `docs/data-retention.md`. | Privacy Owner | Baseline specified | `docs/data-retention.md` (Sign-off by Phase 7) |
