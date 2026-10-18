# Phase 08 Agent Instructions — End-to-end latency, load, and cost optimization

## Goal

Measure and validate P95 end-to-end completion latency below two seconds under the agreed normal workload.

## Required behavior

Read the root `AGENTS.md`, `docs/ARCHITECTURE_DECISIONS.md`, `docs/DEFINITION_OF_DONE.md`, and any documents referenced below. Inspect the repository before editing. Implement **only Phase 08**. If prior-phase files are absent, report the missing prerequisite and create only the minimum current-phase deliverable that is safe; do not fake the gate result. Make changes in small increments and document assumptions.

## Implementation tasks

- Implement `scripts/measure_latency.py` against the real staging chat endpoint. Require explicit environment variables for base URL, protected test token, and synthetic session IDs; never accept production child IDs in the test script.
- Use the workload definition approved in Phase 1. If no exact workload was approved, mark the gate blocked and ask for the test profile to be finalized in documentation; do not silently choose a load profile and claim production readiness.
- Measure client-visible complete-response latency as well as server-side stages; include non-LLM and LLM turns. Capture p50/p95/p99, throughput, error rate, timeout rate, fallback rate, and model latency.
- Profile database query count/duration, context size, provider latency, output validation, and frontend/API round trips. Optimize only bottlenecks supported by measurements.
- Add regression/performance tests for slow provider, timeout, overloaded service, database delay, repeated request, and fallback behavior. Keep automatic retries bounded and avoid retry storms.
- Keep result artifacts free of raw child messages, keys, or session tokens. Record model version, prompt version, commit SHA, region, and test date.

## Required tests and verification

- Run the benchmark against the staging deployment with synthetic accounts and the configured normal workload.
- Fail the phase gate if P95 is >= 2000 ms, required metrics are missing, the successful-response rate is below the configured threshold, or fallback/error volume is hidden.
- Repeat runs enough to reduce noise and record both warm operation and cold-start behavior separately.
- Check that deterministic handlers are actually avoiding LLM calls and that the fallback path does not conceal model slowness.

## Acceptance criteria

- [ ] P95 complete-response latency is < 2000 ms under the Phase 1 normal workload.
- [ ] All required metrics, test parameters, model/prompt versions, and limitations are recorded.
- [ ] Fallback, error, and success rates meet agreed thresholds and are disclosed next to latency.
- [ ] The phase gate passes against staging; local mocks alone do not satisfy this phase.

## Phase gate

Run from repository root:

```bash
python scripts/phase_gate.py --phase 8
```

The command must exit `0`; inspect the generated `artifacts/phase-gates/phase-08.json` report. If a check fails, fix the underlying issue and rerun it. Do not alter acceptance thresholds only to make the gate pass.

## Do not do

Do not use only time-to-first-token, omit timeouts/errors, test only a warm single-user path, or claim a universal guarantee from one run.

## Final report required from the coding agent

Return a concise report with: (1) files created/changed, (2) implementation summary, (3) exact test/gate commands and outcomes, (4) phase report path, (5) manual review still needed, and (6) known limitations. Never state that an unrun check passed.
