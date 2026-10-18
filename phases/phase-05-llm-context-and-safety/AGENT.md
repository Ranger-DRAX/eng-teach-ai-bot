# Phase 05 Agent Instructions — LLM integration, compact context, and response validation

## Goal

Generate natural personalized text while keeping the backend in control and the output validated.

## Required behavior

Read the root `AGENTS.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/DEFINITION_OF_DONE.md`, and any documents referenced below. Inspect the repository before editing. Implement **only Phase 05**. If prior-phase files are absent, report the missing prerequisite and create only the minimum current-phase deliverable that is safe; do not fake the gate result. Make changes in small increments and document assumptions.

## Implementation tasks

- Implement a provider interface and a Google GenAI adapter (or a provider adapter approved in Phase 1). Read the model ID and API key from environment configuration. Never hard-code secrets or provider-specific model names in business logic.
- Build a context assembler that retrieves current level, target skill, selected mode, relevant mastered/needs-practice skills, recent conversation turns, and required lesson state. Minimize and redact context; do not send all historical turns by default.
- Use one LLM call for each generative response. The model receives mode-specific instructions, SEL guidance, age band, output length, and a constrained response schema. The model may return `response_text` only; mode/progression are backend-owned.
- Implement network timeouts, bounded length, schema validation, content/safety validation, and deterministic fallbacks for timeout, provider errors, malformed output, and rejected output.
- Keep system instructions as versioned files/constants and log prompt/model revision identifiers without logging secrets or unnecessary child message bodies.
- Use mocked LLM providers in all regular unit and CI tests. Add an explicitly gated live smoke/evaluation command for staging only.

## Required tests and verification

- Test context relevance and child isolation with two profiles; prove no context crosses accounts.
- Test valid schema, malformed JSON, empty output, output too long, unsafe sample output, provider timeout, rate limit, and provider outage.
- Test all modes and L1/L2/L3 prompt contexts with representative synthetic scenarios.
- Test that a provider failure creates a safe fallback quickly and does not create false assessment evidence.
- Confirm unit tests pass without an API key and do not incur provider charges.

## Acceptance criteria

- [ ] One generative model call is made per generative turn; deterministic paths make zero provider calls.
- [ ] Only validated response text is returned to the child.
- [ ] The backend, not the LLM, sets mode, level, progress, and fallback metadata.
- [ ] Mocked provider tests pass and live tests are separate opt-in staging checks.

## Phase gate

Run from repository root:

```bash
python scripts/phase_gate.py --phase 5
```

The command must exit `0`; inspect the generated `artifacts/phase-gates/phase-05.json` report. If a check fails, fix the underlying issue and rerun it. Do not alter acceptance thresholds only to make the gate pass.

## Do not do

Do not stream raw unvalidated tokens, put a permanent key in the frontend, treat safety prompts as a guarantee, or automatically make a second LLM call on timeout.

## Final report required from the coding agent

Return a concise report with: (1) files created/changed, (2) implementation summary, (3) exact test/gate commands and outcomes, (4) phase report path, (5) manual review still needed, and (6) known limitations. Never state that an unrun check passed.
