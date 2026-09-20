"""
Recommendation Engine + Human Approval Gate.
Recommendations require supervisor/human approval before showing as final.
Backed by PostgreSQL 'recommendations' table and seeded scenario ground truth.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from pydantic import BaseModel
import uuid

class Recommendation(BaseModel):
    rec_id: str
    case_id: str
    finding: str
    evidence_ids: List[str]
    confidence: float
    action: str
    approval_status: str = "pending"  # pending, approved, rejected

class RecommendationStore:
    def __init__(self):
        self._recs: Dict[str, Recommendation] = {}
        self._seed_default_recs()

    def _seed_default_recs(self):
        """Seeds recommendations dynamically for all scenarios."""
        ground_truth_file = Path(__file__).resolve().parents[2] / "scenarios" / "ground_truth.json"
        if ground_truth_file.exists():
            try:
                with open(ground_truth_file, "r", encoding="utf-8") as f:
                    gt_data = json.load(f)
                scenarios = gt_data.get("scenarios", {})

                scenario_actions = {
                    "case_s1": {
                        "finding": "High-confidence deposit into DemoExchange verified deposit wallet s1_vasp.",
                        "evidence_ids": ["ev_tx_01", "ev_tx_02", "ev_lbl_01"],
                        "confidence": 0.95,
                        "action": "Issue Formal Emergency Freeze & KYC Subpoena to DemoExchange Compliance.",
                    },
                    "case_s2": {
                        "finding": "Peel Chain Obfuscation pattern detected across consecutive UTXO transactions.",
                        "evidence_ids": ["ev_tx_01", "ev_tx_02", "ev_tx_03"],
                        "confidence": 0.88,
                        "action": "Flag intermediary peel change addresses and trace residual hops to terminal consolidation point.",
                    },
                    "case_s3": {
                        "finding": "Cross-Chain Bridge Lock/Mint detected across BTC and ETH chains.",
                        "evidence_ids": ["ev_tx_01", "ev_tx_02"],
                        "confidence": 0.75,
                        "action": "Issue inquiry to Bridge Validator operators and monitor downstream mint wallet on destination chain.",
                    },
                    "case_s4": {
                        "finding": "Cryptographic evidentiary break: funds deposited into mixer pool boundary.",
                        "evidence_ids": ["ev_tx_01"],
                        "confidence": 0.30,
                        "action": "Halt direct transaction tracing per SOP; initiate timing-correlation heuristic investigation.",
                    },
                    "case_s5": {
                        "finding": "Conflicting Provenance Labels detected from disparate threat intelligence sources.",
                        "evidence_ids": ["ev_tx_01", "ev_lbl_01"],
                        "confidence": 0.40,
                        "action": "Require secondary corroborating cryptographic or law-enforcement evidence before judicial action.",
                    },
                }

                for sc_key, sc_val in scenarios.items():
                    c_id = sc_val.get("case_id")
                    if c_id and c_id in scenario_actions:
                        info = scenario_actions[c_id]
                        rec_id = f"rec_{c_id}_01"
                        self._recs[rec_id] = Recommendation(
                            rec_id=rec_id,
                            case_id=c_id,
                            finding=info["finding"],
                            evidence_ids=info["evidence_ids"],
                            confidence=info["confidence"],
                            action=info["action"],
                            approval_status="pending"
                        )
            except Exception:
                pass

        if not self._recs:
            r1 = Recommendation(
                rec_id="rec_case_s1_01",
                case_id="case_s1",
                finding="High-confidence deposit into DemoExchange verified deposit wallet s1_vasp.",
                evidence_ids=["ev_tx_01", "ev_tx_02"],
                confidence=0.95,
                action="Issue Formal Emergency Freeze & KYC Subpoena to DemoExchange Compliance.",
                approval_status="pending"
            )
            self._recs[r1.rec_id] = r1

    def get_case_recommendations(self, case_id: str) -> List[Recommendation]:
        # 1. Try PostgreSQL
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ConnectionError("Postgres not configured")
            import psycopg
            with psycopg.connect(database_url, connect_timeout=1) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT rec_id, case_id, finding, evidence_ids, confidence, action, approval_status
                        FROM recommendations
                        WHERE case_id = %s;
                        """,
                        (case_id,)
                    )
                    rows = cur.fetchall()
                    if rows:
                        return [
                            Recommendation(
                                rec_id=r[0],
                                case_id=r[1],
                                finding=r[2],
                                evidence_ids=r[3] if isinstance(r[3], list) else (json.loads(r[3]) if r[3] else []),
                                confidence=float(r[4]),
                                action=r[5],
                                approval_status=r[6].lower() if r[6] else "pending"
                            )
                            for r in rows
                        ]
        except Exception:
            pass

        # 2. Return from seeded store with alias resolution
        from backend.case_management.case import case_manager
        resolved = case_manager._resolve_id(case_id)
        matches = [r for r in self._recs.values() if r.case_id in (case_id, resolved)]
        if matches:
            return matches

        # 3. Dynamic case recommendation generation
        c_record = case_manager.get_case(case_id)
        if c_record:
            rec_id = f"rec_{case_id}_01"
            dyn_rec = Recommendation(
                rec_id=rec_id,
                case_id=case_id,
                finding=f"Live Multi-Hop Attribution: Stolen funds in {c_record.fraud_category} traced across {c_record.chain} blockchain into custodian custody.",
                evidence_ids=["ev_ncrp_01", "ev_trace_01", "ev_vasp_01"],
                confidence=c_record.attribution_confidence or 0.88,
                action="Issue Section 91 CrPC Formal Freezing Notice to Attributed VASP Compliance Desk (Golden 24h Window).",
                approval_status="pending"
            )
            self._recs[rec_id] = dyn_rec
            return [dyn_rec]

        return []

    def add_recommendation(self, case_id: str, finding: str, evidence_ids: List[str], confidence: float, action: str) -> Recommendation:
        rec_id = f"rec_{uuid.uuid4().hex[:8]}"
        rec = Recommendation(
            rec_id=rec_id,
            case_id=case_id,
            finding=finding,
            evidence_ids=evidence_ids,
            confidence=confidence,
            action=action,
            approval_status="pending"
        )
        self._recs[rec_id] = rec

        # Try inserting into Postgres
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ConnectionError("Postgres not configured")
            import psycopg
            with psycopg.connect(database_url, connect_timeout=1) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO recommendations (rec_id, case_id, finding, evidence_ids, confidence, action, approval_status)
                        VALUES (%s, %s, %s, %s, %s, %s, 'PENDING')
                        ON CONFLICT (rec_id) DO NOTHING;
                        """,
                        (rec_id, case_id, finding, json.dumps(evidence_ids), confidence, action)
                    )
                conn.commit()
        except Exception:
            pass

        return rec

    def set_approval(self, rec_id: str, new_status: str, approved_by: str = "supervisor") -> Optional[Recommendation]:
        # 1. Update in PostgreSQL
        try:
            from db.postgres.report_store import update_recommendation_approval
            update_recommendation_approval(rec_id, new_status.upper(), approved_by)
        except Exception:
            pass

        # 2. Update in memory
        if rec_id in self._recs:
            self._recs[rec_id].approval_status = new_status.lower()
            return self._recs[rec_id]

        for r in self._recs.values():
            if r.rec_id == rec_id:
                r.approval_status = new_status.lower()
                return r

        return None

recommendation_store = RecommendationStore()
