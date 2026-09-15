# T3 AI/ML — Teammate Handoff & Test Guide

**Owner:** T3 (AI/ML + Analytics)  
**Module path:** `/ml`  
**Status:** Local scaffold + Neo4j demo seed + GPU risk model working  
**Last updated:** 2026-09-10

---

## 1. What we have done (T3)

### Built
| Area | Location | Notes |
|---|---|---|
| Feature contract (frozen) | `ml/features/feature_spec.py` | **Read-only for others** — T1/T2 supply these fields |
| Feature pipeline | `ml/features/pipeline.py` | Normalizes rows to the contract |
| Neo4j feature extract | `ml/features/neo4j_extract.py` | Pulls wallet features from DB `sih2026` |
| Neo4j client | `ml/db/neo4j_client.py` | Uses repo `.env` (`NEO4J_*`) |
| Demo graph seed | `ml/data/seed_neo4j.py` | 5 scenarios + dormant wallets into Neo4j |
| Ground-truth proposal | `ml/data/scenario_ground_truth.json` | T5 should merge into `/scenarios` |
| Synthetic CSV (fallback) | `ml/data/synthetic/wallet_features.csv` | Used if Neo4j empty |
| **Model 1 — Risk scoring (GPU)** | `ml/risk_model/` | XGBoost on CUDA (`device=cuda`) |
| **Model 2 — Anomaly** | `ml/anomaly/detect.py` | Isolation Forest (CPU; signal only) |
| Metrics + versioning | `ml/evaluation/` | Held-out metrics + artifact tags |
| Predict helpers for T1 | `ml/risk_model/predict.py` | `score_wallet`, `score_wallet_from_neo4j` |
| Trained artifacts | `ml/artifacts/` | `risk_scoring_xgb_gpu_latest.joblib`, anomaly latest, `risk_metrics.json` |

### Hard rules (everyone must honor)
- ML output is always labeled **`model_output`** — never treated as evidence/fact.
- ML **does not** decide final VASP attribution (T1 rules win on disagreement).
- Three numbers stay separate: **rule risk score** | **attribution confidence** | **`ml_probability`**.
- Do **not** merge ML into Evidence Ledger as proven fact.

### What we explicitly did **not** build
- Model 3 infra fingerprinting, GNN, typology, LLM narrative (P2/P3 / out of 10-day scope)
- Case APIs, UI, Evidence Ledger, chain adapters (other owners)

---

## 2. What T3 needs from each teammate

### T1 — Backend / Investigation Logic
| Need | Why | When |
|---|---|---|
| Confirm how you will call ML | Import `score_wallet` / `score_wallet_from_neo4j` **or** HTTP wrapper | ASAP |
| Pass contracted features (or wallet address after graph is live) | Feature vector must match `feature_spec.py` | Day 3–6 |
| Expose `ml_probability` as its **own** field on case/attribution APIs | Three-number framework | Day 6–7 |
| Surface ML vs rules **disagreement** to investigator | Spec hard rule | Day 7–8 |
| Do **not** write ML scores into Evidence as facts | Keep `model_output` separate | Always |

**Suggested API shape T1 can return to T4:**
```json
{
  "rule_risk_score": 0.72,
  "attribution_confidence": 0.81,
  "ml_probability": 0.78,
  "ml": {
    "output_label": "model_output",
    "is_model_output": true,
    "model_name": "risk_scoring_xgb_gpu",
    "model_version": "risk_xgb_gpu-...",
    "device": "cuda",
    "top_features": [{"feature": "touches_known_mixer", "importance": 0.59}],
    "disclaimer": "Statistical prioritization signal only. Does not decide VASP attribution or prove facts."
  }
}
```

**Python call (current):**
```python
from ml.risk_model.predict import score_wallet, score_wallet_from_neo4j

# From address already in Neo4j
score_wallet_from_neo4j("s1_hop1")

# Or from a feature dict matching feature_spec
score_wallet({"total_in": 2.5, "total_out": 2.4, "tx_count": 3, ...})
```

---

### T2 — Blockchain / Graph data
| Need | Why | When |
|---|---|---|
| Real scenario fixtures in Neo4j (BTC+ETH) | Replace T3 demo seed for training/eval | Day 2–3 |
| Normalized wallet/tx fields we can query | Feature extraction | Day 3+ |
| Cross-chain link props (`correlation_confidence`, bridge flags) | Features `touches_bridge`, `cross_chain_confidence` | Day 5 |
| Tell us when demo_seed data can be wiped | Avoid polluting production-like demo | Before Day 9 |

**Until T2 fixtures land:** T3 uses `python -m ml.data.seed_neo4j` demo graph (tagged `demo_seed: true`).

---

### T3 — Us (for visibility)
| Deliverable | Status |
|---|---|
| Feature contract | Done |
| Neo4j extract + GPU risk train | Done (demo data) |
| Anomaly signal | Done (CPU IF) |
| Retrain on real fixtures | Pending T2/T5 |
| Judge Q&A explanation | Pending freeze Day 10 |

---

### T4 — Frontend
| Need | Why | When |
|---|---|---|
| `ThreeNumberCard`: show ML as **third** number only | Never merge scores | Day 7 |
| Label ML clearly (`model_output` / “model estimate”) | Investigator trust + judges | Day 7 |
| Optional: show `top_features` + disclaimer from ML payload | Explainability | Day 7–8 |
| Do not present ML as attribution tier | Tiers are T1 | Always |

---

### T5 — Database
| Need | Why | When |
|---|---|---|
| Postgres table for model outputs (e.g. `model_estimate`) | Persist versioned `model_output` per case/wallet | Day 6 |
| Merge `ml/data/scenario_ground_truth.json` into `/scenarios` | Shared ground truth | Day 2 |
| Keep Neo4j schema stable for Wallet / TRANSACTION / CROSS_CHAIN_LINK / Label / VASP | Feature queries depend on it | Day 1+ |
| Confirm `NEO4J_DATABASE=sih2026` (or update `.env`) | Local connect | Ongoing |

**Suggested `model_estimate` columns:**
`estimate_id`, `case_id`, `wallet_id`, `model_name`, `model_version`, `score`, `label`, `top_features` (JSONB), `generated_at`, `is_model_output` (always true).

---

### T6 — DevOps / Security / Demo
| Need | Why | When |
|---|---|---|
| Env wiring: `MODEL_ARTIFACT_PATH`, `NEO4J_*`, `ML_DEVICE=cuda` (or CPU fallback policy for demo machines) | Reproducible train/serve | Day 1 / Docker |
| Bake frozen `.joblib` into offline demo image | Day 9 offline requirement | Day 9 |
| GPU optional for judge laptops — document CPU fallback if needed | Demo reliability | Day 9–10 |
| Do not commit `.env` secrets | Password safety | Always |

---

## 3. Environment (local T3 setup)

Repo `.env` (gitignored) expects:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your password>
NEO4J_DATABASE=sih2026
MODEL_ARTIFACT_PATH=ml/artifacts
ML_DEVICE=cuda
```

Install:
```powershell
cd c:\Users\choud\OneDrive\Desktop\sih2026
python -m pip install -r ml/requirements.txt
```

Requires: Neo4j running with database `sih2026`. GPU risk training expects NVIDIA + CUDA-capable XGBoost (`ML_DEVICE=cuda`).

---

## 4. How to test what we built

### A. Smoke test — Neo4j connect + seed
```powershell
python -c "from ml.db.neo4j_client import ping; print(ping())"
python -m ml.data.seed_neo4j
```
**Pass if:** `database` is `sih2026`, seed prints Wallet/TRANSACTION counts (non-zero).

### B. Feature extraction from Neo4j
```powershell
python -c "from ml.features.neo4j_extract import extract_all_wallet_features; df=extract_all_wallet_features(); print(df.shape); print(df[['wallet_id','scenario_id','label']].head(10))"
```
**Pass if:** rows > 0, columns include contracted features (`tx_count`, `peel_chain_score`, `ml`-ready fields), no contract validation error.

### C. Train GPU risk model
```powershell
python -m ml.risk_model.train --source neo4j
```
**Pass if:**
- metrics JSON prints with `"device": "cuda"`
- files appear: `ml/artifacts/risk_scoring_xgb_gpu_latest.joblib`, `ml/artifacts/risk_metrics.json`

CSV fallback (no Neo4j):
```powershell
python ml/data/generate_synthetic.py
python -m ml.risk_model.train --source csv
```

### D. Train anomaly model
```powershell
python -m ml.anomaly.detect
```
**Pass if:** `anomaly_isolation_forest_latest.joblib` written under `ml/artifacts/`.

### E. Predict from Neo4j wallet
```powershell
python -c "from ml.risk_model.predict import score_wallet_from_neo4j; import json; print(json.dumps(score_wallet_from_neo4j('s1_hop1'), indent=2)); print(json.dumps(score_wallet_from_neo4j('s4_mixer'), indent=2))"
```
**Pass if:**
- `output_label` == `model_output`
- `is_model_output` == true
- `device` == `cuda`
- `ml_probability` between 0 and 1
- mixer wallet scores higher / more suspicious than a cold/benign wallet (sanity check)

### F. Contract validation
```powershell
python -c "from ml.features.feature_spec import FEATURE_NAMES, validate_feature_vector, empty_feature_row; r=empty_feature_row(); print(len(FEATURE_NAMES), validate_feature_vector(r))"
```
**Pass if:** `validate_feature_vector` returns `[]`.

### G. Held-out evaluate
```powershell
python -m ml.risk_model.evaluate --holdout scenario_5_conflicting
```
**Pass if:** runs without crash and prints precision/recall (numbers may be weak on tiny demo holdout — expected until real fixtures).

---

## 5. Integration checklist (team)

- [ ] T1 reads `feature_spec.py` and confirms call path
- [ ] T2 replaces demo seed with real fixtures
- [ ] T5 adds `model_estimate` + merges ground truth
- [ ] T4 renders three separate numbers + ML disclaimer
- [ ] T6 wires env + freezes artifact in Docker offline bundle
- [ ] T3 retrains on real fixtures and freezes model version for Day 10

---

## 6. Judge-ready one-liner (T3)

> Our ML model only estimates how much a case deserves investigator attention (`ml_probability`). It does **not** decide VASP attribution or create evidence; deterministic rules remain primary, and any ML–rule disagreement is shown openly.

---

## 7. Contact / ownership

| Path | Owner |
|---|---|
| `/ml/**` | T3 only |
| `/backend/api/openapi.yaml` | T1 (T3 does not edit) |
| `/scenarios/fixtures/` | T5 merges; T3 proposes labels |
| DB migrations | T5 |

Questions for T3: ping the AI/ML owner with the wallet address / case_id and whether you need import vs HTTP.
