# INTEGRATION.md — VAJRA 10-Day / 6-Person Build

## Daily Rhythm
| Time | Activity |
|---|---|
| Start of day | 15-min stand-up: yesterday / today / blocker. No long technical discussion. |
| Before coding | Contract check: confirm the shared schema/endpoint your work depends on hasn't changed. |
| Midday | Integration checkpoint: merge at least one branch into `dev`; run smoke tests. |
| Evening | Feature PRs: every completed feature ships with a test + fixture + docs/API note. |
| Night | Demo build: `dev` must execute the current critical path. |
| End of day | Checkpoint tag: tag a working state so rollback is always possible. |

## Dependency Order (who blocks whom)
1. **Day 1** — T1 (API contract) + T5 (Postgres/Neo4j schema) freeze together. Everyone else is blocked on this.
2. **Day 2** — T2 (BTC/ETH adapters) + T5/T3 (scenario fixtures + ground truth) run in parallel. T4 builds against a mock API in parallel — not blocked.
3. **Day 3** — T2 delivers normalized graph → unblocks T1's trace engine and T4's graph UI.
4. **Day 4** — T1's attribution + pattern rules depend on T5's label provenance DB and T2's graph query support.
5. **Day 5** — T1's ATLAS depends on Day 4's attribution output. T2's cross-chain depends on Day 2 fixtures.
6. **Day 6** — T5's Evidence Ledger and T3's risk model can build in parallel; both are needed for T4's Task 7.
7. **Day 7** — T4 swaps every screen from mock to real API — this is the point everyone's work becomes visibly integrated at once. Highest-risk day for contract mismatches; midday integration checkpoint is mandatory.
8. **Day 8** — Full pipeline integration + T6's RBAC/audit/rate limiting land on top of the now-real system.
9. **Day 9** — T6 leads scenario acceptance + offline packaging; everyone fixes only P0 defects found.
10. **Day 10** — T6 leads adversarial testing + freeze; no new features, only fixes.

## Milestones (compressed)
| Milestone | Day | Must work |
|---|---|---|
| M1 — Foundation | 1 | Schemas, APIs, Docker, DBs, contracts frozen. |
| M2 — Data World | 2 | BTC/ETH normalized data + Neo4j graph + 5 scenario fixtures. |
| M3 — Trace | 3 | Bounded trace returns correct ranked paths. |
| M4 — Attribution | 4 | Evidence-tiered VASP attribution + pattern detection. |
| M5 — Challenge / Cross-chain | 5 | ATLAS produces alternatives/contradictions/missing evidence; one bridge correlation works with explicit uncertainty. |
| M6 — Trust | 6 | Evidence Ledger verifies and detects tampering; risk model evaluated. |
| M7 — Action | 7 | Information gap + next-best action works; all core screens run against the real backend. |
| M8 — Product | 8 | Dashboard + report + RBAC + mock external adapter fully integrated. |
| M9 — Validation | 9 | Five scenarios pass end-to-end twice; offline demo package works. |
| M10 — Demo | 10 | Offline, repeatable, <8-minute demo and judge-ready Q&A. |

## Cross-Team Contracts (single source of truth = BUILD.md)
- API shapes: T1 defines, T4 consumes, T6 secures.
- DB shapes: T5 defines, T1/T2 write to, T6 backs up/snapshots for offline demo.
- `ml_probability` (T3's `model_output`, via `rule_risk_score` / `attribution_confidence` / `ml_probability`): T3 produces (XGBoost/GPU risk model + Isolation Forest anomaly), T1 never treats as fact, T4 displays as a distinct third number and shows an explicit "rules vs. model disagree" state when they conflict.
- Evidence hash chain: T5 implements, T1 exposes via API, T4 renders PASS/FAIL, T6 adversarially tests.

## What Happens If a Day Slips
- P0 items never slip past their milestone day without the whole team re-planning that evening.
- If something must be cut, cut UI polish or a P1 item first (per BUILD.md's priority table) — never a P0 item.
- T6 owns the go/no-go call each evening on whether the offline demo path is still reachable in the time remaining.

## Git Workflow

### Branches
- `main` — only updated from `dev` at real milestones (end of Day 1 freeze, Day 8 full-pipeline integration, Day 10 final freeze). Never commit to `main` directly.
- `dev` — the integration branch. Everyone merges here daily, not to `main`.
- One long-lived personal branch per teammate: `t1-backend`, `t2-blockchain`, `t3-ml`, `t4-frontend`, `t5-db`, `t6-infra`.

### Daily Cadence
- **Morning:** rebase your personal branch onto latest `dev` before starting work (`git pull --rebase origin dev`). Resolve conflicts small and early, not on Day 7.
- **Midday integration checkpoint** (per the Daily Rhythm table above): open a PR from your branch into `dev`, even for partial/in-progress work if it doesn't break the build. Small, frequent PRs beat one giant end-of-day PR.
- **Evening:** every completed feature PR includes its test + fixture + a one-line API/docs note if it touches a shared contract.
- **End of day:** tag `dev` at a known-working checkpoint (`day3-checkpoint`, etc.) so anyone can roll back instantly if the next day's merge goes wrong.

### PR / Review Rule
- **Contract files are reviewed by their owner before merge, no exceptions:** T1 reviews any PR touching `/backend/api/openapi.yaml`; T5 reviews any PR touching Postgres migrations or Neo4j schema; T3 reviews any PR touching `/ml/features/feature_spec.py`.
- Every other PR gets a quick sanity look from at least one teammate before merging to `dev` — doesn't need to be deep, just "does this match BUILD.md's contract for this file."
- Never push directly to someone else's owned path (see `BUILD.md`'s file-ownership tree) — open a PR against it instead, per the conflict-avoidance rules already in `BUILD.md`.
- If a PR is blocked (waiting on another teammate's contract change), say so in the PR description rather than working around it silently — this is exactly how the T2/T3 `demo_seed.py` situation should be handled going forward: a visible PR, not a silent overwrite.

### Merge to `main`
- End of Day 1: `dev` → `main` once schemas/contracts are frozen and the empty-stack `docker compose up` works.
- End of Day 8: `dev` → `main` once the full pipeline runs end-to-end.
- End of Day 10: final `dev` → `main` freeze — no further commits after the last rehearsal passes.

## Judge Q&A Prep (Day 10)

Each teammate should be ready to answer, in one sentence, from BUILD.md's original "Questions Every Team Member Must Be Able to Answer":
- T1: How does a bounded trace terminate, and why doesn't it run forever?
- T2: Why is a cross-chain link never shown with the same confidence as a same-chain hop?
- T3: What exactly does your model decide, and what does it explicitly not decide?
- T4: Why are risk score, attribution confidence, and ML probability never merged into one number?
- T5: How does the Evidence Ledger prove tampering happened, mechanically?
- T6: What happens to the demo if the internet goes down mid-presentation?
