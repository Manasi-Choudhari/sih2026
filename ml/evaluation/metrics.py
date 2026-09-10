"""Held-out evaluation metrics for T3 models."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def classification_report_dict(
    y_true,
    y_pred,
    y_proba=None,
) -> dict[str, Any]:
    y_true = np.asarray(y_true).astype(int)
    y_pred = np.asarray(y_pred).astype(int)
    out: dict[str, Any] = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
    }
    if y_proba is not None and len(np.unique(y_true)) > 1:
        y_proba = np.asarray(y_proba, dtype=float)
        try:
            out["roc_auc"] = round(float(roc_auc_score(y_true, y_proba)), 4)
        except ValueError:
            out["roc_auc"] = None
        try:
            out["average_precision"] = round(
                float(average_precision_score(y_true, y_proba)), 4
            )
        except ValueError:
            out["average_precision"] = None
    else:
        out["roc_auc"] = None
        out["average_precision"] = None
    return out
