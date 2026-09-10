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
