"""Run full T3 test suite and write stats to ml/artifacts/test_report.json."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ml.anomaly.detect import AnomalyDetector, train_anomaly
from ml.db.neo4j_client import ping
from ml.evaluation.metrics import classification_report_dict
from ml.features.neo4j_extract import extract_all_wallet_features
from ml.features.pipeline import feature_matrix
from ml.risk_model.model import RiskModel
from ml.risk_model.train import train

ART = Path(__file__).resolve().parents[1] / "artifacts"


def main() -> None:
    print("=== NEO4J ===")
    neo = ping()
    print(neo)

    print("\n=== RETRAIN RISK (GPU) ===")
    risk = train(source="neo4j", holdout_scenario="scenario_5_conflicting")
    print(json.dumps(risk["metrics"], indent=2))

    print("\n=== RETRAIN ANOMALY ===")
    anom_info = train_anomaly(source="neo4j")
    print(anom_info)

    df = extract_all_wallet_features()
    X = feature_matrix(df)
    y = df["label"].astype(int)

    model = RiskModel.load(ART / "risk_scoring_xgb_gpu_latest.joblib")
    proba = model.predict_proba_positive(X)
    pred = (proba >= 0.5).astype(int)
    full = classification_report_dict(y, pred, proba)

    det = AnomalyDetector.load(ART / "anomaly_isolation_forest_latest.joblib")
    anom_flags = []
    anom_scores = []
    for _, row in df.iterrows():
        sig = det.score_one(row.to_dict())
        anom_flags.append(sig.is_anomaly)
        anom_scores.append(sig.anomaly_score)

    df = df.copy()
    df["ml_probability"] = proba
    df["pred"] = pred
    df["anomaly_score"] = anom_scores
    df["is_anomaly"] = anom_flags

    print("\n=== FULL-SET RISK METRICS (all Neo4j wallets) ===")
    print(json.dumps(full, indent=2))

    print("\n=== PER-SCENARIO BREAKDOWN ===")
    per_scenario = {}
    for sid, g in df.groupby("scenario_id"):
        yg = g["label"].astype(int)
        m = classification_report_dict(yg, g["pred"].astype(int), g["ml_probability"])
        row = {
            "n": int(len(g)),
            "positives": int(yg.sum()),
            "avg_ml_probability": round(float(g["ml_probability"].mean()), 4),
            **m,
        }
        per_scenario[str(sid)] = row
        print(
            f"{sid}: n={row['n']} pos={row['positives']} "
            f"avg_ml={row['avg_ml_probability']} "
            f"P={m['precision']} R={m['recall']} F1={m['f1']}"
        )

    print("\n=== PER-WALLET SCORES ===")
    cols = [
        "wallet_id",
        "scenario_id",
        "label",
        "ml_probability",
        "pred",
        "anomaly_score",
        "is_anomaly",
    ]
    table = df[cols].sort_values("ml_probability", ascending=False)
    print(table.to_string(index=False))

    summary = {
        "neo4j": neo,
        "wallets": int(len(df)),
        "labeled_positive": int(y.sum()),
        "labeled_negative": int((y == 0).sum()),
        "predicted_positive": int(pred.sum()),
        "ml_probability_mean": round(float(proba.mean()), 4),
        "ml_probability_std": round(float(proba.std()), 4),
        "ml_probability_min": round(float(proba.min()), 4),
        "ml_probability_max": round(float(proba.max()), 4),
        "anomaly_flagged": int(sum(anom_flags)),
        "anomaly_score_mean": round(float(np.mean(anom_scores)), 4),
        "device": model.device,
        "model_version": model.model_version,
        "holdout_metrics": risk["metrics"],
        "full_set_metrics": full,
        "per_scenario": per_scenario,
        "per_wallet": table.to_dict(orient="records"),
    }
    out = ART / "test_report.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
