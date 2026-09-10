"""
Train GPU risk scoring model on Neo4j-extracted features (default)
or synthetic CSV fallback.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from ml.evaluation.metrics import classification_report_dict
from ml.evaluation.versioning import make_version_tag, resolve_artifact_path
from ml.features.pipeline import feature_matrix, load_synthetic_features
from ml.risk_model.model import RiskModel

ARTIFACT_DIR = Path(
    os.getenv(
        "MODEL_ARTIFACT_PATH",
        str(Path(__file__).resolve().parents[1] / "artifacts"),
    )
)
METRICS_PATH = Path(ARTIFACT_DIR) / "risk_metrics.json"


def _load_frame(source: str):
    if source == "neo4j":
        from ml.features.neo4j_extract import extract_all_wallet_features

        return extract_all_wallet_features()
    return load_synthetic_features()


def train(
    holdout_scenario: str = "scenario_5_conflicting",
    source: str = "neo4j",
    artifact_dir: Path | None = None,
) -> dict:
    artifact_dir = Path(artifact_dir or ARTIFACT_DIR)
    df = _load_frame(source)

    if "scenario_id" not in df.columns:
        raise ValueError("Training data must include scenario_id for held-out split")

    train_df = df[df["scenario_id"] != holdout_scenario].copy()
    test_df = df[df["scenario_id"] == holdout_scenario].copy()

    if train_df.empty or test_df.empty:
        from sklearn.model_selection import train_test_split

        train_df, test_df = train_test_split(
            df, test_size=0.25, random_state=42, stratify=df["label"]
        )
        holdout_scenario = "random_25pct"

    X_train = feature_matrix(train_df)
    y_train = train_df["label"].astype(int)
    X_test = feature_matrix(test_df)
    y_test = test_df["label"].astype(int)

    model = RiskModel()
    if model.device != "cuda":
        raise RuntimeError(
            f"Expected CUDA training device, got {model.device}. Set ML_DEVICE=cuda."
        )
    model.model_version = make_version_tag(prefix="risk_xgb_gpu")
    model.fit(X_train, y_train)

    y_proba = model.predict_proba_positive(X_test)
    y_pred = (y_proba >= 0.5).astype(int)
    metrics = classification_report_dict(y_test, y_pred, y_proba)
    metrics["holdout_scenario"] = holdout_scenario
    metrics["train_rows"] = int(len(train_df))
    metrics["test_rows"] = int(len(test_df))
    metrics["model_version"] = model.model_version
    metrics["device"] = model.device
    metrics["data_source"] = source
    metrics["feature_importance"] = model.global_feature_importance()
    metrics["note"] = (
        "Prototype GPU XGBoost model trained on Neo4j/synthetic features. "
        "Not a production fraud classifier. Output is model_output only."
    )

    artifact_path = resolve_artifact_path(
        artifact_dir, model.MODEL_NAME, model.model_version
    )
    model.save(artifact_path)
    latest = artifact_dir / f"{model.MODEL_NAME}_latest.joblib"
    model.save(latest)

    artifact_dir.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    return {
        "artifact_path": str(artifact_path),
        "latest_path": str(latest),
        "metrics_path": str(METRICS_PATH),
        "metrics": metrics,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train VAJRA GPU risk model")
    parser.add_argument("--holdout", default="scenario_5_conflicting")
    parser.add_argument("--source", choices=["neo4j", "csv"], default="neo4j")
    args = parser.parse_args()

    result = train(holdout_scenario=args.holdout, source=args.source)
    print(json.dumps(result["metrics"], indent=2))
    print(f"Saved model -> {result['artifact_path']}")
    print(f"Latest     -> {result['latest_path']}")
    print(f"Metrics    -> {result['metrics_path']}")


if __name__ == "__main__":
    main()
