"""
Feature engineering pipeline.

Primary path for MVP: load synthetic / fixture feature tables.
Optional path: pull graph signals from Neo4j when T2/T5 data is available.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ml.features.feature_spec import (
    FEATURE_NAMES,
    empty_feature_row,
    validate_feature_vector,
)

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_CSV = ROOT / "data" / "synthetic" / "wallet_features.csv"


def features_from_row(raw: dict[str, Any]) -> dict[str, float | int]:
    """Normalize an arbitrary dict into the frozen feature contract."""
    row = empty_feature_row()
    for name in FEATURE_NAMES:
        if name in raw and raw[name] is not None:
            row[name] = raw[name]
    # Derived: avg_tx_size if not supplied
    if (not raw.get("avg_tx_size")) and row["tx_count"]:
        total = float(row["total_in"]) + float(row["total_out"])
        row["avg_tx_size"] = total / max(int(row["tx_count"]), 1)
    errors = validate_feature_vector(row)
    if errors:
        raise ValueError(f"feature contract violation: {errors}")
    return row


def dataframe_from_records(records: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    meta_cols = ("wallet_id", "case_id", "scenario_id", "label")
    for rec in records:
        feat = features_from_row(rec)
        out = {k: rec.get(k) for k in meta_cols if k in rec}
        out.update(feat)
        rows.append(out)
    return pd.DataFrame(rows)


def load_synthetic_features(path: Path | None = None) -> pd.DataFrame:
    """Load labeled synthetic feature table used until Neo4j fixtures land."""
    csv_path = path or SYNTHETIC_CSV
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Synthetic feature CSV not found at {csv_path}. "
            "Run ml/data/generate_synthetic.py or wait for T2/T5 fixtures."
        )
    df = pd.read_csv(csv_path)
    # Re-validate each row through the contract
    records = df.to_dict(orient="records")
    return dataframe_from_records(records)


def extract_features_for_wallets(
    wallet_signals: list[dict[str, Any]],
) -> pd.DataFrame:
    """
    Convert graph/trace-derived signal dicts (from T1/T2) into feature vectors.

    Expected keys per item: wallet_id, case_id (optional), plus any FEATURE_NAMES.
    """
    return dataframe_from_records(wallet_signals)


def feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return only model input columns in contract order."""
    missing = [c for c in FEATURE_NAMES if c not in df.columns]
    if missing:
        raise ValueError(f"DataFrame missing features: {missing}")
    return df.loc[:, list(FEATURE_NAMES)].astype(float)


# --- Optional Neo4j extraction (used when graph is live) ---

NEO4J_WALLET_SIGNAL_QUERY = """
MATCH (w:Wallet {address: $address})
OPTIONAL MATCH (w)-[t:TRANSACTION]-()
WITH w, collect(t) AS txs
RETURN w.address AS wallet_id,
       w.chain AS chain,
       w.cluster_id AS cluster_id,
       size(txs) AS tx_count
"""


def extract_from_neo4j(
    driver: Any,
    addresses: list[str],
    extra_signals: dict[str, dict[str, Any]] | None = None,
) -> pd.DataFrame:
    """
    Pull minimal wallet stats from Neo4j and merge with caller-supplied
    trace/label signals (T1 pattern outputs). Full Cypher feature pack
    expands once T2 graph schema is populated.
    """
    extra_signals = extra_signals or {}
    records: list[dict[str, Any]] = []
    with driver.session() as session:
        for address in addresses:
            result = session.run(NEO4J_WALLET_SIGNAL_QUERY, address=address)
            neo = result.single()
            base = empty_feature_row()
            if neo:
                base["tx_count"] = int(neo["tx_count"] or 0)
            merged = {**base, **extra_signals.get(address, {}), "wallet_id": address}
            records.append(merged)
    return dataframe_from_records(records)
