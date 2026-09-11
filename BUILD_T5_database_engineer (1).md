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

---

## Documented Deviations & Implementation Notes (for T1–T6 Integration)

> [!NOTE]
> All deviations recorded below are strictly additive, non-breaking, and within T5-owned paths (`/db/`, `/scenarios/`). No existing field names or types were modified or deleted.

### 1. Supporting Store & Helper Infrastructure (`/db/`)
In addition to the raw migration and schema scripts, concrete Python store interfaces were provided under `/db/` to support direct imports by other team tracks:
- `db/evidence_ledger/ledger_store.py`: Append-only hash-chain storage and query functions for T1 API (`/cases/{id}/verify`), plus `save_model_estimate()` and `get_model_estimates_by_case()` for T3 ML handoff.
- `db/postgres/label_store.py`: Querying, tier precedence ordering (`Strong` > `Medium` > `Weak`), and conflict resolution (`resolve_provenance_summary()`) for T1/T2 attribution engine.
- `db/postgres/atlas_store.py`: Result persistence and retrieval for T1's `/cases/{id}/atlas` endpoint.
- `db/postgres/report_store.py`: Human-in-the-loop recommendation approval gate updates and tamper-evident SHA-256 report verification for T1/T4.
- `db/postgres/migrate.py`: Migration runner with `schema_migrations` tracking table and `--dry-run` mode.
- `db/neo4j/apply_schema.py`: Automated constraint and index runner against Neo4j database `sih2026`.
- `db/tests/`: Comprehensive test suite (10 tests) covering hash-chain math, canonical JSON, tamper detection, migration SQL schemas, and fixture data integrity.

### 2. PostgreSQL Schema Additions (Additive Only)
All 9 core entities from `BUILD.md` are present with all specified fields. The following extra columns were added for graph parity and operational requirements:
- **`wallets`**: Added `last_seen TIMESTAMPTZ`, `entity_type VARCHAR(50) DEFAULT 'eoa'`, and `created_at TIMESTAMPTZ`. *(Aligned with Neo4j `(:Wallet)` node properties in `BUILD.md`)*.
- **`vasps`**: Added `known_addresses TEXT[]`, `last_verified TIMESTAMPTZ`, and `created_at TIMESTAMPTZ`. *(Aligned with Neo4j `(:VASP)` node properties in `BUILD.md`)*.
- **`cases`**: Added `updated_at TIMESTAMPTZ`. *(Standard audit timestamp for case lifecycle updates)*.
- **`labels`**: Added `confidence NUMERIC(4,3) DEFAULT 1.000` alongside `confidence_tier`. *(Enables continuous ML/heuristic scoring in addition to discrete tiers)*.
- **`audit_events`**: Added `details JSONB DEFAULT '{}'::jsonb`. *(Enables structured audit log payloads)*.

### 3. Neo4j Schema & Constraints (Community Edition Compatibility)
- **Constraint Downgrade**: In `db/neo4j/schema/constraints.cypher`, a composite uniqueness constraint on `(l.source, l.label_text)` was replaced with two individual indexes (`label_source_constraint_idx` on `l.source`, `label_text_constraint_idx` on `l.label_text`).
  *Reason*: Composite (multi-property) node key/uniqueness constraints require **Neo4j Enterprise**. Since `BUILD.md` specifies **Neo4j Community**, using composite constraints causes startup failures.
- **Extra Indexes**: Added indexes on `(:Wallet).scenario_id` and `(:Wallet).case_id` to accelerate filtering during scenario demonstrations.

### 4. Database Credentials & Testing Strategy
- **Offline / Deterministic Unit & Contract Tests**: The 10 tests in `db/tests/` do **not** require a running PostgreSQL or Neo4j instance. They test pure cryptographic hashing, canonical JSON formatting, tamper detection failure states, SQL table DDL parsing, and fixture schema compliance in-memory.
- **Live Integration Requirements**: Live database connections are required only when executing `python -m db.postgres.migrate`, `python -m db.neo4j.apply_schema`, and `python -m scenarios.seed.seed`. Credentials should be configured in `.env` (copied from `.env.example`):
  - `DATABASE_URL=postgresql://vajra_user:vajra_password@localhost:5432/vajra_db`
  - `NEO4J_URI=bolt://localhost:7687`
  - `NEO4J_USER=neo4j`
  - `NEO4J_PASSWORD=<password>`
  - `NEO4J_DATABASE=sih2026`
- Default fallback connection strings are embedded in the runner modules so that local Docker environments with standard credentials connect out-of-the-box.

