# Testing Strategy

## Test layers

1. **Unit:** progression decisions, skill mastery, mode transitions, context selection, schema validation, safety fallbacks, authorization helpers.
2. **Integration:** FastAPI routes, PostgreSQL repositories, transaction boundaries, idempotent turn submission, mocked LLM adapter, persistence across sessions.
3. **Frontend component:** chat submission, disabled/loading states, progress display, error/fallback rendering, accessibility basics.
4. **End-to-end:** start/resume session, converse, switch modes, perform an exercise, save progress, return in a new session, confirm the dashboard uses persisted data.
5. **Model evaluation:** a versioned synthetic scenario set measuring instruction adherence, educational correctness, mode adherence, age-appropriateness, SEL quality, and invalid/unsafe output rejection. Use a human review sample; automated judges are not ground truth.
6. **Performance:** load test in staging; report p50/p95/p99, throughput, error rate, fallback rate, and the defined workload.
7. **Operations:** backup restore, migration rollback/forward strategy, secret rotation, alert checks, and controlled provider/database outage drills.

## Required scenario categories

- New child with no learning history starts at L1.
- Returning child resumes from persisted level and mastery.
- Child cannot advance when prerequisites or assessment evidence are missing.
- Child never skips a level solely because the LLM suggests it.
- Conversation mode does not force a lesson into every turn.
- Clear request to play or stop changes mode deterministically.
- Text that suggests frustration receives supportive, non-diagnostic handling.
- Ambiguous emotional signal is not stored as a permanent fact.
- Context remains child-scoped and session-safe.
- Prompt injection or a request for personal information does not bypass policy.
- Provider timeout/invalid JSON/safety rejection produces a safe fallback.
- Duplicate request does not double-score an assessment or create duplicate turns.
- Database/provider outage does not corrupt learning progress.
- Dashboard reflects committed backend progress, not optimistic unverified mastery.
- Latency benchmark meets the agreed P95 target without hiding fallback/error volume.

## LLM test rules

- Unit and ordinary CI tests mock the model provider.
- Keep synthetic prompt/response fixtures; do not use real child transcripts.
- Any live evaluation uses a restricted staging project, environment-managed secrets, rate limits, and a recorded model/version/prompt revision.
- Review prompt changes as code. Run the regression evaluation suite when model, prompt, safety policy, or context assembly changes.

## Data and reliability

- Test access isolation using at least two synthetic child profiles.
- Test deletion and retention logic against all relevant stored records and caches.
- Test migrations from an empty database and from the previous supported schema.
- Ensure logs contain correlation IDs and timings but do not contain API keys, bearer tokens, or unnecessary raw messages.
