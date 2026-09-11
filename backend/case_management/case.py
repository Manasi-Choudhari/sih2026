"""
Case Management module for VAJRA:
Creation, in-memory/stub and database backed queue and status management.
"""

from __future__ import annotations
from datetime import datetime, timezone
import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class CreateCaseInput(BaseModel):
    complaint_id: Optional[str] = None
    victim_address: str
    chain: str = "ETH"
    reported_amount: Optional[float] = 0.0
    currency: Optional[str] = "ETH"
    fraud_category: Optional[str] = "Theft"
    victim_ref: Optional[str] = None

class CaseRecord(BaseModel):
    case_id: str
    complaint_id: Optional[str] = None
    status: str = "open"  # open, tracing, attributed, closed
    assigned_investigator: Optional[str] = "investigator_1"
    created_at: str
    victim_address: str
    chain: str
    reported_amount: Optional[float] = 0.0
    currency: Optional[str] = "ETH"
    fraud_category: Optional[str] = "Theft"
    rule_risk_score: float = 0.0
    attribution_confidence: float = 0.0
    ml_probability: float = 0.0
    ml: Optional[Dict[str, Any]] = None

class CaseManager:
    """Manages cases in-memory / persistent bridge."""
    def __init__(self):
        self._cases: Dict[str, CaseRecord] = {}
        self._seed_default_cases()

    def _seed_default_cases(self):
        now = datetime.now(timezone.utc).isoformat()
        # Seed default synthetic test cases
        defaults = [
            CaseRecord(
                case_id="case_s1",
                complaint_id="NCRP-2026-001",
                status="attributed",
                assigned_investigator="Lead Investigator",
                created_at=now,
                victim_address="s1_victim",
                chain="ETH",
                rule_risk_score=0.88,
                attribution_confidence=0.95,
                ml_probability=0.82,
                ml={
                    "output_label": "model_output",
                    "is_model_output": True,
                    "model_name": "risk_scoring_xgb_gpu",
                    "model_version": "risk_xgb_gpu-latest",
                    "device": "cpu",
                    "top_features": [{"feature": "hops_to_nearest_vasp", "importance": 0.42}],
                    "disclaimer": "Statistical prioritization signal only. Does not decide VASP attribution or prove facts."
                }
            ),
            CaseRecord(
                case_id="case_s2",
                complaint_id="NCRP-2026-002",
                status="tracing",
                assigned_investigator="Lead Investigator",
                created_at=now,
                victim_address="s2_peel_0",
                chain="BTC",
                rule_risk_score=0.79,
                attribution_confidence=0.70,
                ml_probability=0.75,
                ml={
                    "output_label": "model_output",
                    "is_model_output": True,
                    "model_name": "risk_scoring_xgb_gpu",
                    "model_version": "risk_xgb_gpu-latest",
                    "device": "cpu",
                    "top_features": [{"feature": "peel_chain_score", "importance": 0.58}],
                    "disclaimer": "Statistical prioritization signal only. Does not decide VASP attribution or prove facts."
                }
            ),
            CaseRecord(
                case_id="case_s3",
                complaint_id="NCRP-2026-003",
                status="tracing",
                assigned_investigator="Lead Investigator",
                created_at=now,
                victim_address="s3_btc_lock",
                chain="BTC",
                rule_risk_score=0.65,
                attribution_confidence=0.55,
                ml_probability=0.62,
                ml={
                    "output_label": "model_output",
                    "is_model_output": True,
                    "model_name": "risk_scoring_xgb_gpu",
                    "model_version": "risk_xgb_gpu-latest",
                    "device": "cpu",
                    "top_features": [{"feature": "touches_bridge", "importance": 0.49}],
                    "disclaimer": "Statistical prioritization signal only. Does not decide VASP attribution or prove facts."
                }
            ),
            CaseRecord(
                case_id="case_s4",
                complaint_id="NCRP-2026-004",
                status="attributed",
                assigned_investigator="Lead Investigator",
                created_at=now,
                victim_address="s4_pre_mixer",
                chain="BTC",
                rule_risk_score=0.92,
                attribution_confidence=0.40,
                ml_probability=0.91,
                ml={
                    "output_label": "model_output",
                    "is_model_output": True,
                    "model_name": "risk_scoring_xgb_gpu",
                    "model_version": "risk_xgb_gpu-latest",
                    "device": "cpu",
                    "top_features": [{"feature": "touches_known_mixer", "importance": 0.65}],
                    "disclaimer": "Statistical prioritization signal only. Does not decide VASP attribution or prove facts."
                }
            ),
            CaseRecord(
                case_id="case_s5",
                complaint_id="NCRP-2026-005",
                status="attributed",
                assigned_investigator="Lead Investigator",
                created_at=now,
                victim_address="s5_conflict",
                chain="ETH",
                rule_risk_score=0.45,
                attribution_confidence=0.35,
                ml_probability=0.74,
                ml={
                    "output_label": "model_output",
                    "is_model_output": True,
                    "model_name": "risk_scoring_xgb_gpu",
                    "model_version": "risk_xgb_gpu-latest",
                    "device": "cpu",
                    "top_features": [{"feature": "conflicting_labels", "importance": 0.70}],
                    "disclaimer": "Statistical prioritization signal only. Does not decide VASP attribution or prove facts."
                }
            )
        ]
        for c in defaults:
            self._cases[c.case_id] = c

    def create_case(self, data: CreateCaseInput) -> CaseRecord:
        case_id = f"case_{uuid.uuid4().hex[:8]}"
        complaint_id = data.complaint_id or f"COMP-{uuid.uuid4().hex[:6].upper()}"
        record = CaseRecord(
            case_id=case_id,
            complaint_id=complaint_id,
            status="open",
            assigned_investigator="Lead Investigator",
            created_at=datetime.now(timezone.utc).isoformat(),
            victim_address=data.victim_address,
            chain=data.chain.upper(),
            reported_amount=data.reported_amount or 0.0,
            currency=data.currency or "ETH",
            fraud_category=data.fraud_category or "Theft",
            rule_risk_score=0.5,
            attribution_confidence=0.0,
            ml_probability=0.5,
            ml={
                "output_label": "model_output",
                "is_model_output": True,
                "model_name": "risk_scoring_xgb_gpu",
                "model_version": "risk_xgb_gpu-latest",
                "device": "cpu",
                "top_features": [{"feature": "tx_count", "importance": 0.1}],
                "disclaimer": "Statistical prioritization signal only. Does not decide VASP attribution or prove facts."
            }
        )
        self._cases[case_id] = record
        return record

    def list_cases(self, status: Optional[str] = None) -> List[CaseRecord]:
        if status:
            return [c for c in self._cases.values() if c.status.lower() == status.lower()]
        return list(self._cases.values())

    def get_case(self, case_id: str) -> Optional[CaseRecord]:
        return self._cases.get(case_id)

    def update_status(self, case_id: str, status: str) -> Optional[CaseRecord]:
        if case_id in self._cases:
            self._cases[case_id].status = status
            return self._cases[case_id]
        return None

case_manager = CaseManager()
