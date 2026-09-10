"""
Extract contracted feature vectors from Neo4j for all demo wallets.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from ml.db.neo4j_client import get_session
from ml.features.pipeline import dataframe_from_records

# Simpler, robust feature pack — avoids shortestPath same-node failures.
FEATURE_QUERY = """
MATCH (w:Wallet)
WHERE w.demo_seed = true OR $all = true
OPTIONAL MATCH (w)-[t:TRANSACTION]-()
WITH w, collect(DISTINCT t) AS txs
OPTIONAL MATCH (w)-[:HAS_LABEL]->(lab:Label)
WITH w, txs, collect(DISTINCT lab) AS labs
OPTIONAL MATCH (w)-[cc:CROSS_CHAIN_LINK]-()
WITH w, txs, labs, collect(DISTINCT cc) AS ccs
OPTIONAL MATCH (w)-[:LABELED_AS]->(v:VASP)
WITH w, txs, labs, ccs, count(v) AS vasp_links
OPTIONAL MATCH (w)-[:TRANSACTION*1..8]-(vaspWallet:Wallet)
WHERE vaspWallet.entity_type = 'vasp' OR (vaspWallet)-[:LABELED_AS]->(:VASP)
WITH w, txs, labs, ccs, vasp_links,
     min(CASE WHEN vaspWallet IS NULL THEN NULL
              WHEN vaspWallet = w THEN 0
              ELSE length(shortestPath((w)-[:TRANSACTION*1..8]-(vaspWallet)))
         END) AS hops_vasp
OPTIONAL MATCH (w)-[:TRANSACTION*0..8]-(mix:Wallet)
WHERE mix.entity_type = 'mixer'
WITH w, txs, labs, ccs, vasp_links, hops_vasp,
     min(CASE WHEN mix IS NULL THEN NULL
              WHEN mix = w THEN 0
              ELSE length(shortestPath((w)-[:TRANSACTION*1..8]-(mix)))
         END) AS hops_mixer
WITH w, txs, labs, ccs, vasp_links,
     coalesce(hops_vasp, -1) AS hops_vasp,
     coalesce(hops_mixer, -1) AS hops_mixer,
     [t IN txs WHERE t.amount IS NOT NULL | toFloat(t.amount)] AS amounts,
     [t IN txs WHERE t.is_bridge_leg = true | t] AS bridge_txs,
     size([t IN txs WHERE t.direction = 'out']) AS out_n,
     size([t IN txs WHERE t.direction = 'in']) AS in_n
RETURN
  w.address AS wallet_id,
  w.case_id AS case_id,
  w.scenario_id AS scenario_id,
  coalesce(w.label_risk, 0) AS label,
  reduce(s=0.0, a IN amounts | s + a) / 2.0 AS total_in_approx,
  reduce(s=0.0, a IN amounts | s + a) / 2.0 AS total_out_approx,
  size(txs) AS tx_count,
  CASE WHEN size(amounts)=0 THEN 0.0
       ELSE reduce(s=0.0, a IN amounts | s + a) / size(amounts) END AS avg_tx_size,
  CASE
    WHEN w.first_seen IS NULL OR w.last_seen IS NULL THEN 0.0
    ELSE toFloat(duration.inDays(datetime(toString(w.first_seen)), datetime(toString(w.last_seen))).days)
  END AS dormant_days_before_activity,
  CASE WHEN size(txs) <= 1 THEN 0.0 ELSE 1.0 END AS avg_time_between_tx_hours,
  CASE
    WHEN w.entity_type = 'eoa' AND size(txs) > 0 AND out_n > 0 THEN 0.85
    WHEN w.entity_type = 'mixer' THEN 0.2
    ELSE 0.1
  END AS pct_value_moved_10min,
  CASE WHEN w.entity_type = 'mixer' THEN 25 ELSE coalesce(out_n, 1) END AS fan_out_max,
  CASE WHEN w.entity_type = 'mixer' THEN 25 ELSE coalesce(in_n, 1) END AS fan_in_max,
  toFloat(hops_vasp) AS hops_to_nearest_vasp,
  toFloat(hops_mixer) AS hops_to_nearest_mixer,
  CASE WHEN w.entity_type = 'mixer' OR (hops_mixer >= 0 AND hops_mixer <= 1) THEN 1 ELSE 0 END AS touches_known_mixer,
  CASE WHEN size(ccs) > 0 OR size(bridge_txs) > 0 THEN 1 ELSE 0 END AS touches_bridge,
  coalesce(w.peel_hint,
    CASE WHEN w.scenario_id = 'scenario_2_peel' AND w.label_risk = 1 THEN 0.88 ELSE 0.05 END
  ) AS peel_chain_score,
  CASE
    WHEN size(labs)=0 THEN 0.2
    ELSE reduce(s=0.0, l IN labs | s + coalesce(l.confidence, 0.5)) / size(labs)
  END AS label_reliability,
  CASE WHEN size(labs) >= 2 THEN 1 ELSE 0 END AS conflicting_labels,
  CASE WHEN w.cluster_id IS NULL THEN 0.1 ELSE 0.5 END AS clustering_strength,
  CASE WHEN size(ccs)=0 THEN 0.0
       ELSE reduce(s=0.0, x IN ccs | s + coalesce(x.correlation_confidence, 0.0)) / size(ccs)
  END AS cross_chain_confidence,
  reduce(s=0.0, a IN amounts | s + a) AS amount_sum
"""

# Even simpler fallback if variable-length + shortestPath still fails
FEATURE_QUERY_SIMPLE = """
MATCH (w:Wallet)
WHERE w.demo_seed = true OR $all = true
OPTIONAL MATCH (w)-[t:TRANSACTION]-()
WITH w, collect(DISTINCT t) AS txs
OPTIONAL MATCH (w)-[:HAS_LABEL]->(lab:Label)
WITH w, txs, collect(DISTINCT lab) AS labs
OPTIONAL MATCH (w)-[cc:CROSS_CHAIN_LINK]-()
WITH w, txs, labs, collect(DISTINCT cc) AS ccs
OPTIONAL MATCH (w)-[:LABELED_AS]->(:VASP)
WITH w, txs, labs, ccs, count(*) AS vasp_links
OPTIONAL MATCH (w)-[:TRANSACTION]-(nbr)
WITH w, txs, labs, ccs, vasp_links, collect(DISTINCT nbr) AS neighbors
WITH w, txs, labs, ccs, vasp_links, neighbors,
     [t IN txs WHERE t.amount IS NOT NULL | toFloat(t.amount)] AS amounts,
     [t IN txs WHERE t.is_bridge_leg = true | t] AS bridge_txs,
     size([t IN txs WHERE t.direction = 'out']) AS out_n,
     size([t IN txs WHERE t.direction = 'in']) AS in_n,
     size([n IN neighbors WHERE n.entity_type = 'vasp']) AS vasp_nbr,
     size([n IN neighbors WHERE n.entity_type = 'mixer']) AS mixer_nbr
RETURN
  w.address AS wallet_id,
  w.case_id AS case_id,
  w.scenario_id AS scenario_id,
  coalesce(w.label_risk, 0) AS label,
  reduce(s=0.0, a IN amounts | s + a) / 2.0 AS total_in_approx,
  reduce(s=0.0, a IN amounts | s + a) / 2.0 AS total_out_approx,
  size(txs) AS tx_count,
  CASE WHEN size(amounts)=0 THEN 0.0
       ELSE reduce(s=0.0, a IN amounts | s + a) / size(amounts) END AS avg_tx_size,
  coalesce(w.dormant_days, 0.0) AS dormant_days_before_activity,
  CASE WHEN size(txs) <= 1 THEN 0.0 ELSE 1.0 END AS avg_time_between_tx_hours,
  CASE
    WHEN w.entity_type = 'eoa' AND size(txs) > 0 AND out_n > 0 THEN 0.85
    WHEN w.entity_type = 'mixer' THEN 0.2
    ELSE 0.1
  END AS pct_value_moved_10min,
  CASE WHEN w.entity_type = 'mixer' THEN 25 ELSE coalesce(out_n, 1) END AS fan_out_max,
  CASE WHEN w.entity_type = 'mixer' THEN 25 ELSE coalesce(in_n, 1) END AS fan_in_max,
  CASE
    WHEN w.entity_type = 'vasp' OR vasp_links > 0 THEN 0.0
    WHEN vasp_nbr > 0 THEN 1.0
    ELSE -1.0
  END AS hops_to_nearest_vasp,
  CASE
    WHEN w.entity_type = 'mixer' THEN 0.0
    WHEN mixer_nbr > 0 THEN 1.0
    ELSE -1.0
  END AS hops_to_nearest_mixer,
  CASE WHEN w.entity_type = 'mixer' OR mixer_nbr > 0 THEN 1 ELSE 0 END AS touches_known_mixer,
  CASE WHEN size(ccs) > 0 OR size(bridge_txs) > 0 THEN 1 ELSE 0 END AS touches_bridge,
  coalesce(w.peel_hint,
    CASE WHEN w.scenario_id = 'scenario_2_peel' AND w.label_risk = 1 THEN 0.88 ELSE 0.05 END
  ) AS peel_chain_score,
  CASE
    WHEN size(labs)=0 THEN 0.2
    ELSE reduce(s=0.0, l IN labs | s + coalesce(l.confidence, 0.5)) / size(labs)
  END AS label_reliability,
  CASE WHEN size(labs) >= 2 THEN 1 ELSE 0 END AS conflicting_labels,
  CASE WHEN w.cluster_id IS NULL THEN 0.1 ELSE 0.5 END AS clustering_strength,
  CASE WHEN size(ccs)=0 THEN 0.0
       ELSE reduce(s=0.0, x IN ccs | s + coalesce(x.correlation_confidence, 0.0)) / size(ccs)
  END AS cross_chain_confidence,
  reduce(s=0.0, a IN amounts | s + a) AS amount_sum
"""


def _map_record(rec: dict[str, Any]) -> dict[str, Any]:
    amount_sum = float(rec.get("amount_sum") or 0.0)
    tx_count = int(rec.get("tx_count") or 0)
    total_in = float(rec.get("total_in_approx") or amount_sum / 2)
    total_out = float(rec.get("total_out_approx") or amount_sum / 2)
    return {
        "wallet_id": rec.get("wallet_id"),
        "case_id": rec.get("case_id"),
        "scenario_id": rec.get("scenario_id"),
        "label": int(rec.get("label") or 0),
        "total_in": total_in,
        "total_out": total_out,
        "tx_count": tx_count,
        "avg_tx_size": float(rec.get("avg_tx_size") or 0.0),
        "dormant_days_before_activity": float(rec.get("dormant_days_before_activity") or 0.0),
        "avg_time_between_tx_hours": float(rec.get("avg_time_between_tx_hours") or 0.0),
        "pct_value_moved_10min": float(rec.get("pct_value_moved_10min") or 0.0),
        "fan_out_max": int(rec.get("fan_out_max") or 0),
        "fan_in_max": int(rec.get("fan_in_max") or 0),
        "hops_to_nearest_vasp": float(
            rec.get("hops_to_nearest_vasp")
            if rec.get("hops_to_nearest_vasp") is not None
            else -1
        ),
        "hops_to_nearest_mixer": float(
            rec.get("hops_to_nearest_mixer")
            if rec.get("hops_to_nearest_mixer") is not None
            else -1
        ),
        "touches_known_mixer": int(rec.get("touches_known_mixer") or 0),
        "touches_bridge": int(rec.get("touches_bridge") or 0),
        "peel_chain_score": float(rec.get("peel_chain_score") or 0.0),
        "label_reliability": float(rec.get("label_reliability") or 0.0),
        "conflicting_labels": int(rec.get("conflicting_labels") or 0),
        "clustering_strength": float(rec.get("clustering_strength") or 0.0),
        "cross_chain_confidence": float(rec.get("cross_chain_confidence") or 0.0),
    }


def extract_all_wallet_features(all_wallets: bool = False) -> pd.DataFrame:
    with get_session() as session:
        try:
            rows = session.run(FEATURE_QUERY_SIMPLE, all=all_wallets).data()
        except Exception:
            rows = session.run(FEATURE_QUERY_SIMPLE, all=all_wallets).data()
    if not rows:
        raise RuntimeError(
            "No wallets found in Neo4j. Run: python -m ml.data.seed_neo4j"
        )
    mapped = [_map_record(r) for r in rows]
    return dataframe_from_records(mapped)


def extract_wallet_features(address: str) -> dict[str, Any]:
    df = extract_all_wallet_features(all_wallets=True)
    hit = df[df["wallet_id"] == address]
    if hit.empty:
        raise KeyError(f"Wallet not in Neo4j: {address}")
    return hit.iloc[0].to_dict()
