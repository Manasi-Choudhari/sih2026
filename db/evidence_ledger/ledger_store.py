"""
VAJRA (SIH 26183) — Evidence Ledger & Model Estimate Persistence Store
Handles appending hash-chained evidence records, fetching ordered case records,
and persisting versioned model estimates.
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from db.evidence_ledger.hash_chain import (
    GENESIS_HASH,
    compute_record_hash,
)

load_dotenv()


def get_connection():
    import psycopg

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://vajra_user:vajra_password@localhost:5432/vajra_db",
    )
    return psycopg.connect(database_url)


def get_latest_evidence_hash_for_case(case_id: str) -> str:
    """Gets the latest content_hash for a case, or 'GENESIS' if no records exist."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT content_hash
                FROM evidence
                WHERE case_id = %s
                ORDER BY created_at DESC, evidence_id DESC
                LIMIT 1;
                """,
                (case_id,),
            )
            row = cur.fetchone()
            return row[0] if row else GENESIS_HASH


def append_evidence_record(
    case_id: str,
    evidence_type: str,
    source: str,
    content: Dict[str, Any],
    software_version: str = "1.0.0",
    evidence_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Appends a new evidence record to the case's hash chain.
    Automatically resolves the previous hash and calculates content_hash.
    """
    if evidence_id is None:
        evidence_id = f"ev_{uuid.uuid4().hex[:12]}"

    prev_hash = get_latest_evidence_hash_for_case(case_id)

    record_without_hash = {
        "case_id": case_id,
        "content": content,
        "evidence_id": evidence_id,
        "software_version": software_version,
        "source": source,
        "type": evidence_type,
    }

    content_hash = compute_record_hash(record_without_hash, prev_hash)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO evidence (
                    evidence_id, case_id, type, source, content,
                    content_hash, prev_hash, software_version
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    evidence_id,
                    case_id,
                    evidence_type,
                    source,
                    json.dumps(content),
                    content_hash,
                    prev_hash,
                    software_version,
                ),
            )
        conn.commit()

    return {
        "evidence_id": evidence_id,
        "case_id": case_id,
        "type": evidence_type,
        "source": source,
        "content": content,
        "content_hash": content_hash,
        "prev_hash": prev_hash,
        "software_version": software_version,
    }


def get_evidence_records_for_case(case_id: str) -> List[Dict[str, Any]]:
    """Retrieves all evidence records for a case, strictly ordered by creation."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    evidence_id, case_id, type, source, content,
                    content_hash, prev_hash, software_version, created_at
                FROM evidence
                WHERE case_id = %s
                ORDER BY created_at ASC, evidence_id ASC;
                """,
                (case_id,),
            )
            rows = cur.fetchall()

    records = []
    for r in rows:
        records.append(
            {
                "evidence_id": r[0],
                "case_id": r[1],
                "type": r[2],
                "source": r[3],
                "content": r[4] if isinstance(r[4], dict) else json.loads(r[4]),
                "content_hash": r[5],
                "prev_hash": r[6],
                "software_version": r[7],
                "created_at": r[8].isoformat() if r[8] else None,
            }
        )
    return records


# ---------------------------------------------------------------------------
# Task 6b: ModelEstimate Persistence
# ---------------------------------------------------------------------------


def save_model_estimate(
    case_id: str,
    model_name: str,
    model_version: str,
    score: float,
    label: str,
    top_features: Optional[List[Dict[str, Any]]] = None,
    wallet_id: Optional[str] = None,
    estimate_id: Optional[str] = None,
) -> str:
    """Persists a versioned ML model estimation output."""
    if estimate_id is None:
        estimate_id = f"est_{uuid.uuid4().hex[:12]}"
    if top_features is None:
        top_features = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO model_estimates (
                    estimate_id, case_id, wallet_id, model_name, model_version,
                    score, label, top_features, is_model_output
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                RETURNING estimate_id;
                """,
                (
                    estimate_id,
                    case_id,
                    wallet_id,
                    model_name,
                    model_version,
                    score,
                    label,
                    json.dumps(top_features),
                ),
            )
            created_id = cur.fetchone()[0]
        conn.commit()
    return created_id


def get_model_estimates_by_case(case_id: str) -> List[Dict[str, Any]]:
    """Retrieves all model estimates for a case."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    estimate_id, case_id, wallet_id, model_name, model_version,
                    score, label, top_features, generated_at, is_model_output
                FROM model_estimates
                WHERE case_id = %s
                ORDER BY generated_at DESC;
                """,
                (case_id,),
            )
            rows = cur.fetchall()

    estimates = []
    for r in rows:
        estimates.append(
            {
                "estimate_id": r[0],
                "case_id": r[1],
                "wallet_id": r[2],
                "model_name": r[3],
                "model_version": r[4],
                "score": float(r[5]),
                "label": r[6],
                "top_features": r[7] if isinstance(r[7], list) else json.loads(r[7]),
                "generated_at": r[8].isoformat() if r[8] else None,
                "is_model_output": bool(r[9]),
            }
        )
    return estimates
