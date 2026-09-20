# BUILD_T3.md — AI/ML + Analytics
> ⚠️ AGENT INSTRUCTIONS: You are building ONLY the items in this file. Nothing else. Build exactly as specified.

## Your Scope
A small number of *supporting* statistical models — not the crime-solving AI. Tracing and attribution stay rule-based and explainable (owned by T1). Your models prioritize and flag; they never manufacture facts or become the final attribution.

> **Hard rule from the source spec:** "The model may prioritize what deserves attention. It must NOT manufacture facts or convert a statistical estimate into evidence."
> - Your output is always labeled `model_output` in the data — never mixed with proven facts.
> - Your model never decides final VASP attribution (that's T1's rule-based engine, M12).
> - Your model never claims two wallets are "the same owner" with certainty — only as a probability/signal.
> - If your model and the deterministic rules disagree, the rules win by default, and the disagreement is shown to the investigator, not hidden.

## Your Files
- `/ml/features/` — feature engineering pipeline
- `/ml/risk_model/` — Model 1: risk scoring
- `/ml/anomaly/` — Model 2: anomaly detection
- `/ml/evaluation/` — held-out evaluation + model versioning

## Your Tasks (ordered by priority)

### Task 1: ML scope + evaluation plan (Day 1)
- What to build: define the feature-vector contract with T1/T2 (what graph-derived features you'll consume); define the evaluation plan (train/held-out split, metrics).
- Acceptance criteria: feature contract frozen and committed alongside the other Day 1 contracts.

### Task 2: Ground-truth scenario labels (Day 2, shared with T2/T5)
- What to build: ground-truth labels/scenario metadata for the 5 synthetic scenarios so model evaluation has something real to check against.
- Acceptance criteria: labels available in the shared scenario fixture set.

### Task 3: Feature extraction pipeline (Day 3–4)
- What to build: convert graph-derived signals (hop counts, timing/amount patterns, clustering strength, label reliability, fan-out/fan-in stats) into a feature vector per wallet/case.
- Inputs: normalized graph data (T2), trace-derived features (T1)
- Outputs: feature vectors consumed by both your models
- Acceptance criteria: feature pipeline runs end-to-end on at least 2 scenario fixtures.

### Task 4: Model 1 — Risk Scoring (Day 6, build this first of the two models)
- What to build: Random Forest or Gradient Boosting classifier (scikit-learn) predicting a "how suspicious is this case" score, used to help investigators prioritize.
- Must be explainable (feature importance) — this matters for an investigation tool.
- Must NOT be treated as final attribution or a legal conclusion; it's a sorting tool only.
- Acceptance criteria: held-out evaluation metrics documented; API returns the model estimate as a distinct field, separate from the rule-based risk factors.

### Task 5: Model 2 — Anomaly Detection (Day 7, only if Model 1 is stable)
- What to build: anomaly signal for dormant-wallet activation / large behavioral deviation from a wallet's own history, feeding the information-gap engine as one more signal, not a verdict.
- Acceptance criteria: signal integrates into T1's information-gap ranking without overriding rule-based outputs.

### Task 6: ML API integration (Days 6–8)
- What to build: expose model outputs via the agreed feature/response contract so T1's backend and T4's frontend can consume `model_output`-labeled fields.
- Acceptance criteria: risk/confidence/evidence cards on the frontend correctly display the model estimate as separate from rule-based confidence.

### Task 7: Model freeze + judge explainability prep (Day 10)
- What to build: freeze model artifacts/version; prepare a short, plain-language explanation of what the model does and does not decide, for judge Q&A.
- Acceptance criteria: model artifact frozen; explanation ready and consistent with the hard rule above.

## Contracts You Must Honor
- Feature-vector contract (frozen Day 1), `model_output` labeling convention, three-number framework (your model output is one number among three, never merged).

## DO NOT
- Do not build anything outside your scope list (no typology classification, no GNN, no LLM narrative layer — all explicitly P2/P3, out of scope for 10 days).
- Do not let your model decide final VASP attribution.
- Do not present a probability as a proven fact anywhere in the UI or reports.
- Do not modify files owned by other teammates.
