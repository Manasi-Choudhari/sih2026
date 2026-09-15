# VAJRA Database Engine (T5)

Welcome to the **VAJRA (SIH 26183)** database subsystem. This module provides schema management, data persistence, graph indexing, the cryptographic Evidence Ledger, and scenario seed pipelines for the multi-chain financial intelligence platform.

---

## Directory Structure

```text
db/
├── evidence_ledger/          # Cryptographic tamper-evident hash-chain engine
│   ├── hash_chain.py         # Bit-for-bit deterministic canonical JSON & SHA-256 chaining
│   ├── verify.py             # Chain integrity verification & tamper detection
│   └── ledger_store.py       # PostgreSQL persistence for evidence & model_estimates
├── neo4j/                    # Neo4j Graph DB schema & indexes
│   ├── schema/
│   │   ├── constraints.cypher # Node uniqueness constraints (Community Edition compatible)
│   │   └── indexes.cypher     # Traversal & relationship indexes
│   └── apply_schema.py       # Automated Cypher runner
├── postgres/                 # PostgreSQL relational storage & migrations
│   ├── migrations/           # Numbered SQL migrations (001_init.sql to 005_recommendation_reports.sql)
│   ├── migrate.py            # Migration runner with schema_migrations tracking
│   ├── label_store.py        # Label provenance, tier ordering, & conflict resolution
│   ├── atlas_store.py        # ATLAS hypothesis results persistence
│   └── report_store.py       # Recommendation approval gates & report hash verification
├── tests/                    # Offline unit & contract test suite (10/10 tests)
└── requirements.txt          # Python dependencies
```

---

## Quick Start

### 1. Environment Configuration
Copy `.env.example` from repo root to `.env`:
```ini
DATABASE_URL=postgresql://vajra_user:vajra_password@localhost:5432/vajra_db
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=sih2026
```

### 2. Run Migrations & Apply Graph Schema
```powershell
# Run PostgreSQL migrations
python -m db.postgres.migrate

# Apply Neo4j constraints & indexes
python -m db.neo4j.apply_schema
```

### 3. Seed Scenario Fixtures
```powershell
# Load 5 demonstration scenarios into both Postgres & Neo4j
python -m scenarios.seed.seed

# Reset/clean scenario data
python -m scenarios.seed.reset
```

### 4. Run Test Suite
```powershell
python -m pytest db/tests/ -v
```

---

## Documented Deviations & Implementation Notes (for T1–T6 Integration)

> [!NOTE]
> All deviations are strictly additive, non-breaking, and confined to T5-owned paths (`/db/`, `/scenarios/`). No existing field names or types were modified or deleted.

### 1. Supporting Store Modules (`/db/`)
To support clean programmatic integration by other teams, concrete Python store modules were implemented:
- **`db/evidence_ledger/ledger_store.py`**: Append-only hash-chain storage and query functions for T1 API (`/cases/{id}/verify`), plus `save_model_estimate()` and `get_model_estimates_by_case()` for T3 ML handoff.
- **`db/postgres/label_store.py`**: Querying, tier precedence ordering (`Strong` > `Medium` > `Weak`), and conflict resolution (`resolve_provenance_summary()`) for T1/T2 attribution engine.
- **`db/postgres/atlas_store.py`**: Result persistence and retrieval for T1's `/cases/{id}/atlas` endpoint.
- **`db/postgres/report_store.py`**: Human-in-the-loop recommendation approval gate updates and tamper-evident SHA-256 report verification for T1/T4.
- **`db/postgres/migrate.py`**: Migration runner with `schema_migrations` tracking table and `--dry-run` mode.
- **`db/neo4j/apply_schema.py`**: Automated constraint and index runner against Neo4j database `sih2026`.

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

### 4. Database Credentials & Testing Architecture
- **Offline / Deterministic Unit & Contract Tests**: The 10 tests in `db/tests/` do **not** require a running PostgreSQL or Neo4j instance. They test pure cryptographic hashing, canonical JSON formatting, tamper detection failure states, SQL table DDL parsing, and fixture schema compliance in-memory.
- **Live Integration Requirements**: Live database connections are required only when executing migrations (`migrate.py`), applying schemas (`apply_schema.py`), and seeding (`seed.py`). Credentials are read from `.env` with sensible local Docker defaults.
