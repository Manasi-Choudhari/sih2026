"""
Recommendation Engine + Human Approval Gate.
Recommendations require supervisor/human approval before showing as final.
"""

from typing import List, Dict, Optional
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
        r1 = Recommendation(
            rec_id="rec_s1_01",
            case_id="case_s1",
            finding="High-confidence deposit into DemoExchange verified deposit wallet s1_vasp.",
            evidence_ids=["ev_s1_tx1", "ev_s1_tx2", "ev_s1_label"],
            confidence=0.95,
            action="Issue Formal Emergency Freeze & KYC Subpoena to DemoExchange Compliance.",
            approval_status="pending"
        )
        self._recs[r1.rec_id] = r1

    def get_case_recommendations(self, case_id: str) -> List[Recommendation]:
        return [r for r in self._recs.values() if r.case_id == case_id]

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
        return rec

    def set_approval(self, rec_id: str, new_status: str) -> Optional[Recommendation]:
        if rec_id in self._recs:
            self._recs[rec_id].approval_status = new_status
            return self._recs[rec_id]
        return None

recommendation_store = RecommendationStore()
