# Phase 02 Agent Instructions — Curriculum, mastery rules, mode taxonomy, and test fixtures

## Goal

Specify the education and interaction policy in deterministic, reviewable artifacts before implementing the engine.

## Required behavior

Read the root `AGENTS.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/DEFINITION_OF_DONE.md`, and any documents referenced below. Inspect the repository before editing. Implement **only Phase 02**. If prior-phase files are absent, report the missing prerequisite and create only the minimum current-phase deliverable that is safe; do not fake the gate result. Make changes in small increments and document assumptions.

## Implementation tasks

- Create `docs/curriculum.md` defining measurable L1, L2, and L3 objectives, age-appropriate examples, prerequisite skills, activity types, and content boundaries.
- Create `docs/progression-rules.md` defining skill states (for example unassessed/developing/mastered), assessment evidence, promotion/demotion or review behavior, prerequisites, consistency across sessions, and how missing evidence is handled. Do not treat unassessed as mastered.
- Create `docs/mode-policy.md` defining Learning, Conversation, Engagement, and Support, mode-selection priorities, explicit requests to stop/change activity, ambiguous signals, and safe fallback behavior.
- Define a versioned synthetic scenario fixture at `backend/tests/fixtures/progression_cases.json` with cases for no history, insufficient evidence, each valid transition, missing prerequisite, level skipping, unassessed skills, and repeated mistakes.
- Define `backend/tests/fixtures/mode_cases.json` with clear/ambiguous intents, topic change, explicit stop/break, playful engagement, and possible frustration. Do not label a child with a durable personality or medical/emotional diagnosis.
- Document SEL principles, sample responses, boundaries, and human-review criteria. SEL is supportive education, not therapy.

## Required tests and verification

- Run `python scripts/check_curriculum_spec.py` to validate fixture schema, unique case IDs, required scenario coverage, and valid level/mode names.
- Have an educator or suitable reviewer check that the curriculum is age-appropriate and that mastery decisions are explainable.
- For the fixture checker, do not weaken required scenarios to resolve failures; fix the specification.

## Acceptance criteria

- [ ] Curriculum objectives are observable and differ meaningfully across L1/L2/L3.
- [ ] Progression rules are deterministic and independent of LLM self-assessment.
- [ ] Mode rules make explicit child requests and safety/support priorities clear.
- [ ] All required synthetic fixture cases exist and the phase gate passes.

## Phase gate

Run from repository root:

```bash
python scripts/phase_gate.py --phase 2
```

The command must exit `0`; inspect the generated `artifacts/phase-gates/phase-02.json` report. If a check fails, fix the underlying issue and rerun it. Do not alter acceptance thresholds only to make the gate pass.

## Do not do

Do not infer a child’s actual mood as fact, advance levels by time alone, or use model-generated praise as evidence of mastery.

## Final report required from the coding agent

Return a concise report with: (1) files created/changed, (2) implementation summary, (3) exact test/gate commands and outcomes, (4) phase report path, (5) manual review still needed, and (6) known limitations. Never state that an unrun check passed.
