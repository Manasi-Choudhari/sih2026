# VAJRA — SIH 26183: Real-Time Crypto Fraud Attribution

> Multi-chain blockchain investigation platform for tracing illicit fund flows, attributing VASP endpoints, and producing tamper-evident evidence.

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
