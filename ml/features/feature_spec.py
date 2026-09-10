"""
Feature-vector contract (T3 owns this file).
T1/T2 read this to know which graph-derived fields to supply.
Do not change without an explicit team decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FeatureDtype = Literal["float", "int", "bool"]


@dataclass(frozen=True)
class FeatureDef:
    name: str
    dtype: FeatureDtype
    description: str
    source: str  # "graph" | "trace" | "label" | "derived"


# Frozen Day-1 feature vector — one row per wallet in a case context.
FEATURE_DEFINITIONS: tuple[FeatureDef, ...] = (
    FeatureDef("total_in", "float", "Total inbound value (native units)", "graph"),
    FeatureDef("total_out", "float", "Total outbound value (native units)", "graph"),
    FeatureDef("tx_count", "int", "Number of transactions touching this wallet", "graph"),
    FeatureDef("avg_tx_size", "float", "Mean absolute transaction amount", "derived"),
    FeatureDef("dormant_days_before_activity", "float", "Days idle before current burst", "graph"),
    FeatureDef("avg_time_between_tx_hours", "float", "Mean gap between sequential txs (hours)", "graph"),
    FeatureDef("pct_value_moved_10min", "float", "Fraction of inbound value moved out within 10 minutes", "trace"),
    FeatureDef("fan_out_max", "int", "Max outputs from a single tx", "graph"),
    FeatureDef("fan_in_max", "int", "Max inputs into a single receive burst", "graph"),
    FeatureDef("hops_to_nearest_vasp", "float", "Hop distance to nearest labeled VASP; -1 if none", "trace"),
    FeatureDef("hops_to_nearest_mixer", "float", "Hop distance to mixer/privacy boundary; -1 if none", "trace"),
    FeatureDef("touches_known_mixer", "bool", "Wallet on a known mixer path (0/1)", "label"),
    FeatureDef("touches_bridge", "bool", "Wallet participates in a CROSS_CHAIN_LINK (0/1)", "graph"),
    FeatureDef("peel_chain_score", "float", "0–1 strength of peel-chain value-decay pattern", "trace"),
    FeatureDef("label_reliability", "float", "0–1 aggregate reliability of labels on this wallet", "label"),
    FeatureDef("conflicting_labels", "bool", "Two or more conflicting entity labels present (0/1)", "label"),
    FeatureDef("clustering_strength", "float", "0–1 strength of co-spend / cluster signal", "graph"),
    FeatureDef("cross_chain_confidence", "float", "Bridge correlation confidence; 0 if same-chain only", "trace"),
)

FEATURE_NAMES: tuple[str, ...] = tuple(f.name for f in FEATURE_DEFINITIONS)

# Output labeling convention — never merge with rule-based evidence.
MODEL_OUTPUT_LABEL = "model_output"

# Three-number framework: this module produces only ML probability.
# Rule risk score and attribution confidence are owned by T1.
ML_FIELD_NAME = "ml_probability"


def empty_feature_row() -> dict[str, float | int]:
    """Default zeros for all contracted features."""
    row: dict[str, float | int] = {}
    for f in FEATURE_DEFINITIONS:
        if f.dtype == "bool":
            row[f.name] = 0
        elif f.dtype == "int":
            row[f.name] = 0
        else:
            row[f.name] = 0.0
    return row


def validate_feature_vector(features: dict) -> list[str]:
    """Return list of contract violations (empty = OK)."""
    errors: list[str] = []
    for name in FEATURE_NAMES:
        if name not in features:
            errors.append(f"missing feature: {name}")
    for key in features:
        if key not in FEATURE_NAMES and key not in ("wallet_id", "case_id", "scenario_id", "label"):
            errors.append(f"unknown feature: {key}")
    return errors
