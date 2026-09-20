"""
VAJRA (SIH 26183) — Recommendation Approval & Report Metadata Store
Handles updating human approval gate state for recommendations and
persisting tamper-evident report metadata for T1's report generator.
"""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from db.evidence_ledger.hash_chain import canonical_json

load_dotenv()


def get_connection():
    import psycopg

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ConnectionError("PostgreSQL not configured (DATABASE_URL not set)")
    return psycopg.connect(database_url, connect_timeout=1)


def update_recommendation_approval(
    rec_id: str,
    approval_status: str,
    approved_by: str,
    rejection_reason: Optional[str] = None,
) -> bool:
    """
    Updates the approval gate state of a recommendation record.
    Allowed statuses: 'APPROVED', 'REJECTED', 'PENDING'
    """
    if approval_status not in ("APPROVED", "REJECTED", "PENDING"):
        raise ValueError(f"Invalid approval status: {approval_status}")

    now = datetime.now(timezone.utc)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE recommendations
                SET approval_status = %s,
                    approved_by = %s,
                    approved_at = %s,
                    rejection_reason = %s
                WHERE rec_id = %s;
                """,
                (approval_status, approved_by, now, rejection_reason, rec_id),
            )
            updated = cur.rowcount > 0
        conn.commit()
    return updated


def save_case_report(
    case_id: str,
    report_data: Dict[str, Any],
    version: str = "1.0.0",
    summary: Optional[str] = None,
    report_id: Optional[str] = None,
    report_format: str = "JSON",
) -> Dict[str, Any]:
    """
    Persists report metadata and computes a SHA-256 hash of canonical report data
    for integrity verification.
    """
    if report_id is None:
        report_id = f"rep_{uuid.uuid4().hex[:12]}"

    canonical_str = canonical_json(report_data)
    report_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO case_reports (
                    report_id, case_id, report_hash, version,
                    format, report_data, summary
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING report_id, generated_at;
                """,
                (
                    report_id,
                    case_id,
                    report_hash,
                    version,
                    report_format,
                    json.dumps(report_data),
                    summary,
                ),
            )
            row = cur.fetchone()
            gen_at = row[1].isoformat() if row and row[1] else None
        conn.commit()

    return {
        "report_id": report_id,
        "case_id": case_id,
        "report_hash": report_hash,
        "version": version,
        "format": report_format,
        "summary": summary,
        "generated_at": gen_at,
    }


def get_case_report_and_verify(report_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a report and verifies its content against its stored report_hash.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    report_id, case_id, report_hash, version,
                    format, report_data, summary, generated_at
                FROM case_reports
                WHERE report_id = %s;
                """,
                (report_id,),
            )
            row = cur.fetchone()

    if not row:
        return None

    report_data = row[5] if isinstance(row[5], dict) else json.loads(row[5])
    canonical_str = canonical_json(report_data)
    calculated_hash = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()
    is_valid = calculated_hash == row[2]

    return {
        "report_id": row[0],
        "case_id": row[1],
        "report_hash": row[2],
        "version": row[3],
        "format": row[4],
        "report_data": report_data,
        "summary": row[6],
        "generated_at": row[7].isoformat() if row[7] else None,
        "integrity_check": "PASS" if is_valid else "FAIL",
    }
