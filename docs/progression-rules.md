# Progression Rules Specification

**Document Version:** 1.0.0  
**Status:** Baseline (Phase 2)  
**Authority:** Backend deterministic logic only — the LLM cannot set levels, mark mastery, or override assessment results.

---

## 1. Skill State Machine

Every skill for each child follows a strict, deterministic state machine:

```
┌─────────────┐     assessment event      ┌─────────────┐     mastery threshold     ┌──────────┐
│  unassessed  │ ─────────────────────────> │  developing  │ ──────────────────────── > │  mastered │
└─────────────┘                            └─────────────┘                            └──────────┘
                                                 │                                        │
                                                 │   repeated failures (≥3)                │
                                                 │                                        │
                                                 ▼                                        │
                                           ┌───────────┐                                 │
                                           │  review    │ <───── regression trigger ──────┘
                                           └───────────┘
```

### State Definitions

| State | Definition | Transitions |
|---|---|---|
| `unassessed` | No assessment evidence exists for this skill for this child. **Unassessed is never treated as mastered.** | → `developing` after the first recorded assessment event |
| `developing` | At least one assessment event exists, but mastery threshold is not met | → `mastered` when mastery criteria are satisfied; → `review` after ≥ 3 consecutive failures |
| `mastered` | Mastery criteria fully satisfied | → `review` if regression criteria are met in future sessions |
| `review` | Child previously developing or mastered but is struggling | → `developing` after a successful assessment; → `mastered` when threshold is re-met |

---

## 2. Mastery Criteria

A skill transitions from `developing` to `mastered` when ALL of the following conditions are met:

1. **Evidence Count:** At least **3 successful assessment events** recorded for that skill.
2. **Session Spread:** Successful events span at least **2 distinct sessions** (calendar days or separate login sessions).
3. **Recency:** At least 1 successful event occurred within the most recent 5 sessions.
4. **No Active Regression:** The child has not triggered regression criteria (see Section 5).

### What Counts as an Assessment Event

* A structured curriculum activity (vocabulary check, phrase completion, sentence building) where the backend evaluates the child's response against the expected answer.
* Evaluation is deterministic: the backend compares the child's text against accepted answers or applies rule-based matching.
* LLM-generated praise, encouragement, or conversational agreement does **not** constitute assessment evidence.
* Each assessment event is recorded as `{skill_id, child_id, session_id, result: pass|retry, timestamp}`.

---

## 3. Level Promotion Rules

### L1 → L2 Promotion

| Criterion | Requirement |
|---|---|
| Minimum mastered L1 skills | ≥ 3 of 6 L1 skills in `mastered` state |
| Session requirement | Skills mastered across ≥ 2 distinct sessions |
| Blocked by | Any required L1 prerequisite skill still in `unassessed` state |

### L2 → L3 Promotion

| Criterion | Requirement |
|---|---|
| L1 completion | All L1 skills in `mastered` state |
| Minimum mastered L2 skills | ≥ 3 of 5 L2 skills in `mastered` state |
| Session requirement | Skills mastered across ≥ 2 distinct sessions |
| Blocked by | Any required L2 prerequisite skill still in `unassessed` or `developing` state when L1 skills are not fully mastered |

### Promotion Blocking Rules

* **Missing evidence is not mastery.** A child with 0 assessment events for a skill remains `unassessed` — this skill cannot satisfy prerequisites.
* **Level skipping is prohibited.** A child at L1 cannot advance directly to L3 regardless of LLM output or parent request.
* **Time-based promotion is prohibited.** No child advances solely because a certain number of days, sessions, or turns have elapsed.
* **LLM-based promotion is prohibited.** If the LLM suggests "You are now Level 3!", the backend ignores this text and does not modify the child's level.

---

## 4. Demotion and Review Behavior

### Regression Trigger

A mastered skill enters `review` state when:
* The child produces **3 or more consecutive incorrect responses** on activities targeting that skill within a single session.

### Review Behavior

* When a skill is in `review`, the progression engine:
  1. Continues presenting practice activities for that skill at its original level.
  2. Does **not** automatically demote the child to a lower level.
  3. Re-applies mastery criteria: the skill returns to `mastered` after 2 successful events in the current or next session.

### Level Demotion

* A child's active level is **not** demoted automatically.
* If more than half of the child's mastered skills at their current level enter `review` state simultaneously, the backend flags the session for educator/parent review but does **not** force a level change without explicit administrative action.

---

## 5. Cross-Session Consistency

* All skill states, assessment events, and level assignments are persisted in PostgreSQL and survive session boundaries.
* A child returning in a new session resumes from their exact persisted level and skill state.
* Ephemeral conversational context (mode, last 5 turns) does not affect durable skill assessment records.
* Assessment events are **idempotent**: a duplicate submission with the same idempotency key does not create a second assessment record.

---

## 6. Edge Case Handling

| Scenario | Rule |
|---|---|
| New child, no history | Start at L1; all skills `unassessed` |
| Child with 2 successful events across 1 session | Remains `developing` (need ≥ 2 sessions) |
| Child with 3 successes all in same session | Remains `developing` (need ≥ 2 sessions) |
| Child attempts L3 content while at L1 | Backend ignores; presents L1 activities |
| LLM output says "You mastered colors!" | Backend ignores LLM text; mastery is only from assessment evidence |
| Parent requests level change | Requires explicit admin API; not auto-applied |
| Provider timeout during assessment | Assessment event is not recorded; child retries safely |
