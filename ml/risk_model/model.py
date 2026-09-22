"""
Model 1 — Risk scoring on GPU via XGBoost (gradient boosting).

Requires NVIDIA CUDA. Refuses silent CPU fallback when ML_DEVICE=cuda.
Trees train/infer on GPU via XGBoost device='cuda'.
Output is always labeled model_output — never final VASP attribution.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

from ml.features.feature_spec import FEATURE_NAMES, ML_FIELD_NAME, MODEL_OUTPUT_LABEL
from ml.features.pipeline import feature_matrix


def _resolve_device() -> str:
    requested = os.getenv("ML_DEVICE", "cuda").lower()
    if requested in ("cuda", "gpu"):
        try:
            import xgboost as xgb

            info = xgb.build_info()
            if not info.get("USE_CUDA"):
                raise RuntimeError("Installed xgboost has USE_CUDA=False")
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                "GPU required (ML_DEVICE=cuda) but XGBoost CUDA is unavailable"
            ) from exc
        return "cuda"
    return "cpu"


@dataclass
class RiskPrediction:
    ml_probability: float
    predicted_label: int
    top_features: list[dict[str, float]]
    model_name: str
    model_version: str
    device: str
    is_model_output: bool = True
    output_label: str = MODEL_OUTPUT_LABEL

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "output_label": self.output_label,
            "is_model_output": self.is_model_output,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "device": self.device,
            ML_FIELD_NAME: self.ml_probability,
            "predicted_class": int(self.predicted_label),
            "top_features": self.top_features,
            "disclaimer": (
                "Statistical prioritization signal only. "
                "Does not decide VASP attribution or prove facts."
            ),
        }


class RiskModel:
    MODEL_NAME = "risk_scoring_xgb_gpu"

    def __init__(self, n_estimators: int = 200, random_state: int = 42):
        self.device = _resolve_device()
        self.clf = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=5,
            learning_rate=0.08,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="binary:logistic",
            eval_metric="logloss",
            tree_method="hist",
            device=self.device,
            random_state=random_state,
            n_jobs=1,
        )
        self.model_version: str = "untrained"
        self.feature_names: list[str] = list(FEATURE_NAMES)

    def fit(self, X: pd.DataFrame, y: pd.Series) -> "RiskModel":
        mat = X[self.feature_names].to_numpy(dtype=np.float32)
        self.clf.fit(mat, y.astype(np.int32))
        return self

    def predict_proba_positive(self, X: pd.DataFrame) -> np.ndarray:
        mat = X[self.feature_names].to_numpy(dtype=np.float32)
        if self.device == "cuda":
            import xgboost as xgb
            dmat = xgb.DMatrix(mat, feature_names=self.feature_names)
            raw = self.clf.get_booster().predict(dmat)
            if isinstance(raw, np.ndarray) and raw.ndim == 1:
                return raw
        proba = np.asarray(self.clf.predict_proba(mat))
        classes = [int(c) for c in list(self.clf.classes_)]
        if 1 not in classes:
            return np.zeros(len(X), dtype=np.float32)
        idx = classes.index(1)
        return proba[:, idx]

    def predict_one(self, features: dict[str, float | int]) -> RiskPrediction:
        df = pd.DataFrame([features])
        X = feature_matrix(df)
        proba = float(self.predict_proba_positive(X)[0])
        pred = int(proba >= 0.5)
        top = self._top_features_for_row(X.iloc[0])
        return RiskPrediction(
            ml_probability=round(proba, 4),
            predicted_label=pred,
            top_features=top,
            model_name=self.MODEL_NAME,
            model_version=self.model_version,
            device=self.device,
        )

    def _top_features_for_row(self, row: pd.Series, k: int = 5) -> list[dict[str, float]]:
        importances = np.asarray(self.clf.feature_importances_)
        pairs = sorted(
            zip(self.feature_names, importances, strict=True),
            key=lambda x: x[1],
            reverse=True,
        )[:k]
        return [
            {
                "feature": n,
                "importance": round(float(i), 4),
                "value": round(float(row[n]), 4),
            }
            for n, i in pairs
        ]

    def global_feature_importance(self) -> list[dict[str, float]]:
        importances = np.asarray(self.clf.feature_importances_)
        return [
            {"feature": n, "importance": round(float(i), 4)}
            for n, i in sorted(
                zip(self.feature_names, importances, strict=True),
                key=lambda x: x[1],
                reverse=True,
            )
        ]

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "clf": self.clf,
            "model_version": self.model_version,
            "feature_names": self.feature_names,
            "model_name": self.MODEL_NAME,
            "device": self.device,
        }
        joblib.dump(payload, path)
        return path

    @classmethod
    def load(cls, path: Path) -> "RiskModel":
        payload = joblib.load(path)
        obj = cls()
        obj.clf = payload["clf"]
        obj.device = _resolve_device()
        if hasattr(obj.clf, "set_params"):
            obj.clf.set_params(device=obj.device, tree_method="hist")
        obj.model_version = payload["model_version"]
        obj.feature_names = payload["feature_names"]
        return obj
