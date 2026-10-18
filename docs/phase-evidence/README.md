# Phase Evidence

The phase gate writes machine-readable reports to `artifacts/phase-gates/`. Keep those local/CI artifacts for debugging, but do not commit reports containing environment or deployment details unless reviewed and redacted.

Each phase-specific `AGENT.md` also asks the coding agent to provide a short evidence summary covering:

- acceptance criteria satisfied;
- exact commands run and exit codes;
- relevant test counts and outcomes;
- phase gate report path;
- manual reviews still required;
- known issues and risks;
- database migrations or configuration changes.

A JSON report only verifies files and commands configured in `scripts/phase_gate.py`. It does not replace human review for safety, privacy, educational quality, or deployment readiness.
