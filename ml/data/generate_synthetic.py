"""
Generate synthetic labeled feature rows for the 5 VAJRA scenarios.

Used for train/held-out eval until T2/T5 load real fixtures into Neo4j.
Labels: 1 = suspicious / prioritize, 0 = low priority.
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT = Path(__file__).resolve().parent / "synthetic" / "wallet_features.csv"

# Columns match feature_spec + metadata
FIELDNAMES = [
    "wallet_id",
    "case_id",
    "scenario_id",
    "label",
    "total_in",
    "total_out",
    "tx_count",
    "avg_tx_size",
    "dormant_days_before_activity",
    "avg_time_between_tx_hours",
    "pct_value_moved_10min",
    "fan_out_max",
    "fan_in_max",
    "hops_to_nearest_vasp",
    "hops_to_nearest_mixer",
    "touches_known_mixer",
    "touches_bridge",
    "peel_chain_score",
    "label_reliability",
    "conflicting_labels",
    "clustering_strength",
    "cross_chain_confidence",
]


def _row(wallet_id, case_id, scenario_id, label, **feats):
    base = {k: 0 for k in FIELDNAMES}
    base.update(
        {
            "wallet_id": wallet_id,
            "case_id": case_id,
            "scenario_id": scenario_id,
            "label": label,
        }
    )
    base.update(feats)
    if not base["avg_tx_size"] and base["tx_count"]:
        base["avg_tx_size"] = (base["total_in"] + base["total_out"]) / max(base["tx_count"], 1)
    return base


def build_rows() -> list[dict]:
    rows: list[dict] = []

    # Scenario 1 — direct VASP (high risk at origin / mid hop; VASP terminal)
    rows.append(
        _row(
            "s1_victim",
            "case_s1",
            "scenario_1_direct",
            1,
            total_in=0.0,
            total_out=2.5,
            tx_count=2,
            dormant_days_before_activity=0,
            avg_time_between_tx_hours=0.2,
            pct_value_moved_10min=0.95,
            fan_out_max=1,
            fan_in_max=1,
            hops_to_nearest_vasp=1,
            hops_to_nearest_mixer=-1,
            peel_chain_score=0.1,
            label_reliability=0.9,
            clustering_strength=0.4,
        )
    )
    rows.append(
        _row(
            "s1_hop1",
            "case_s1",
            "scenario_1_direct",
            1,
            total_in=2.5,
            total_out=2.48,
            tx_count=3,
            avg_time_between_tx_hours=0.15,
            pct_value_moved_10min=0.98,
            fan_out_max=1,
            hops_to_nearest_vasp=0,
            label_reliability=0.95,
            clustering_strength=0.5,
        )
    )
    rows.append(
        _row(
            "s1_vasp",
            "case_s1",
            "scenario_1_direct",
            0,
            total_in=2.48,
            total_out=0.1,
            tx_count=40,
            avg_time_between_tx_hours=2.0,
            pct_value_moved_10min=0.05,
            fan_out_max=8,
            fan_in_max=20,
            hops_to_nearest_vasp=0,
            label_reliability=0.99,
            clustering_strength=0.9,
        )
    )
    # benign filler for s1
    rows.append(
        _row(
            "s1_cold",
            "case_s1",
            "scenario_1_direct",
            0,
            total_in=0.01,
            total_out=0.01,
            tx_count=1,
            dormant_days_before_activity=400,
            avg_time_between_tx_hours=100,
            pct_value_moved_10min=0.0,
            hops_to_nearest_vasp=6,
            label_reliability=0.2,
            clustering_strength=0.1,
        )
    )

    # Scenario 2 — peel chain
    for i, peel in enumerate([0.85, 0.88, 0.9, 0.82]):
        rows.append(
            _row(
                f"s2_peel_{i}",
                "case_s2",
                "scenario_2_peel",
                1,
                total_in=3.0 - i * 0.4,
                total_out=2.7 - i * 0.4,
                tx_count=4 + i,
                avg_time_between_tx_hours=0.5,
                pct_value_moved_10min=0.7 + i * 0.05,
                fan_out_max=2,
                hops_to_nearest_vasp=5 - i,
                peel_chain_score=peel,
                label_reliability=0.5,
                clustering_strength=0.55,
            )
        )
    rows.append(
        _row(
            "s2_normal",
            "case_s2",
            "scenario_2_peel",
            0,
            total_in=0.2,
            total_out=0.15,
            tx_count=5,
            avg_time_between_tx_hours=24,
            pct_value_moved_10min=0.1,
            peel_chain_score=0.05,
            hops_to_nearest_vasp=8,
            label_reliability=0.4,
        )
    )

    # Scenario 3 — cross-chain bridge (lower default confidence)
    rows.append(
        _row(
            "s3_btc_lock",
            "case_s3",
            "scenario_3_cross_chain",
            1,
            total_in=1.2,
            total_out=1.2,
            tx_count=2,
            pct_value_moved_10min=0.9,
            touches_bridge=1,
            cross_chain_confidence=0.55,
            hops_to_nearest_vasp=3,
            label_reliability=0.6,
        )
    )
    rows.append(
        _row(
            "s3_eth_mint",
            "case_s3",
            "scenario_3_cross_chain",
            1,
            total_in=1.18,
            total_out=1.15,
            tx_count=3,
            touches_bridge=1,
            cross_chain_confidence=0.55,
            hops_to_nearest_vasp=2,
            pct_value_moved_10min=0.8,
            label_reliability=0.55,
        )
    )
    rows.append(
        _row(
            "s3_benign",
            "case_s3",
            "scenario_3_cross_chain",
            0,
            total_in=0.05,
            total_out=0.04,
            tx_count=2,
            touches_bridge=0,
            cross_chain_confidence=0.0,
            hops_to_nearest_vasp=7,
            label_reliability=0.3,
        )
    )

    # Scenario 4 — mixer boundary
    rows.append(
        _row(
            "s4_pre_mixer",
            "case_s4",
            "scenario_4_mixer",
            1,
            total_in=4.0,
            total_out=4.0,
            tx_count=6,
            fan_out_max=25,
            pct_value_moved_10min=0.92,
            hops_to_nearest_mixer=0,
            touches_known_mixer=1,
            label_reliability=0.7,
            clustering_strength=0.3,
        )
    )
    rows.append(
        _row(
            "s4_mixer",
            "case_s4",
            "scenario_4_mixer",
            1,
            total_in=50.0,
            total_out=49.5,
            tx_count=200,
            fan_in_max=80,
            fan_out_max=80,
            touches_known_mixer=1,
            hops_to_nearest_mixer=0,
            label_reliability=0.85,
        )
    )
    rows.append(
        _row(
            "s4_quiet",
            "case_s4",
            "scenario_4_mixer",
            0,
            total_in=0.02,
            total_out=0.02,
            tx_count=1,
            dormant_days_before_activity=30,
            touches_known_mixer=0,
            hops_to_nearest_mixer=5,
            label_reliability=0.2,
        )
    )

    # Scenario 5 — conflicting labels
    rows.append(
        _row(
            "s5_conflict",
            "case_s5",
            "scenario_5_conflicting",
            1,
            total_in=1.5,
            total_out=1.4,
            tx_count=8,
            conflicting_labels=1,
            label_reliability=0.25,
            hops_to_nearest_vasp=1,
            pct_value_moved_10min=0.6,
            clustering_strength=0.35,
        )
    )
    rows.append(
        _row(
            "s5_clean_label",
            "case_s5",
            "scenario_5_conflicting",
            0,
            total_in=0.3,
            total_out=0.25,
            tx_count=4,
            conflicting_labels=0,
            label_reliability=0.9,
            hops_to_nearest_vasp=4,
            pct_value_moved_10min=0.1,
        )
    )

    # Extra dormant-activation rows for anomaly + risk diversity
    rows.append(
        _row(
            "s_dormant_hot",
            "case_extra",
            "scenario_dormant",
            1,
            total_in=0.0,
            total_out=8.0,
            tx_count=3,
            dormant_days_before_activity=365,
            avg_time_between_tx_hours=0.1,
            pct_value_moved_10min=0.99,
            fan_out_max=5,
            hops_to_nearest_vasp=2,
            label_reliability=0.4,
        )
    )
    rows.append(
        _row(
            "s_dormant_cold",
            "case_extra",
            "scenario_dormant",
            0,
            total_in=0.01,
            total_out=0.0,
            tx_count=1,
            dormant_days_before_activity=365,
            avg_time_between_tx_hours=0,
            pct_value_moved_10min=0.0,
            hops_to_nearest_vasp=-1,
            label_reliability=0.1,
        )
    )

    return rows


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
