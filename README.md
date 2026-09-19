# VAJRA — SIH 26183: Real-Time Crypto Fraud Attribution

> Multi-chain blockchain investigation platform for tracing illicit fund flows, attributing VASP endpoints, and producing tamper-evident evidence.

📖 **Complete Project Documentation & Integration Manual**:  
See [PROJECT_MASTER_INTEGRATION_GUIDE.md](file:///d:/SIH2026/Project/sih2026/PROJECT_MASTER_INTEGRATION_GUIDE.md) for full architectural integration, role login credentials, all frontend routes, backend API endpoints, and the National Crypto Fraud Portal (NCRP / CFCFRMS / 1930) automated ingestion specification.

---

# T2 Blockchain Engineer — Setup & Guide

Owned by **T2 (Blockchain Engineer)**. All code lives under `/blockchain` and scenario chain data under `/scenarios/fixtures/`.

## What This Module Does

| Component | Purpose |
|---|---|
| **Chain Detection** | Identifies BTC vs ETH addresses by format/checksum (rejects out-of-scope chains) |
| **BTC Adapter** | Fetches Bitcoin transactions via Blockchair API with retries, backoff, and cache fallback |
| **ETH Adapter** | Fetches Ethereum transactions via Etherscan V2 API with retries, backoff, and cache fallback |
| **Normalization** | Converts raw chain data into a unified `NormalizedTransaction` schema matching Neo4j edge shape |
| **Graph Indexer** | Writes `:Wallet` nodes and `:TRANSACTION` / `:CROSS_CHAIN_LINK` edges into Neo4j |
| **Cross-Chain Correlator** | Matches lock/burn ↔ mint/release bridge events (confidence always ≤ 0.85) |
| **Scenario Fixtures** | 5 deterministic test scenarios with chain data for the offline demo |

## Prerequisites

| Requirement | Notes |
|---|---|
| Python **3.10+** | Check: `python --version` |
| Neo4j (Desktop or Docker) | Bolt port **7687** open |
| Etherscan API key | Free tier at [etherscan.io](https://etherscan.io/apis) |
| Blockchair API key (optional) | Free tier at [blockchair.com/api](https://blockchair.com/api) — adapter works without key at lower rate limits |

## Setup

### Step 1 — Install dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r blockchain/requirements.txt
```

### Step 2 — Configure `.env`
```powershell
copy .env.example .env
```

Fill in your credentials:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
EXPLORER_API_KEY_ETH=your_etherscan_key
EXPLORER_API_KEY_BTC=               # optional
```

### Step 3 — Verify Neo4j connection
```powershell
python -c "from dotenv import load_dotenv; load_dotenv(); from blockchain.indexer.worker import GraphIndexer; g = GraphIndexer(); g.connect(); print('Connected'); g.close()"
```

### Step 4 — Run tests
```powershell
python -m pytest tests/ -v
```

**Pass:** All 6 tests should pass:
```
tests/test_blockchain.py::test_chain_detection               PASSED
tests/test_blockchain.py::test_normalized_transaction_schema  PASSED
tests/test_blockchain.py::test_cross_chain_correlator_rule    PASSED
tests/test_blockchain.py::test_adapter_mock_injection         PASSED
tests/test_scenario_fixtures.py::test_fixtures_exist          PASSED
tests/test_scenario_fixtures.py::test_fixtures_parse_and_validate_transactions PASSED
```

## File Map

```text
blockchain/                          [T2 owned]
  chain_detection/
    detect.py                        ← BTC/ETH address format detection
  adapters/
    base.py                          ← Abstract adapter interface
    btc/client.py                    ← Blockchair BTC adapter
    eth/client.py                    ← Etherscan V2 ETH adapter
  normalization/
    normalize.py                     ← NormalizedTransaction + CrossChainLink schemas
  indexer/
    worker.py                        ← Neo4j graph writer + pattern query support
  cross_chain/
    correlator.py                    ← Bridge lock/mint correlation engine
  requirements.txt

scenarios/fixtures/                  [shared — T2 owns chain data]
  scenario_1_direct.json             ← Victim → Hop → VASP (ETH)
  scenario_2_peel.json               ← 4-hop peel chain (BTC)
  scenario_3_cross_chain.json        ← BTC lock → ETH mint bridge
  scenario_4_mixer.json              ← Mixer boundary + fan-out (BTC)
  scenario_5_conflicting.json        ← Conflicting entity labels (ETH)

tests/
  test_blockchain.py                 ← Unit tests for detection, schema, correlator
  test_scenario_fixtures.py          ← Fixture validation tests
```

## How Other Teammates Use T2's Code

### T1 (Backend) — Trace engine queries
```python
from blockchain.indexer.worker import GraphIndexer

indexer = GraphIndexer()
neighbors = indexer.get_wallet_outgoing_transactions("s1_victim")
fan_out = indexer.get_fan_out_metrics("s4_mixer")
timing = indexer.get_inbound_and_outbound_window("s2_peel_1")
indexer.close()
```

### T1/T5 — Writing transactions to graph
```python
from blockchain.normalization.normalize import NormalizedTransaction
from blockchain.indexer.worker import GraphIndexer

tx = NormalizedTransaction(
    tx_hash="0xabc", chain="ETH",
    from_address="0xsender", to_address="0xreceiver",
    block_height=100, timestamp="2026-09-10T12:00:00Z",
    amount=2.5, asset="ETH", direction="out",
    is_bridge_leg=False, confidence_of_link=1.0,
)
indexer = GraphIndexer()
indexer.write_transaction(tx)
indexer.close()
```

### T1 — Chain detection
```python
from blockchain.chain_detection.detect import detect_chain

chain = detect_chain("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045")  # → "ETH"
chain = detect_chain("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq")  # → "BTC"
```

## Hard Rules (Do Not Break)

- Cross-chain links use `:CROSS_CHAIN_LINK`, **never** a fake `:TRANSACTION` edge
- Cross-chain confidence is **always ≤ 0.85** (lower than same-chain)
- Live explorer fetching is **never on the demo critical path** — cached fallback only
- Do not add a 3rd chain (Tron, Monero, etc.)
- Do not edit files outside `blockchain/` or `scenarios/fixtures/` (chain data only)

---
---

# T3 AI/ML — Setup & Continue Guide

Start here if you are new to the **VAJRA AI/ML (`/ml`)** module.

For teammate contracts (what T1–T6 owe each other), see [`T3_TEAM_HANDOFF.md`](./T3_TEAM_HANDOFF.md).  
Project scope: [`BUILD.md`](../BUILD.md) + [`BUILD_T3_ai_ml_analytics.md`](../BUILD_T3_ai_ml_analytics.md).

---

## 1. What this module does

Supporting ML only — **not** final crime attribution.

| Model | Role | Tech |
|---|---|---|
| Risk scoring | `ml_probability` for investigator priority | XGBoost on **GPU (CUDA)** |
| Anomaly | Unusual / dormant-activation signal | Isolation Forest (CPU) |

Rules from T1 always win on disagreement. Outputs are always tagged `model_output`.

---

## 2. Prerequisites

| Requirement | Notes |
|---|---|
| Windows / macOS / Linux | Developed on Windows |
| Python **3.10+** | Check: `python --version` |
| Neo4j (Desktop or Server) | Bolt port **7687** open |
| NVIDIA GPU + drivers (recommended) | For `ML_DEVICE=cuda`. Without GPU, ask T3 before switching to CPU |
| Git | Clone/pull the repo |

Optional: Neo4j Browser on `http://localhost:7474` to inspect the graph.

---

## 3. First-time setup

### Step 1 — Get the code
```powershell
cd <path-to>\sih2026
```

### Step 2 — Create your `.env`
Copy the example and fill in **your** Neo4j password/database (do not commit `.env`):

```powershell
copy .env.example .env
```

Edit `.env`:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=YOUR_PASSWORD_HERE
NEO4J_DATABASE=sih2026
NEO4J_INSTANCE=sih2026
MODEL_ARTIFACT_PATH=ml/artifacts
ML_DEVICE=cuda
```

- Create a Neo4j database named `sih2026` (or change `NEO4J_DATABASE` to match yours).
- Never put real passwords in markdown or git.

### Step 3 — Install Python packages
From repo root:

```powershell
python -m pip install -r ml/requirements.txt
```

### Step 4 — Confirm Neo4j
Start Neo4j, then:

```powershell
python -c "from ml.db.neo4j_client import ping; print(ping())"
```

**Pass:** prints something like `{'database': 'sih2026', 'node_count': ...}`.

### Step 5 — Seed demo graph (if empty)
```powershell
python -m ml.data.seed_neo4j
```

Loads 5 synthetic scenarios + dormant wallets (nodes tagged `demo_seed: true`).

### Step 6 — Train models
```powershell
python -m ml.risk_model.train --source neo4j
python -m ml.anomaly.detect
```

**Pass:** `ml/artifacts/risk_scoring_xgb_gpu_latest.joblib` exists and train metrics show `"device": "cuda"`.

### Step 7 — Smoke predict
```powershell
python -c "from ml.risk_model.predict import score_wallet_from_neo4j; import json; print(json.dumps(score_wallet_from_neo4j('s1_hop1'), indent=2))"
```

**Pass:** `output_label` is `model_output`, `ml_probability` between 0 and 1.

---

## 4. Daily workflow (continue from here)

```text
1. Pull latest code
2. Ensure Neo4j is running + .env is correct
3. If graph was reset → re-seed (or load T2 fixtures when available)
4. Retrain if features/labels changed
5. Run test report
6. Only edit files under /ml (unless team agrees otherwise)
```

### Useful commands

| Goal | Command |
|---|---|
| Ping Neo4j | `python -c "from ml.db.neo4j_client import ping; print(ping())"` |
| Re-seed demo data | `python -m ml.data.seed_neo4j` |
| Extract features | `python -c "from ml.features.neo4j_extract import extract_all_wallet_features; print(extract_all_wallet_features().shape)"` |
| Train risk (Neo4j) | `python -m ml.risk_model.train --source neo4j` |
| Train risk (CSV fallback) | `python ml/data/generate_synthetic.py` then `python -m ml.risk_model.train --source csv` |
| Train anomaly | `python -m ml.anomaly.detect` |
| Score one wallet | `python -c "from ml.risk_model.predict import score_wallet_from_neo4j; print(score_wallet_from_neo4j('s4_mixer'))"` |
| Full stats report | `python -m ml.evaluation.run_test_report` |
| Held-out evaluate | `python -m ml.risk_model.evaluate --holdout scenario_5_conflicting` |

Test report output: `ml/artifacts/test_report.json`.

---

## 5. Repo map (what lives where)

```text
ml/
  features/
    feature_spec.py      ← CONTRACT — T1/T2 read; T3 owns writes
    pipeline.py          ← normalize feature rows
    neo4j_extract.py     ← Neo4j → feature table
  risk_model/
    model.py / train.py / evaluate.py / predict.py
  anomaly/
    detect.py            ← Isolation Forest signal
  evaluation/
    metrics.py / versioning.py / run_test_report.py
  data/
    seed_neo4j.py        ← demo scenarios into Neo4j
    scenario_ground_truth.json
    synthetic/           ← CSV fallback
  db/
    neo4j_client.py      ← connection from .env
  artifacts/             ← trained .joblib + metrics JSON
  requirements.txt
```

**Do not edit outside `/ml` unless you own that path** (see BUILD.md).

---

## 6. How T1 should call ML

```python
from ml.risk_model.predict import score_wallet, score_wallet_from_neo4j

# Wallet already in Neo4j
score_wallet_from_neo4j("s1_hop1")

# Or pass a feature dict matching feature_spec.FEATURE_NAMES
score_wallet({"total_in": 2.5, "tx_count": 3, ...})
```

Response always includes:
- `output_label: "model_output"`
- `ml_probability`
- `model_version`, `device`, `top_features`, `disclaimer`

Keep this **separate** from rule risk score and attribution confidence.

---

## 7. What to build next (priority)

1. **Wait for T2 fixtures** → replace demo seed with real scenario graph data.  
2. **T5 `model_estimate` table** → persist scores with `is_model_output=true`.  
3. **T1 API field** → expose `ml_probability` on case/attribution responses.  
4. **T4 UI** → third number on `ThreeNumberCard` + disclaimer.  
5. **Retrain + freeze** artifact for offline demo (Day 9–10).  
6. **Do not** start GNN / typology / LLM / infra-fingerprint (out of scope).

---

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| `NEO4J_PASSWORD missing` | Create `.env` from `.env.example` |
| Auth / connection failed | Neo4j running? Correct password? DB name exists? |
| `No wallets found` | Run `python -m ml.data.seed_neo4j` |
| `GPU required ... CUDA unavailable` | Install CUDA-capable XGBoost, or discuss CPU fallback with team (`ML_DEVICE`) |
| XGBoost device mismatch warning | Safe to ignore for now — trees still run on `cuda:0` |
| Import errors for `ml.*` | Run commands from **repo root** `sih2026` |
| Metrics look “perfect” or weird | Demo dataset is small; wait for real fixtures before claiming production quality |

---

## 9. Hard rules (do not break)

- ML may **prioritize**; it must **not** manufacture facts or final VASP attribution.  
- Label every ML field `model_output`.  
- Never merge ML into Evidence Ledger as proven fact.  
- On ML vs rules disagreement → **rules win**, show the disagreement.  
- Only install packages aligned with the project stack (see `ml/requirements.txt` / BUILD.md).

---

## 10. Quick “am I done setting up?” checklist

- [ ] `.env` filled (not committed)
- [ ] `pip install -r ml/requirements.txt` OK
- [ ] `ping()` returns your database name
- [ ] Seed (or real fixtures) loaded
- [ ] Risk model trained with `"device": "cuda"` (or agreed CPU mode)
- [ ] `score_wallet_from_neo4j('s1_hop1')` returns a probability
- [ ] Read `feature_spec.py` before changing features
- [ ] Read `T3_TEAM_HANDOFF.md` before integrating with T1–T6

You’re ready to continue from **Section 4** and the next items in **Section 7**.

---
<<<<<<< HEAD
---

# T1 Backend & Investigation Lead — Setup & Continue Guide

Start here if you are developing or maintaining the **VAJRA Backend (`/backend`)** module.

For teammate contracts (what T1–T6 owe each other), see [`BUILD_T1_backend_investigation_lead.md`](./BUILD_T1_backend_investigation_lead.md) and [`INTEGRATION.md`](./INTEGRATION.md).  
Master Project Scope: [`BUILD.md`](./BUILD.md).

---

## 1. What this module does

The **core investigation lifecycle and attribution brain** of VAJRA:

| Component | Role | Tech / Specs |
|---|---|---|
| **Case Management** | Complaint intake, queue status (`active`, `closed`), investigator assignment | FastAPI + Pydantic |
| **Bounded Trace Engine** | Priority/BFS graph tracer with hard ceilings (8 hops max, 1% value cutoff, fan-out limits) | BFS with priority scoring over Neo4j |
| **Pattern Detection** | Detect peel chains, rapid forwarding (>90% in <10m), structuring, mixer bounds, cross-chain legs | Deterministic rules on materialized subgraphs |
| **VASP Attribution** | Resolves terminal service endpoints into evidence tiers: `Strong`, `Medium`, `Weak`, `Unknown` | Multi-source provenance & corroboration engine |
| **Three-Number Framework** | `rule_risk_score` (rules) + `attribution_confidence` (VASP) + `ml_probability` (ML signal) | Distinct numbers; rules strictly win on conflict |
| **ATLAS Challenge Engine** | Stress-tests leading attributions with counter-hypotheses, contradictions, & missing data | Adversarial hypothesis ranker |
| **Evidence Ledger** | Tamper-evident audit trail linking all evidence via SHA-256 canonical hash chaining | Canonical JSON SHA-256 chain (`GENESIS` → `prev_hash`) |
| **Next-Best Action** | Ranks investigative next actions via mathematical priority formula | `(rel × attr × qual × gain) / cost` |
| **Recommendation Gate** | Human approval gate for freeze notices, subpoenas, and deep cluster monitors | Approval store (`approved`, `rejected`, `pending`) |
| **Reporting & Interop** | Standardized court-admissible dossiers with SHA-256 hashes + simulated NCRP webhook | PDF/HTML payload + mock external callback |

---

## 2. Prerequisites

| Requirement | Notes |
|---|---|
| Windows / macOS / Linux | Developed on Windows (PowerShell) |
| Python **3.10+** | Check: `python --version` |
| Neo4j (Desktop or Server) | Bolt port **7687** open for graph queries |
| Virtual Environment | `.venv` in workspace root recommended |
| Git | Repo on branch `backend_investigation` |

---

## 3. First-time setup

### Step 1 — Verify Environment
Make sure `.env` exists in the repository root (created from `.env.example`):

```powershell
copy .env.example .env
```

Ensure `.env` contains:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=YOUR_PASSWORD_HERE
NEO4J_DATABASE=sih2026
```

### Step 2 — Install Backend Python Packages
From repo root:

```powershell
python -m pip install -r backend/requirements.txt
```

### Step 3 — Run the Backend Test Suite
Verify that all 10 pipeline stages pass:

```powershell
python backend/run_tests.py
```

**Pass:** You will see `ALL 10 T1 BACKEND & INVESTIGATION PIPELINE TESTS PASSED!`.

---

## 4. Daily workflow (continue from here)

```text
1. Pull latest code from dev branch
2. Ensure virtual environment is active: .venv\Scripts\Activate.ps1
3. Launch backend API server in reload mode
4. Test endpoints via Swagger UI (http://localhost:8000/docs)
5. Run tests before committing: python backend/run_tests.py
6. Only edit files under /backend (unless team agrees otherwise)
```

### Useful commands

| Goal | Command |
|---|---|
| Start Backend Server | `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload` |
| Run All 10 T1 Tests | `python backend/run_tests.py` |
| Run Pytest Test Suite | `pytest backend/test_t1_pipeline.py -v` |
| Inspect OpenAPI Spec | Open `http://localhost:8000/openapi.json` |
| Test Auth Login | `curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"username\":\"investigator_user\",\"password\":\"secure\"}"` |
| Fetch Case Queue | `curl http://localhost:8000/cases` |
| Verify Evidence Ledger | `curl http://localhost:8000/cases/case_s1/verify` |
| Inspect Graph Subgraph | `curl http://localhost:8000/cases/case_s1/graph` |
| Inspect VASP Attribution | `curl http://localhost:8000/cases/case_s1/attribution` |
| Inspect ATLAS Challenge | `curl http://localhost:8000/cases/case_s1/atlas` |

---

## 5. Repo map (what lives where)

```text
backend/
  api/
    openapi.yaml                 ← CONTRACT — Frozen OpenAPI specification
    routes/
      api_v1.py                  ← Route definitions for all endpoints
  case_management/
    case.py                      ← Case store, status tracking, queue management
  trace/
    engine.py                    ← Bounded priority BFS graph tracer
  patterns/
    engine.py                    ← Pattern coordinator
    peel_chain.py                ← Peel chain detector
    fanout.py                    ← Fan-out / consolidation rules
    mixer_boundary.py            ← Mixer & privacy pool evidentiary boundaries
    structuring.py               ← Structuring / smurfing heuristics
  attribution/
    candidates.py                ← VASP attribution generator
    tiers.py                     ← Strong / Medium / Weak / Unknown tier rules
    evidence_ledger.py           ← SHA-256 canonical JSON hash chain & tamper detection
    provenance_rules.py          ← Label source freshness & confidence caps
  atlas/
    engine.py                    ← Counter-hypothesis & robustness assessor
    contradictions.py            ← Contradiction identification
  information_gap/
    ranking.py                   ← Next-Best-Action priority formula
  recommendation/
    engine.py                    ← Recommendation store & human approval gate
  reporting/
    report_generator.py          ← SHA-256 hashed court-ready evidence dossiers
  external/
    ncrp_mock.py                 ← Simulated NCRP / SAHYOG webhook adapter
  main.py                        ← FastAPI application entry point
  requirements.txt               ← Backend dependencies
  run_tests.py                   ← Direct test runner
  test_t1_pipeline.py            ← Unit & contract tests
```

**Do not edit outside `/backend` unless you own that path** (see `BUILD.md`).

---

## 6. How other modules interact with T1

### What T4 (Frontend) consumes from T1:
- `GET /cases` → Investigator dashboard case queue.
- `GET /cases/{id}/graph` → Force-directed transaction graph visualization.
- `GET /cases/{id}/attribution` → ThreeNumberCard (`rule_risk_score`, `attribution_confidence`, `ml_probability`).
- `GET /cases/{id}/atlas` → Counter-hypotheses and contradiction matrix.
- `GET /cases/{id}/evidence` & `/verify` → Tamper-evident ledger status (PASS/FAIL badge).
- `POST /cases/{id}/recommendations` → Action approval / rejection buttons.
- `POST /cases/{id}/report` → Court-ready dossier download.

### What T1 consumes from T3 (ML):
```python
from ml.risk_model.predict import score_wallet_from_neo4j

# Direct Python call returns ml_probability & metadata dict
ml_result = score_wallet_from_neo4j(wallet_address)
```
- Returned in attribution under `ml_probability` and `ml` dictionary.
- Always labeled `output_label: "model_output"`.
- Never written to the Evidence Ledger as an indisputable fact.
- If rules and ML disagree → **rules win**, and the disagreement is explicitly surfaced to the investigator.

---

## 7. What to build next (priority)

1. **Replace synthetic seed with live T2 fixtures** as soon as T2 pushes real BTC/ETH subgraphs.
2. **Hook PostgreSQL storage (T5)** to replace in-memory case state while preserving identical API contracts.
3. **Connect real Neo4j driver** in `/backend/trace/engine.py` using Cypher queries once Day 3 graph is finalized.
4. **Coordinate with T4 (Frontend)** on endpoint verification during the Day 7 mock-to-real API swap.
5. **Support T6 offline package verification (Day 9–10)** ensuring all routes respond with no external internet connection.

---

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'backend'` | Run python commands from the **repo root** (`sih2026`), not inside `/backend`. |
| `FastAPI port 8000 already in use` | Kill existing process or run on alternate port: `--port 8001`. |
| `Pydantic validation error on /cases` | Verify request payload keys match `CreateCaseInput` (`victim_address`, `chain`, `reported_amount`). |
| `Evidence Ledger verification fails` | Do not modify `EvidenceEntry` records in-place; append only to keep hash chain intact. |
| `ML import error from backend` | Check that `ml/` has `__init__.py` and your virtual environment has installed ML dependencies if invoking ML functions. |

---

## 9. Hard rules (do not break)

- **Rules Win Over ML**: In any attribution conflict between heuristic rules and ML models, rules strictly take precedence.
- **Three Numbers Never Collapse**: Keep `rule_risk_score`, `attribution_confidence`, and `ml_probability` as separate numbers. Never average or collapse them into one single score.
- **Tamper-Evident Ledger Integrity**: Every ledger entry must contain the canonical JSON hash of its predecessor. Never allow silent mutations.
- **Human Approval Gate**: Investigative recommendations (freezes, compliance subpoenas) must stay in `"pending"` status until an investigator or supervisor explicitly signs off.
- **Simulated Badging**: All mock external adapters (NCRP/SAHYOG) must return `simulation_mode: True` and be visibly badged as "Simulated".

---

## 10. Quick “am I done setting up?” checklist

- [ ] `.env` filled with correct Neo4j settings
- [ ] `pip install -r backend/requirements.txt` OK
- [ ] `python backend/run_tests.py` passes all 10/10 tests
- [ ] `uvicorn backend.main:app --reload` serves [http://localhost:8000/docs](http://localhost:8000/docs)
- [ ] `/cases` returns list of active investigation cases
- [ ] `/cases/case_s1/verify` returns `status: "PASS"` and `is_tampered: false`
- [ ] Read `BUILD_T1_backend_investigation_lead.md` before adding new routes or modifying contracts

You’re ready to continue from **Section 4** and work on the next priorities in **Section 7**.

---

## 11. T6 DevOps / Security + QA-Demo Lead (`/infra`, `/scenarios/acceptance`)

The T6 module provides the cross-cutting infrastructure, security, audit logging, rate limiting, and end-to-end scenario validation harness required by `BUILD.md` and `BUILD_T6_devops_security_qa.md`.

### Strict File Tree Structure (100% BUILD.md Compliant)
```text
/infra
  /docker/                            docker-compose.yml, Dockerfile.backend, Dockerfile.frontend, Dockerfile.ml
  /auth/                              jwt.py, rbac.py
  /rate_limiting/                     middleware.py
  /audit/                             audit_middleware.py
  /demo/                              offline_bundle.sh, reset.sh, fallback.md
  ci.yml

/scenarios
  /acceptance/                        test_runner.py
```

### Key Capabilities

1. **Multi-Service Docker Stack (`infra/docker/`)**:
   - Spins up `Postgres 16`, `Neo4j 5.18` (APOC plugin enabled), `Redis 7`, `MinIO`, `backend` (FastAPI), `ml` (XGBoost/Anomaly), and `frontend` (Next.js).
   - Fully isolated network (`vajra_network`) with health checks.
   - Run stack:
     ```bash
     docker compose -f infra/docker/docker-compose.yml up -d
     ```

2. **JWT Auth & Role-Based Access Control (`infra/auth/`)**:
   - `jwt.py`: Cryptographic HS256 JWT creation, decoding, and expiration enforcement.
   - `rbac.py`: Role definitions (`investigator`, `supervisor`, `admin`), permission matrices, and FastAPI route protection dependencies (`require_role`, `require_permission`).
   - Inlined contracts ensure standalone execution without requiring Python package glue (`__init__.py`).
   - Demo test credentials:
     - Investigator: `inv_sharma` / `investigator123`
     - Supervisor: `sup_verma` / `supervisor123`
     - Admin: `admin_vajra` / `admin123`

3. **Rate Limiting & Circuit Breaker (`infra/rate_limiting/middleware.py`)**:
   - In-memory sliding-window rate limiter with Redis backend support.
   - Circuit breaker with degraded mode fallback for external explorer APIs (Etherscan/Blockchair).

4. **Ordered Audit Trail Logging (`infra/audit/audit_middleware.py`)**:
   - Implements the PostgreSQL `AuditEvent` schema for tracking all state-changing actions (case creation, recommendation approval, report generation, verify calls, unauthorized attempts).
   - Fast case-specific audit trail retrieval (`audit_event_store.get_events_for_case(case_id)`).

5. **Scenario Acceptance & Adversarial Test Harness (`scenarios/acceptance/test_runner.py`)**:
   - Evaluates all 5 mandatory synthetic scenarios (`--stub` or `--live`).
   - Executes the complete 6-point Task 9 Adversarial Test Suite (`--adversarial`):
     - `ADV-01`: Poisoned / stale / conflicting label degradation to Weak/Unknown.
     - `ADV-02`: Mixer & privacy boundary clean termination (`mixer_boundary`).
     - `ADV-03`: Fan-out explosion capping (terminates as pattern event above threshold).
     - `ADV-04`: ML-vs-rule disagreement (deterministic rules take strict precedence; 3 scores unmerged).
     - `ADV-05`: Hash-chained evidence tampering detection (verify returns `FAIL`).
     - `ADV-06`: RBAC unauthorized action attempt blocking & security audit logging.
   - Run full verification:
     ```bash
     python scenarios/acceptance/test_runner.py --all
     ```

6. **Offline Demo Reliability & Reset (`infra/demo/`)**:
   - `reset.sh`: Clean one-command state restoration between demo judge runs.
   - `offline_bundle.sh`: Offline asset packaging script (no internet critical path).
   - `fallback.md`: Technical fallback documentation and judge Q&A defense.


