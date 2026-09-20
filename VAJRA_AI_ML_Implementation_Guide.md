# VAJRA — AI/ML Module: Your Complete Implementation Guide
*(Written in plain English, for someone new to blockchain — you own the dataset, database, and ML model)*

---

## 0. First, some words you'll keep seeing (glossary)

Before anything else, here are the terms from the project doc, explained simply:

| Term | What it means, in plain words |
|---|---|
| **Wallet / Address** | A crypto "bank account" — a string of letters/numbers that sends or receives crypto. Not tied to a name by default. |
| **Transaction (tx)** | One transfer of crypto from one wallet to another. Has a hash (unique ID), amount, timestamp. |
| **Blockchain** | A public, shared ledger (list) of every transaction ever made on that network (e.g. Bitcoin, Ethereum). Anyone can read it. |
| **VASP** | "Virtual Asset Service Provider" — a crypto exchange or service (like Binance, WazirX). If stolen funds land in a VASP's wallet, investigators can (with legal process) ask that VASP "whose account is this?" |
| **Hop** | One step in a chain of transactions (Wallet A → Wallet B is 1 hop, B → C is another hop). |
| **Graph** | Think of wallets as dots (nodes) and transactions as arrows connecting them (edges). This is how we store and query the money trail. We use **Neo4j**, a database built specifically for graphs. |
| **Cluster / Clustering** | Grouping multiple wallet addresses that likely belong to the *same real owner*, based on behavior patterns. |
| **Mixer** | A service designed to break the trail — it mixes many people's coins together so you can't tell whose money went where. |
| **Bridge (cross-chain)** | A service that moves value from one blockchain to another (e.g., Bitcoin → Ethereum). The two sides don't share a transaction hash, so you need special logic to link them. |
| **Fan-out / Fan-in** | Fan-out = one wallet sends to many wallets at once. Fan-in = many wallets send into one wallet. Both are patterns worth flagging. |
| **Peel chain** | A money-laundering pattern where a wallet repeatedly sends most of its balance onward and keeps a small "peel" behind, hop after hop. |
| **Attribution** | Concluding "this wallet likely belongs to VASP X." This is NOT the same as proving who the *person* is — it's about which *service* holds the funds. |
| **Evidence tier** | How trustworthy a piece of proof is (Strong / Medium / Weak / Unknown), based on source quality and freshness. |
| **Evidence Ledger** | An unchangeable, hash-linked log of every fact and decision in a case — like a tamper-evident notebook. |
| **model_output** | A label the system puts on anything that came from your ML model, so nobody confuses "the model thinks X" with "we proved X." |

---

## 1. Where your job fits in the bigger picture

The full VAJRA system takes a **victim's wallet address** and tries to trace where the stolen crypto went, eventually pointing investigators to a VASP (exchange) and the evidence to back it up.

The pipeline looks like this:

```
Wallet address in
   ↓
Blockchain data is fetched & organized (teammates T2/T5)
   ↓
Stored as a graph in Neo4j: Wallet → Transaction → Wallet (teammates T2/T5)
   ↓
Bounded trace finds the relevant paths (T1)
   ↓
Deterministic RULES detect known fraud patterns (T1/T3 — mostly rule-based, NOT ML)
   ↓
      >>> YOUR ML MODELS run here — as one extra signal <<<
   ↓
VASP attribution engine ranks candidate exchanges (T1)
   ↓
ATLAS tries to disprove the leading theory (T1)
   ↓
Report + dashboard shown to investigator (T4)
```

**Your role (T3 — AI/ML + Analytics) is narrow and specific.** You are not building "the AI that solves the crime." You are building a small number of *supporting* statistical models that help prioritize and flag things — while the actual tracing and attribution stays rule-based and explainable.

This is stated as a hard rule in the source document, so it's worth repeating in bold:

> **The model may prioritize what deserves attention. It must NOT manufacture facts or convert a statistical estimate into evidence.**

Practically, this means:
- Your model's output is always labeled `model_output` in the data — never mixed in with "proven facts."
- Your model never decides the final VASP attribution — that's rule-based (M12).
- Your model never claims two wallets are "the same owner" with certainty — only as a probability/signal.
- If your model and the deterministic rules disagree, the deterministic rules win by default, and the disagreement itself gets shown to the investigator.

---

## 2. Exactly what you are building — 3 models (in priority order)

The source document names these specific models. Build them **in this order**, because each one is progressively more optional:

### Model 1 — Risk Scoring (build this first, it's the most important)
- **What it predicts:** A "how suspicious is this wallet/case" score, used to help investigators prioritize which cases to look at first.
- **Algorithm:** Random Forest or Gradient Boosting (e.g., `scikit-learn`'s `RandomForestClassifier` or `GradientBoostingClassifier`). These are good because they're fast, work well on tabular (spreadsheet-like) data, and — importantly — you can explain *why* they gave a score (feature importance), which matters for an investigation tool.
- **Inputs:** Engineered features from the transaction graph (see Section 5 below).
- **Must NOT do:** Be treated as final attribution or a legal conclusion. It's a sorting tool, not a verdict.

### Model 2 — Anomaly Detection
- **What it predicts:** Whether a wallet's current behavior looks unusual compared to its own history (e.g., a wallet that's been dormant for a year suddenly moves a large amount — "dormant activation").
- **Algorithm:** Isolation Forest (or a similar "how different is this point from normal" method). Unlike Model 1, this doesn't need labeled fraud/not-fraud examples — it just learns what "normal" looks like and flags outliers.
- **Must NOT do:** Claim fraud with certainty. It only says "this is unusual," not "this is a crime."

### Model 3 — Infrastructure Fingerprinting
- **What it predicts:** Whether two different wallets, possibly from *different* cases, show the same underlying "operational signature" — similar timing patterns, gas fees, fan-in/fan-out shape, or bridge usage — suggesting shared infrastructure (e.g., the same laundering operation reused across multiple frauds).
- **Algorithm:** Similarity/clustering methods over behavioral features (e.g., cosine similarity on a feature vector, or clustering algorithms like DBSCAN/KMeans).
- **Must NOT do:** Claim common *ownership*. It can only say "these look operationally similar," never "these belong to the same person."

### Optional stretch goals (only attempt after Models 1–3 are solid and stable)
| Priority | Model | Notes |
|---|---|---|
| P2 | Typology classification | Only if you actually have real category labels (e.g., "phishing," "romance scam") — otherwise skip, don't fake it. |
| P2 | GNN (Graph Neural Network) | A more advanced model (GraphSAGE/GCN in PyTorch) that learns directly from the graph shape instead of hand-built features. Nice upgrade, but never let it become something the MVP depends on. |
| P3 | LLM narrative layer | Just for turning your *already-verified* structured results into readable sentences for the report. It must never touch tracing, scoring, or decisions — text generation only, after the fact. |

Do **not** start these until Models 1–3 work and are demo-stable — the project timeline explicitly deprioritizes them.

---

## 3. The data you need — and where it comes from

Since this is a hackathon build (20 days) and you can't get real leaked fraud datasets, here's the realistic data strategy:

### 3a. Two data sources
1. **Public blockchain data** — real Bitcoin/Ethereum transactions pulled through block explorer APIs (by teammates T2). This gives you *realistic structure* (real fee patterns, timing, amounts) but no fraud labels.
2. **Synthetic ground-truth scenarios** — the team is building 5 deliberately-constructed scenarios (direct VASP transfer, peel chain, cross-chain bridge, mixer boundary, conflicting labels) with **known correct answers**. This is your main source of labeled data for training/testing, since real fraud labels don't exist publicly.

### 3b. Why synthetic + public is the right approach here
You cannot train a trustworthy "is this fraud" classifier from scratch in 20 days with no real labels — and you shouldn't try to fake confidence you don't have. Instead:
- Use the **synthetic scenarios** to create clearly labeled training/test examples (you know exactly which wallets in Scenario 2 form a "peel chain," for example).
- Use **public chain data** to make sure your features behave sensibly on real-world transaction patterns (so the model isn't only trained on toy data).
- Be upfront in the report/demo that this is a prototype-scale model trained on synthetic + public data, not a production fraud model — this is explicitly expected and accepted by the project's own rules.

### 3c. What "the dataset" actually looks like
Not raw blockchain data — you need to build a **feature table** where each row is one wallet (or one case), like this:

| wallet_id | total_in | total_out | tx_count | avg_time_between_tx | fan_out_max | fan_in_max | pct_value_moved_10min | dormant_days_before_activity | touches_known_mixer | ... | label (for training only) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| w_001 | 5.2 BTC | 5.1 BTC | 14 | 3.2 hrs | 1 | 6 | 0.97 | 210 | 0 | ... | 1 (suspicious, from synthetic scenario) |

This table is what your models actually train and predict on — **not** raw transactions.

---

## 4. Database design — where your data and model outputs live

The project already fixes the overall data architecture (this is frozen on Day 1–2 by the whole team, so you build *on top of* it, not separately):

- **Neo4j** — stores the graph: Wallets, Transactions, VASPs, Labels, and how they connect. This is what you'll **query** to build your features.
- **PostgreSQL** — stores structured records: Cases, Evidence, Recommendations, and (this is where you come in) **your model's outputs**.

### 4a. The Neo4j graph shape you'll be reading from
```
(:Wallet {address, chain, first_seen, last_seen, cluster_id, entity_type})
(:VASP {name, known_addresses, last_verified})
(:Label {source, label_text, confidence, first_seen, last_verified})

(:Wallet)-[:TRANSACTION {
    tx_hash, chain, block_height, timestamp, amount, asset,
    direction, is_bridge_leg, confidence_of_link
}]->(:Wallet)

(:Wallet)-[:CROSS_CHAIN_LINK {
    source_chain_tx, dest_chain_tx, bridge_contract,
    correlation_method, correlation_confidence
}]->(:Wallet)
```
You'll run Cypher (Neo4j's query language) queries against this to pull raw numbers for feature engineering — e.g., "count of outgoing transactions per wallet in the last 24h," "max fan-out for this wallet," etc.

### 4b. What you need to ADD to the Postgres side
A table to store your model's results, something like:

```sql
CREATE TABLE model_estimate (
    estimate_id     UUID PRIMARY KEY,
    case_id         UUID REFERENCES case(case_id),
    wallet_id       TEXT,
    model_name      TEXT,       -- e.g. 'risk_scoring_v1'
    model_version   TEXT,       -- e.g. '2026-XX-XX-commit-abc123'
    score           FLOAT,      -- e.g. 0.0 - 1.0
    label           TEXT,       -- e.g. 'high_risk', 'anomalous', 'similar_infra'
    top_features    JSONB,      -- feature importances, for explainability
    generated_at    TIMESTAMP,
    is_model_output BOOLEAN DEFAULT TRUE   -- always true; keeps this clearly separate from "facts"
);
```

Why `is_model_output` and `model_version` matter: the non-negotiable project rule is **"ML outputs are explicitly marked model_output"** — every field you produce must be traceable to exactly which model version made it, and must never silently blend into the "Evidence" table as if it were a fact.

---

## 5. Feature engineering — turning the graph into numbers a model can use

This is the heart of your work. For each wallet, compute features like:

**Volume/behavior features**
- Total value in / out
- Number of transactions
- Average transaction size
- Time since first/last activity ("dormant_days")

**Timing features**
- Average time gap between incoming and next outgoing transaction (fast pass-through is suspicious)
- % of value moved out within 10 minutes of being received (`pct_value_moved_10min` — this matches the "rapid forwarding" pattern the rules engine also looks for)

**Structural (graph) features**
- Max fan-out (most outputs from one transaction)
- Max fan-in (most inputs into one transaction)
- Number of hops to nearest known VASP/mixer
- Whether wallet touches a known mixer or bridge contract

**Decay/peeling features**
- Value-decay pattern across sequential transfers (does most of the balance keep moving forward with a small "peel" left behind?)

You'll compute these using Cypher queries into Neo4j (via the Python `neo4j` driver) plus some Python/pandas aggregation.

> **Tip:** Talk to T1 and T2 early — the pattern-detection engine (M09) is *already* computing some of these signals with deterministic rules. Reuse their feature definitions where possible rather than reinventing them; this avoids the two systems disagreeing on what "fast forwarding" means.

---

## 6. Step-by-step build plan (your own checklist)

This maps to the project's Day 12–13 slots, broken into concrete sub-steps:

### Phase A — Setup (do this early, in parallel with other teams, roughly Days 1–5)
1. Get read access to the Neo4j graph and Postgres schema once frozen (Day 2).
2. Write a small Python script that connects to Neo4j and pulls a sample wallet's transactions, just to confirm you can query it.
3. Agree with T1/T2 on the **feature vector contract** — the exact list of feature names and types you'll produce. Freeze this early since your work is blocked until it exists (per the project's dependency map).

### Phase B — Data prep (Days 3–8, alongside scenario-building)
4. Once the 5 synthetic scenarios exist (Day 3) and are loaded into Neo4j (Day 5), write the feature-extraction pipeline: Neo4j → raw records → pandas DataFrame of engineered features.
5. Label your training rows using the scenario ground truth (e.g., all wallets in the "peel chain" scenario = label 1 for that pattern).
6. Split into train/test — with so little data, use a held-out scenario or k-fold cross-validation rather than a huge train/test split.

### Phase C — Model 1: Risk scoring (Day 12 target)
7. Train a Random Forest / Gradient Boosting classifier on your feature table.
8. Evaluate on held-out data — look at precision/recall, not just accuracy (with imbalanced fraud-style data, accuracy is misleading).
9. Save the trained model with a **version identifier** (e.g., timestamp + git commit hash).
10. Wrap it in a small function/service that takes a wallet_id, computes features, and returns a score + top contributing features (for explainability).
11. Write this result into the `model_estimate` table, tagged `model_output`.

### Phase D — Model 2: Anomaly detection (Day 12–13)
12. Train Isolation Forest on the "normal" behavior features (unsupervised — no labels needed).
13. Test that it correctly flags the "dormant activation" scenario as anomalous.
14. Store results the same way as Model 1.

### Phase E — Model 3: Infrastructure fingerprinting (Day 13, if time allows)
15. Build a feature vector per wallet capturing timing/gas/fan-in-out/bridge-usage "signature."
16. Use similarity scoring or clustering to find wallets with matching signatures across different cases.
17. Store as a `model_output` similarity flag, never as an ownership claim.

### Phase F — Integration (Day 12–15)
18. Expose your model results through the API (coordinate with T1) so the dashboard can show them — likely surfaced next to (not merged into) the Risk Score / Attribution Confidence / Evidence Strength "three numbers."
19. Confirm the merge test passes: **held-out evaluation results + API response format** (this is literally the project's checklist item for your workstream).

### Phase G — Adversarial testing (Day 19)
20. Test what happens when your model and the deterministic rules disagree — make sure this disagreement is surfaced honestly, not hidden or auto-resolved in the model's favor.
21. Be ready to explain your evaluation numbers to judges (see Section 8).

---

## 7. Model training & evaluation — keep it honest

Since this is a prototype with limited/synthetic data, a few important habits:

- **Always hold out data you didn't train on** before reporting any accuracy number. Even with only 5 scenarios, hold at least one back for testing.
- **Report precision/recall**, not just accuracy — in fraud-style problems, a model that just predicts "not suspicious" for everything can still look "accurate" while being useless.
- **Track feature importance** — for each prediction, be able to say "this wallet scored high risk mainly because of X, Y, Z." This is critical for investigator trust and for judges' questions.
- **Version everything** — every trained model artifact should have a version tag stored alongside its predictions, so results are reproducible (this connects directly to the project's Evidence Ledger philosophy of reproducibility).
- **Never let the model's confidence number be shown as if it were the Evidence Strength number.** They are different things computed by different systems — this is one of the project's "non-negotiable" rules.

---

## 8. Questions you should be ready to answer (from the source document)

These appear explicitly as questions every team member — especially you — must be able to answer:

- *"What exactly does your ML model predict, and how was it evaluated?"*
  → Answer with the specifics from Section 6/7 above: which model, which features, held-out evaluation, precision/recall.
- *"What if ML and deterministic rules disagree?"*
  → The deterministic rule result is treated as primary; the disagreement is shown to the investigator rather than silently resolved.

---

## 9. Suggested folder structure for your code

```
ml/
├── data/
│   ├── extract_features.py      # Neo4j → feature DataFrame
│   └── scenario_labels.py       # Attach ground-truth labels from synthetic scenarios
├── models/
│   ├── risk_scoring.py          # Model 1: Random Forest / Gradient Boosting
│   ├── anomaly_detection.py     # Model 2: Isolation Forest
│   └── fingerprinting.py        # Model 3: similarity/clustering
├── evaluation/
│   └── evaluate.py              # Held-out metrics, precision/recall, feature importance
├── serving/
│   └── api.py                   # Small service: wallet_id -> score + top features -> writes to model_estimate table
├── artifacts/                   # Saved trained models, versioned by filename/date
└── tests/
    └── test_features.py
```

---

## 10. Definition of done — your checklist

- [ ] Feature-extraction pipeline pulls consistent features from Neo4j for any wallet.
- [ ] Risk scoring model trained, evaluated on held-out data, with precision/recall documented.
- [ ] Anomaly detection model correctly flags the "dormant activation" scenario.
- [ ] (Stretch) Infrastructure fingerprinting flags similarity across at least one pair of test wallets.
- [ ] All model outputs are written to the database tagged `model_output`, with `model_version`.
- [ ] API returns your model's score/label separately from Risk Score / Attribution Confidence / Evidence Strength — never merged into them.
- [ ] You can explain, in plain words, what your model does and does not prove — to a judge, cold.

---

**Bottom line to keep in your head the whole build:** you are the "second opinion" system, not the judge. Your models make the investigator's job faster by pointing at what deserves attention — the actual conclusions and evidence always come from the rule-based, explainable parts of the system.
