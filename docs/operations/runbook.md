# Production Operations & Incident Response Runbook

**Document Version:** 1.0.0  
**Phase:** 9 (Deployment and Operations)  
**Classification:** Internal Operational Guide  

---

## 1. System Architecture & Components

The English Learning Chatbot production environment consists of:
- **Frontend App:** Next.js App Router deployed behind a CDN/Reverse Proxy.
- **Backend API:** FastAPI running under Uvicorn in containerized replicas.
- **Durable Store:** Managed PostgreSQL with automated daily snapshots and point-in-time recovery (PITR).
- **External LLM Provider:** Google Gemini API (`gemini-2.0-flash`) accessed via outbound HTTPS with strict timeouts (1,500 ms).

---

## 2. Deployment Procedures

### 2.1 Standard Deployment (Zero-Downtime Rolling Update)
1. CI automatically runs all quality checks (lint, typecheck, migrations, unit tests, safety eval, E2E tests).
2. Docker images built and tagged with commit SHA (`release-<git-sha>`).
3. Database migrations applied in forward-compatible mode:
   ```bash
   python -m alembic upgrade head
   ```
4. Rolling restart of backend replicas (health checks via `/health` and `/ready`).
5. Frontend static assets deployed to CDN with cache invalidation.

### 2.2 Rollback Procedure
If errors spike post-deploy:
1. Revert container image to previous known stable tag:
   ```bash
   kubectl rollout undo deployment/chatbot-backend
   ```
2. Verify traffic drains to previous version without dropping active sessions.
3. If database migration needs rollback (only if backward-incompatible):
   ```bash
   python -m alembic downgrade -1
   ```

---

## 3. Monitoring, Metrics, and Alerting Thresholds

The application exposes structured metrics and request correlation IDs (`X-Correlation-ID`):

| Alert Name | Metric Trigger | Severity | Action |
|---|---|---|---|
| **HighLatencyP95** | P95 latency > 1,500 ms over 5 min | P2 | Inspect provider latency & DB connection pool |
| **SLO_Breach_P95** | P95 latency > 2,000 ms over 3 min | P1 | Check LLM provider degradation; force fallback if needed |
| **HighErrorRate** | 5xx error rate > 0.5% over 5 min | P1 | Page on-call engineer; inspect error logs |
| **ProviderOutage** | Provider failure / timeout rate > 5% | P2 | Verify Google Gemini status; fallback activates automatically |
| **ElevatedFallbackRate** | Fallback responses > 10% over 10 min | P2 | Investigate output validator rejections or LLM drift |
| **HighProviderSpend** | Hourly token spend exceeds budget by 50% | P3 | Review traffic volume and prompt token lengths |

---

## 4. Incident Response Playbooks

### Playbook A: External LLM Provider Outage
**Symptom:** Alerts `ProviderOutage` or `HighLatencyP95` trigger; logs show `provider_timeout` or `503 Service Unavailable` from external API.
1. The backend automatically switches to deterministic fallback responses (children receive safe greetings or continue structured exercises without interruption).
2. Verify external status page (Google Cloud / Gemini API status).
3. If prolonged outage: Toggle `LLM_PROVIDER=mock` or configure alternative model endpoint in environment variables without database downtime.
4. Notify guardians via status banner if generative conversation mode is temporarily degraded.

### Playbook B: Database Connection Failure
**Symptom:** Backend `/health` reports database failure; 500 errors spike.
1. Verify managed PostgreSQL health, replica lag, and CPU/storage metrics.
2. Check database connection pool limits (`pool_size`, `max_overflow`).
3. If primary database is unresponsive: trigger automated failover to standby replica.
4. Update connection string `DATABASE_URL` and restart backend pods.

### Playbook C: Secret Key Rotation
**Symptom:** Scheduled quarterly rotation or compromised credentials.
1. Generate new API key in Google Cloud Console.
2. Update secret store (Kubernetes Secrets / Cloud Secret Manager).
3. Perform rolling restart of backend services with the new `GEMINI_API_KEY`.
4. Deactivate old key in Google Cloud Console after verifying zero errors on the new key.

### Playbook D: Data Deletion & Right-to-be-Forgotten Request
**Symptom:** Guardian requests deletion of child profile and conversation history.
1. Authenticate guardian request via dashboard or support ticket.
2. Execute cascading deletion endpoint:
   ```http
   DELETE /api/v1/children/{child_id}
   ```
3. Database cascading foreign keys purge `chat_turns`, `chat_sessions`, `assessment_events`, `child_skills`, and the `children` record.
4. Verify zero residual records exist for `child_id`.
5. Send written confirmation to guardian within 48 hours.

---

## 5. Escalation Contacts & On-Call Matrix

- **Primary On-Call:** Platform Engineering Team (`ops@english-learning-chatbot.local`)
- **Secondary On-Call:** Lead Backend Developer
- **Child Safety & Compliance Officer:** Designated Safeguarding Lead (`safety@english-learning-chatbot.local`)
- **Executive Escalation:** Project Lead / CTO
