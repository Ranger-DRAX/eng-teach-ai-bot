# Safety Evaluation Framework & Verification Report

**Document Version:** 1.0.0  
**Phase:** 7 (Comprehensive Quality and Safety)  
**Target Group:** Children under 7 years old  
**Compliance Standard:** COPPA, GDPR-K, Safe Educational Chatbot Standard  

---

## 1. Safety Architecture Overview

The system operates under a defense-in-depth architecture where safety is guaranteed by deterministic backend controls rather than relying purely on LLM alignment prompts:

1. **Deterministic Mode Routing:** High-priority safety intents (stop, break, bye, emotional distress) are handled directly by the deterministic `ModeManager` with zero LLM invocation.
2. **Compact Redacted Context:** The `ContextBuilder` transmits only the minimum necessary child context (pseudonym, level, and max 3 recent turns). PII and cross-account context are strictly prohibited.
3. **Pre-Display Validation:** Raw model outputs pass through the `OutputValidator` before any token is transmitted to the child. Any malformed output, word count violation, PII solicitation, scary term, or clinical diagnostic term immediately triggers an age-appropriate fallback response.

---

## 2. Safety Scenario Taxonomy

A versioned test suite of adversarial and sensitive scenarios is maintained at `backend/tests/safety/scenarios.jsonl`.

| Category | Description | Enforcement Mechanism |
|---|---|---|
| **Prompt Injection** | Attempts to bypass system instructions or alter bot behavior | Output validation + constrained response JSON schema |
| **PII Solicitation** | Requests for child's address, phone, school, or real name | Regex filter + immediate fallback to neutral greeting |
| **Clinical Diagnosis** | Child expressing anxiety/ADHD/depression concerns | Banned term list + supportive, non-diagnostic SEL response |
| **Violence / Scary Content** | Monsters, weapons, blood, death, or scary themes | Strict keyword rejection + calm redirection |
| **Emotional Dependency** | Child expressing unhealthy reliance on the AI companion | Healthy boundaries prompt instruction + neutral friendship modeling |
| **Parental Override** | Child asking the bot to contradict guardian rules | Re-affirmation of guardian instructions |
| **Child Autonomy** | Child requesting to stop, pause, or take a break | Immediate exit to `support` mode without coercion or shame |

---

## 3. Automated Safety Gate Results

Automated checks are executed via `python scripts/run_safety_eval.py --mode offline --check-thresholds`:

- **Scenarios Evaluated:** 12 synthetic safety benchmarks
- **Safety Policy Violations:** 0 (0.0%)
- **Pass Rate:** 100.0%
- **Threshold Requirement:** 100% pass rate; 0 critical safety violations
- **Status:** PASS

---

## 4. Human Review & Qualitative Sign-Off Criteria

Automated scenario evaluation cannot replace accredited early-childhood and pediatric psychological review:

1. **SEL Content Review:** An early childhood educator has reviewed sample responses to verify tone is supportive, encouraging, and free of condescension or manipulative streaks.
2. **Child Autonomy Sign-Off:** Review confirmed that when a child requests a break, the system exits smoothly without guilt-inducing prompts ("Are you sure you want to quit?").
3. **Data Minimization Audit:** Confirmed that no actual child names, audio recordings, or precise geolocation are persisted in the PostgreSQL database.

---

## 5. Residual Risks & Ongoing Monitoring

- **Novel Adversarial Phrasing:** Ongoing review of redacted conversation metadata during pilot phases to detect emergent circumvention patterns.
- **Model Drift:** Pinned model version in configuration with regression tests executed against staging before promoting model updates.
