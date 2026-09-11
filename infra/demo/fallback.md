# VAJRA Offline Demo & Fallback Guide (T6 Task 8 & Judge Prep)

## 1. Overview
During SIH judging, internet connectivity is unpredictable and presentation time is strictly limited (typically 8–10 minutes). VAJRA is architected to run **completely offline** with zero critical-path reliance on public networks.

---

## 2. No-Internet Demo Execution Mode

### Offline Guarantees
- **All Core Services Run Locally:** PostgreSQL, Neo4j, Redis, MinIO, FastAPI backend, ML inference, and Next.js frontend communicate exclusively via the local Docker bridge network (`vajra_network`) or localhost.
- **Explorer API Independence:** Blockchain explorers (Etherscan, Blockchair) are decoupled. In demo mode, all transaction hops for the 5 scenarios are pre-loaded via deterministic fixtures (`scenarios/fixtures/`). If an external API is called, `ExplorerCircuitBreaker` instantly returns cached fixture data without hanging or crashing.
- **NCRP / SAHYOG Simulation:** In compliance with the competition spec, `NCRP_MOCK_MODE=true` is hardcoded. All external intelligence feeds display a visible `[Simulated]` badge.

---

## 3. CPU Fallback Path (No-GPU Judge Laptop)

T3's primary risk model trains on CUDA-enabled GPU hardware (`ML_DEVICE=cuda`). However, competition judge laptops often lack NVIDIA GPUs.

### How the CPU Fallback Operates:
1. **Config:** Set `ML_DEVICE=cpu` in `.env` or Docker environment.
2. **Inference:** The Isolation Forest anomaly detector runs natively on CPU. The XGBoost risk scoring model loads pre-compiled weights from `ml/artifacts/risk_scoring_xgb_gpu_latest.joblib` and scores feature vectors on standard x86_64 CPU cores.
3. **Graph Fallback:** If Neo4j is temporarily disconnected, the ML pipeline automatically loads feature vectors from `ml/data/synthetic/wallet_features.csv`.
4. **Validation Command:**
   ```bash
   python -c "from ml.risk_model.predict import score_wallet; print(score_wallet({'tx_count': 5, 'total_in': 10.0, 'total_out': 9.8}))"
   ```

---

## 4. One-Command Demo Reset

Between judging presentations or rehearsal runs, transient cases, test transactions, and audit trails must be reset to pristine state within seconds.

### On Windows:
```cmd
infra\demo\reset.bat
```

### On Linux / macOS:
```bash
./infra/demo/reset.sh
```

**What this resets:**
- Flushes transient Redis cache entries.
- Restores deterministic initial state in Neo4j graph (`sih2026`).
- Clears ephemeral audit events.
- Executes `scenarios/acceptance/test_runner.py --stub` to verify that all 5 scenarios pass cleanly.

---

## 5. Judge Q&A Defense for T6

> **Judge Question:** *"What happens to the demo if the internet connection drops or times out mid-presentation?"*
>
> **T6 Answer:**  
> *"Nothing fails, Sir. VAJRA's entire critical path runs 100% offline inside self-contained containers on localhost. The transaction subgraphs for all 5 fraud scenarios are locally materialized in Neo4j, model weights are pre-baked in `ml/artifacts`, external explorer calls automatically fall back to cached fixtures via our circuit-breaker middleware, and NCRP is explicitly run in deterministic simulated mode. We can pull the Ethernet cable right now and run the complete investigation end-to-end without a single error."*
