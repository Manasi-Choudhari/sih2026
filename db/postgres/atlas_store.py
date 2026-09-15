"""
VAJRA (SIH 26183) — ATLAS Results Persistence Store
Handles storing and retrieving ATLAS results (competing hypotheses,
contradictions, missing evidence, robustness score) for cases.
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    import psycopg

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://vajra_user:vajra_password@localhost:5432/vajra_db",
    )
    return psycopg.connect(database_url)


def save_atlas_result(
    case_id: str,
    robustness_score: float,
    alternatives: Optional[List[Dict[str, Any]]] = None,
    contradictions: Optional[List[Dict[str, Any]]] = None,
    missing_evidence: Optional[List[str]] = None,
    challenger_hypothesis: Optional[str] = None,
    atlas_id: Optional[str] = None,
) -> str:
    """Saves an ATLAS evaluation result tied to a case."""
    if atlas_id is None:
        atlas_id = f"atlas_{uuid.uuid4().hex[:12]}"
    if alternatives is None:
        alternatives = []
    if contradictions is None:
        contradictions = []
    if missing_evidence is None:
        missing_evidence = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO atlas_results (
                    atlas_id, case_id, alternatives, contradictions,
                    missing_evidence, robustness_score, challenger_hypothesis
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING atlas_id;
                """,
                (
                    atlas_id,
                    case_id,
                    json.dumps(alternatives),
                    json.dumps(contradictions),
                    json.dumps(missing_evidence),
                    robustness_score,
                    challenger_hypothesis,
                ),
            )
            created_id = cur.fetchone()[0]
        conn.commit()
    return created_id


def get_atlas_result_by_case(case_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves the latest ATLAS result for a case."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    atlas_id,
                    case_id,
                    alternatives,
                    contradictions,
                    missing_evidence,
                    robustness_score,
                    challenger_hypothesis,
                    evaluated_at
                FROM atlas_results
                WHERE case_id = %s
                ORDER BY evaluated_at DESC
                LIMIT 1;
                """,
                (case_id,),
            )
            row = cur.fetchone()

    if not row:
        return None

    return {
        "atlas_id": row[0],
        "case_id": row[1],
        "alternatives": row[2] if isinstance(row[2], list) else json.loads(row[2]),
        "contradictions": row[3] if isinstance(row[3], list) else json.loads(row[3]),
        "missing_evidence": row[4] if isinstance(row[4], list) else json.loads(row[4]),
        "robustness_score": float(row[5]),
        "challenger_hypothesis": row[6],
        "evaluated_at": row[7].isoformat() if row[7] else None,
    }
