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

