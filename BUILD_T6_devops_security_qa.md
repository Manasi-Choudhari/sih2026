# BUILD_T6.md — DevOps / Security + QA-Demo Lead
> ⚠️ AGENT INSTRUCTIONS: You are building ONLY the items in this file. Nothing else. Build exactly as specified.

## Your Scope
This role exists because the team grew from 5 to 6 — it splits the old "DB+DevOps" role in two so DB (T5) gets a dedicated owner and this cross-cutting set (infra, security, audit, testing, demo reliability) gets one too. You are cross-cutting from Day 1: every other teammate's work has to run inside what you build.

## Your Files
- `/infra/docker/` — Docker Compose stack
- `/infra/auth/` — JWT + RBAC middleware
- `/infra/rate_limiting/` — rate limiting middleware
- `/infra/audit/` — audit logging middleware
- `/infra/demo/` — offline demo packaging, fallback behavior, reset scripts
- `/scenarios/acceptance/` — scenario acceptance + adversarial test suite

## Your Tasks (ordered by priority)

### Task 1: Docker Compose skeleton + CI (Day 1)
- What to build: Compose file wiring Postgres, Neo4j, Redis, backend, frontend, ML service, object storage — enough for every teammate to run the whole stack locally from Day 1 onward. Basic CI (lint + test on push).
- Acceptance criteria: `docker compose up` brings up every service without manual steps, using T1/T5's frozen contracts.

### Task 2: Auth + RBAC skeleton (Day 2)
- What to build: JWT auth middleware and a role model (e.g., investigator vs. supervisor) that T1's endpoints and T4's UI can both build against.
- Acceptance criteria: `/auth/login` issues a token; a protected route rejects an unauthenticated call.

### Task 3: Scenario test harness (Day 2, shared with T2/T3/T5)
- What to build: the test runner that will execute all 5 synthetic scenarios end-to-end and compare against expected outputs — built early so every module can be checked against it as it lands.
- Acceptance criteria: harness runs (even against stubs) by Day 2 and reports pass/fail per scenario.

### Task 3b: ML env wiring + GPU/CPU fallback (Day 1 Docker, then Day 9, per T3's handoff)
- What to build: wire `MODEL_ARTIFACT_PATH`, `NEO4J_DATABASE`, `ML_DEVICE` into Docker/CI from Day 1. T3's risk model trains/serves on GPU (`ML_DEVICE=cuda`, XGBoost+CUDA) with a CPU/CSV fallback path already built — you own making sure the offline demo image works on a judge laptop with **no GPU**: document and test the CPU fallback explicitly, don't assume GPU will be present.
- On Day 9, bake T3's frozen `.joblib` artifacts (`ml/artifacts/`) into the offline demo image so no retraining happens at demo time.
- Never commit `.env` secrets (Neo4j password, etc.) — confirm `.env` stays gitignored.
- Acceptance criteria: offline demo image runs risk scoring correctly on a CPU-only machine, not just on your dev GPU box.

### Task 4: Rate limiting + explorer-API resilience support (Day 3–4)
- What to build: rate limiting middleware; support T2 in adding graceful fallback for explorer API failures (cached data, visible degraded-mode indicator).
- Acceptance criteria: repeated calls are throttled correctly; simulated explorer outage doesn't crash the pipeline.

### Task 5: Audit logging (Day 6, alongside T5's Evidence Ledger work)
- What to build: `AuditEvent` capture middleware for every state-changing action (case creation, approval, report generation, verify calls).
- Acceptance criteria: `/cases/{id}/audit` returns a complete, ordered trail for a full scenario run.

### Task 6: RBAC enforcement + unauthorized-action test (Day 8)
- What to build: enforce role checks on recommendation approval and report generation specifically; a test proving an unauthorized role is blocked.
- Acceptance criteria: unauthorized action attempt is blocked and audited, and T4's UI reflects the block.

### Task 7: Scenario acceptance run (Day 9)
- What to build: run all 5 scenarios twice through the full integrated pipeline, log correctness + latency, file P0-only defect reports back to owners.
- Acceptance criteria: 5/5 scenarios pass twice in a row.

### Task 8: Offline demo packaging (Day 9)
- What to build: pre-indexed demo dataset, fully self-contained Docker Compose bundle (no internet calls on the critical path), one-command reset-between-runs script, and a documented fallback path if any live component fails during judging.
- Acceptance criteria: on a machine with no internet access, `docker compose up` + reset script reproduces the demo from a clean state.

### Task 9: Adversarial test suite (Day 10)
- What to build: tests for poisoned/stale/conflicting labels, mixer/privacy boundary handling, fan-out explosion, ML-vs-rule disagreement (rules must win), evidence tampering (must FAIL verify), and unauthorized-action attempts.
- Acceptance criteria: adversarial test report produced; no test reveals an unsupported claim reaching the UI.

### Task 10: Freeze + rehearsal (Day 10)
- What to build: final clean-install smoke test, coordinate 3 full timed rehearsals with the team, prep judge Q&A logistics (which teammate answers which question type).
- Acceptance criteria: demo completes within time budget 3/3 rehearsals; code/data/models frozen.

## Contracts You Must Honor
- Every service you containerize must expose the ports/env vars from BUILD.md's Environment Variables table.
- `NCRP_MOCK_MODE` must always be `true` in this build's Compose config.

## DO NOT
- Do not enable any live NCRP/SAHYOG integration — mock only.
- Do not let the demo depend on any internet-reachable service on its critical path.
- Do not soften an adversarial test to make it pass — a caught issue must be routed back to the owning teammate, not hidden.
- Do not modify files owned by other teammates.
