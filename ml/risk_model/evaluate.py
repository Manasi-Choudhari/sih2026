"""
Evaluate a saved risk model on synthetic / held-out features.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ml.evaluation.metrics import classification_report_dict
from ml.features.pipeline import feature_matrix, load_synthetic_features
from ml.risk_model.model import RiskModel

_ART = Path(__file__).resolve().parents[1] / "artifacts"
DEFAULT_MODEL = (
    _ART / "risk_scoring_xgb_gpu_latest.joblib"
    if (_ART / "risk_scoring_xgb_gpu_latest.joblib").exists()
    else _ART / "risk_scoring_rf_latest.joblib"
)


def evaluate(
    model_path: Path,
    holdout_scenario: str | None = "scenario_5_conflicting",
) -> dict:
    model = RiskModel.load(model_path)
    df = load_synthetic_features()
    if holdout_scenario and "scenario_id" in df.columns:
        df = df[df["scenario_id"] == holdout_scenario].copy()
    X = feature_matrix(df)
    y = df["label"].astype(int)
    proba = model.predict_proba_positive(X)
    pred = (proba >= 0.5).astype(int)
    report = classification_report_dict(y, pred, proba)
    report["model_version"] = model.model_version
    report["model_path"] = str(model_path)
    report["n_rows"] = int(len(df))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--holdout", default="scenario_5_conflicting")
    args = parser.parse_args()
    report = evaluate(args.model, holdout_scenario=args.holdout)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
