"""
Model 2 — Anomaly detection (Isolation Forest).

Flags dormant activation / large behavioral deviation vs learned "normal".
Signal only — feeds information-gap ranking; never overrides rule-based outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from ml.features.feature_spec import FEATURE_NAMES, MODEL_OUTPUT_LABEL
from ml.features.pipeline import feature_matrix
from ml.evaluation.versioning import make_version_tag, resolve_artifact_path

ARTIFACT_DIR = Path(__file__).resolve().parents[1] / "artifacts"


@dataclass
class AnomalySignal:
    anomaly_score: float  # higher = more anomalous (0–1 mapped)
    is_anomaly: bool
    model_name: str
    model_version: str
    is_model_output: bool = True
    output_label: str = MODEL_OUTPUT_LABEL

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "output_label": self.output_label,
            "is_model_output": self.is_model_output,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "anomaly_score": self.anomaly_score,
            "is_anomaly": self.is_anomaly,
            "disclaimer": (
                "Unusual vs learned normal behavior. "
                "Does not claim fraud or ownership."
            ),
        }


class AnomalyDetector:
    MODEL_NAME = "anomaly_isolation_forest"

    def __init__(self, contamination: float = 0.25, random_state: int = 42):
        self.clf = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=random_state,
        )
        self.model_version: str = "untrained"
        self.feature_names: list[str] = list(FEATURE_NAMES)

    def fit(self, X: pd.DataFrame) -> "AnomalyDetector":
        # Prefer fitting on low-risk / label==0 rows when available
        self.clf.fit(X[self.feature_names])
        return self

    def score_one(self, features: dict[str, float | int]) -> AnomalySignal:
        df = pd.DataFrame([features])
        X = feature_matrix(df)
        # decision_function: higher = more normal; negate for anomaly-ness
        raw = float(self.clf.decision_function(X[self.feature_names])[0])
        pred = int(self.clf.predict(X[self.feature_names])[0])  # -1 anomaly
        # Map roughly to 0–1 where 1 = anomalous
        anomaly_score = float(1.0 / (1.0 + np.exp(raw * 5)))
        return AnomalySignal(
            anomaly_score=round(anomaly_score, 4),
            is_anomaly=(pred == -1),
            model_name=self.MODEL_NAME,
            model_version=self.model_version,
        )

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "clf": self.clf,
                "model_version": self.model_version,
                "feature_names": self.feature_names,
                "model_name": self.MODEL_NAME,
            },
            path,
        )
        return path

    @classmethod
    def load(cls, path: Path) -> "AnomalyDetector":
        payload = joblib.load(path)
        obj = cls()
        obj.clf = payload["clf"]
        obj.model_version = payload["model_version"]
        obj.feature_names = payload["feature_names"]
        return obj


def train_anomaly(
    artifact_dir: Path | None = None,
    source: str = "neo4j",
) -> dict[str, str]:
    """
    Isolation Forest remains sklearn (CPU) — no CUDA IF in the approved stack.
    Risk scoring (Model 1) is the GPU path. Features still come from Neo4j.
    """
    artifact_dir = artifact_dir or ARTIFACT_DIR
    if source == "neo4j":
        from ml.features.neo4j_extract import extract_all_wallet_features

        df = extract_all_wallet_features()
    else:
        from ml.features.pipeline import load_synthetic_features

        df = load_synthetic_features()
    normal = df[df["label"] == 0] if "label" in df.columns else df
    if len(normal) < 3:
        normal = df
    X = feature_matrix(normal)
    det = AnomalyDetector()
    det.model_version = make_version_tag(prefix="anomaly_if")
    det.fit(X)
    path = resolve_artifact_path(artifact_dir, det.MODEL_NAME, det.model_version)
    det.save(path)
    latest = artifact_dir / f"{det.MODEL_NAME}_latest.joblib"
    det.save(latest)
    return {
        "artifact_path": str(path),
        "latest_path": str(latest),
        "version": det.model_version,
        "feature_source": source,
        "compute": "cpu_sklearn_isolation_forest",
    }


if __name__ == "__main__":
    info = train_anomaly()
    print(info)
