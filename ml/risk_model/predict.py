"""
Thin predict helpers for T1 integration (GPU risk model + anomaly signal).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from ml.anomaly.detect import AnomalyDetector
from ml.features import pipeline as feat_pipeline
from ml.risk_model.model import RiskModel

ARTIFACT_DIR = Path(
    os.environ.get(
        "MODEL_ARTIFACT_PATH",
        str(Path(__file__).resolve().parents[1] / "artifacts"),
    )
)


def _risk_path() -> Path:
    gpu = ARTIFACT_DIR / "risk_scoring_xgb_gpu_latest.joblib"
    if gpu.exists():
        return gpu
    return ARTIFACT_DIR / "risk_scoring_rf_latest.joblib"


def _anomaly_path() -> Path:
    return ARTIFACT_DIR / "anomaly_isolation_forest_latest.joblib"


_CACHED_RISK_MODEL: RiskModel | None = None
_CACHED_ANOMALY_MODEL: AnomalyDetector | None = None


def score_wallet(raw_features: dict[str, Any]) -> dict[str, Any]:
    global _CACHED_RISK_MODEL
    feats = feat_pipeline.features_from_row(raw_features)
    if _CACHED_RISK_MODEL is None:
        _CACHED_RISK_MODEL = RiskModel.load(_risk_path())
    return _CACHED_RISK_MODEL.predict_one(feats).to_api_dict()


def score_wallet_from_neo4j(address: str) -> dict[str, Any]:
    from ml.features.neo4j_extract import extract_wallet_features

    feats = extract_wallet_features(address)
    return score_wallet(feats)


def anomaly_wallet(raw_features: dict[str, Any]) -> dict[str, Any]:
    feats = feat_pipeline.features_from_row(raw_features)
    det = AnomalyDetector.load(_anomaly_path())
    return det.score_one(feats).to_api_dict()


def score_case_wallets(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        pred = score_wallet(row)
        if "wallet_id" in row:
            pred["wallet_id"] = row["wallet_id"]
        if "case_id" in row:
            pred["case_id"] = row["case_id"]
        out.append(pred)
    return out
