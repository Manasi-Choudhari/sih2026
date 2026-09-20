"""
VAJRA (SIH 26183) — Label Provenance Store
Supports T1's attribution engine by fetching, ranking, and resolving
provenance, freshness, and confidence tiers for wallet labels.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Obtain a PostgreSQL connection."""
    import psycopg

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ConnectionError("PostgreSQL not configured (DATABASE_URL not set)")
    return psycopg.connect(database_url, connect_timeout=1)


def add_label(
    label_id: str,
    wallet_id: str,
    source: str,
    label_text: str,
    confidence_tier: str,
    confidence: float = 1.0,
    source_type: str = "CROWDSOURCE",
    last_verified: Optional[datetime] = None,
    provenance_details: Optional[Dict[str, Any]] = None,
) -> None:
    """Store or update a label with full provenance metadata."""
    if last_verified is None:
        last_verified = datetime.now(timezone.utc)
    if provenance_details is None:
        provenance_details = {}

    import json

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO labels (
                    label_id, wallet_id, source, label_text, confidence_tier,
                    confidence, source_type, last_verified, provenance_details
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (label_id) DO UPDATE SET
                    source = EXCLUDED.source,
                    label_text = EXCLUDED.label_text,
                    confidence_tier = EXCLUDED.confidence_tier,
                    confidence = EXCLUDED.confidence,
                    source_type = EXCLUDED.source_type,
                    last_verified = EXCLUDED.last_verified,
                    provenance_details = EXCLUDED.provenance_details;
                """,
                (
                    label_id,
                    wallet_id,
                    source,
                    label_text,
                    confidence_tier,
                    confidence,
                    source_type,
                    last_verified,
                    json.dumps(provenance_details),
                ),
            )
        conn.commit()


def get_labels_by_wallet_address(address: str) -> List[Dict[str, Any]]:
    """
    Fetches all active labels for a given wallet address, ordered by confidence tier and freshness.
    Tier precedence: Strong > Medium > Weak > Unknown
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    l.label_id,
                    l.wallet_id,
                    w.address,
                    l.source,
                    l.label_text,
                    l.confidence_tier,
                    l.confidence,
                    l.source_type,
                    l.last_verified,
                    l.first_seen,
                    l.provenance_details
                FROM labels l
                JOIN wallets w ON l.wallet_id = w.wallet_id
                WHERE w.address = %s AND l.is_active = TRUE
                ORDER BY
                    CASE l.confidence_tier
                        WHEN 'Strong' THEN 1
                        WHEN 'Medium' THEN 2
                        WHEN 'Weak' THEN 3
                        ELSE 4
                    END,
                    l.confidence DESC,
                    l.last_verified DESC NULLS LAST;
                """,
                (address,),
            )
            rows = cur.fetchall()

    results = []
    for r in rows:
        results.append(
            {
                "label_id": r[0],
                "wallet_id": r[1],
                "address": r[2],
                "source": r[3],
                "label_text": r[4],
                "confidence_tier": r[5],
                "confidence": float(r[6]) if r[6] is not None else 1.0,
                "source_type": r[7],
                "last_verified": r[8].isoformat() if r[8] else None,
                "first_seen": r[9].isoformat() if r[9] else None,
                "provenance_details": r[10] or {},
            }
        )
    return results


def resolve_provenance_summary(address: str) -> Dict[str, Any]:
    """
    Computes a provenance resolution summary for T1:
    - Lists all distinct labels.
    - Identifies if conflict exists (different entity labels with similar confidence).
    - Suggests the governing tier pressure (per Scenario 5: conflicting_labels_lower_reliability).
    """
    labels = get_labels_by_wallet_address(address)
    if not labels:
        return {
            "address": address,
            "has_conflict": False,
            "labels": [],
            "top_label": None,
            "effective_tier": "Unknown",
        }

    distinct_entities = {lbl["label_text"] for lbl in labels}
    has_conflict = len(distinct_entities) > 1

    # If conflicting labels exist without a dominant Strong official label, downgrade tier
    top = labels[0]
    effective_tier = top["confidence_tier"]
    if has_conflict and effective_tier != "Strong":
        effective_tier = "Weak"

    return {
        "address": address,
        "has_conflict": has_conflict,
        "distinct_entity_count": len(distinct_entities),
        "labels": labels,
        "top_label": top,
        "effective_tier": effective_tier,
    }
