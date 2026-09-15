# BUILD_T5.md — Database Engineer
> ⚠️ AGENT INSTRUCTIONS: You are building ONLY the items in this file. Nothing else. Build exactly as specified.

## Your Scope
PostgreSQL schema/migrations, Neo4j schema, the Evidence Ledger's persistence + hash-chain verification, and label provenance storage. (DevOps/security/demo packaging is T6's job in this 6-person split — coordinate closely but don't own it.)

## Your Files
- `/db/postgres/migrations/` — Postgres schema migrations
- `/db/neo4j/schema/` — Neo4j constraints/indexes
- `/db/evidence_ledger/` — hash-chain persistence + verify logic
- `/scenarios/seed/` — shared seed/reset script (co-owned with T2/T3)

## Your Tasks (ordered by priority)

### Task 1: Freeze schemas (Day 1)
- What to build: Postgres entities exactly per BUILD.md's table (Complaint, Case, Wallet, VASP, Label, Evidence, Recommendation, Alert, AuditEvent) and Neo4j constraints for the Wallet/VASP/Label/TRANSACTION/CROSS_CHAIN_LINK/LABELED_AS shapes.
- Acceptance criteria: migrations committed; schemas match BUILD.md exactly; T1's API contract and your schema agree field-for-field.

### Task 2: Seed/reset pipeline (Day 2, shared with T2/T3)
- What to build: one-command seed script loading the 5 scenario fixtures into both Postgres and Neo4j, and a reset command for demo repeatability.
- Acceptance criteria: seed → query → trace start works from a clean database.

### Task 3: Graph indexes + persistence (Day 3)
- What to build: indexes supporting T1's trace engine queries and T2's neighborhood lookups at demo-scale performance.
- Acceptance criteria: performance holds under Scenario 1's trace without timing out.

### Task 4: Label provenance DB (Day 4)
- What to build: storage supporting T1's attribution engine — source, freshness, confidence_tier per label, queryable by wallet.
- Acceptance criteria: conflicting-labels scenario returns all relevant labels with correct provenance.

### Task 5: ATLAS persistence (Day 5)
- What to build: storage for `AtlasResult` records (alternatives, contradictions, missing data, robustness score) tied to a case.
- Acceptance criteria: ATLAS results persist and are retrievable via `/cases/{id}/atlas`.

### Task 6: Evidence Ledger (Day 6) — your highest-priority single deliverable
- What to build: append-only, hash-chained evidence records.
```
record_hash = SHA256(canonical_json(record_without_hash) + previous_record_hash)

verify():
    previous = "GENESIS"
    for record in ordered_case_records:
        expected = SHA256(canonical_json(record_without_hash) + previous)
        if expected != record.content_hash: return FAIL
        previous = record.content_hash
    return PASS
```
- File(s): `/db/evidence_ledger/`
- Acceptance criteria: hash chain verifies on a clean case; a deliberately tampered record produces a detectable FAIL via `/cases/{id}/verify`.

### Task 6b: `model_estimate` table + ground-truth merge (Day 6, per T3's handoff)
- What to build: a new Postgres table persisting versioned ML output per case/wallet — this was added after T3's build, not in the original schema freeze.
```
model_estimate: estimate_id, case_id, wallet_id, model_name, model_version,
                 score, label, top_features (JSONB), generated_at,
                 is_model_output (always true)
```
- Also merge T3's `ml/data/scenario_ground_truth.json` proposal into `/scenarios` (shared folder, you have final merge authority there).
- Confirm `NEO4J_DATABASE=sih2026` matches your Neo4j schema setup, or coordinate an `.env` update with T3 if it should change.
- Acceptance criteria: `model_estimate` rows persist correctly and are retrievable by case_id; merged ground truth is available to the shared scenario test harness.

### Task 7: Recommendation/report persistence (Days 6–8)
- What to build: storage for recommendation records with approval_status, and generated-report metadata (hash/timestamp/version) for T1's report generator.
- Acceptance criteria: approval gate state persists correctly; report metadata is retrievable and matches its stored hash.

### Task 8: Integration + performance hardening (Days 8–10)
- What to build: fix schema/query issues found during full-pipeline integration; support T6's offline demo package with a pre-indexed, ready-to-load database snapshot.
- Acceptance criteria: fresh Docker environment (built with T6) loads your pre-indexed snapshot and runs the demo with no internet.

## Contracts You Must Honor
- Exact Postgres/Neo4j entity shapes from BUILD.md.
- Evidence record hash-chain formula above, unchanged.

## DO NOT
- Do not change schema field names/types without a team-level decision — this breaks T1's API and T4's UI simultaneously.
- Do not build DevOps/security/demo packaging — that's T6's scope; coordinate, don't own.
- Do not modify files owned by other teammates.
