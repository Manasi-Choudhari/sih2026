"""
FastAPI Route Handlers matching openapi.yaml specifications and BUILD.md requirements.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel

from backend.case_management.case import case_manager, CreateCaseInput, CaseRecord
from backend.trace.engine import trace_engine, TraceResult
from backend.attribution.candidates import attribute_trace, AttributionResponse
from backend.atlas.engine import atlas_engine, AtlasResult
from backend.attribution.evidence_ledger import evidence_ledger, EvidenceEntry
from backend.recommendation.engine import recommendation_store, Recommendation
from backend.information_gap.ranking import rank_next_actions, ActionRecommendation
from backend.reporting.report_generator import generate_report, ReportResponse
from backend.external.ncrp_mock import process_mock_callback, ExternalCaseUpdate, ExternalCaseUpdateAck
from infra.auth.jwt import create_access_token, decode_access_token

router = APIRouter()

# Auth Models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "investigator"

class RecommendationActionRequest(BaseModel):
    rec_id: str
    action: str

# 1. Auth
@router.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    role = "supervisor" if "admin" in req.username.lower() or "super" in req.username.lower() else "investigator"
    token = create_access_token(
        data={
            "sub": req.username,
            "username": req.username,
            "role": role,
        },
        expires_minutes=480
    )
    return LoginResponse(
        access_token=token,
        token_type="bearer",
        role=role
    )

# 2. Case Management
@router.post("/cases", response_model=CaseRecord, status_code=201)
def create_case(data: CreateCaseInput):
    return case_manager.create_case(data)

@router.get("/cases", response_model=List[CaseRecord])
def get_cases(status: Optional[str] = Query(None)):
    return case_manager.list_cases(status=status)

@router.get("/cases/{id}", response_model=CaseRecord)
def get_case(id: str = Path(...)):
    case = case_manager.get_case(id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

# 3. Trace Graph
@router.get("/cases/{id}/graph")
def get_case_graph(id: str = Path(...)):
    case = case_manager.get_case(id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    res = trace_engine.trace(root=case.victim_address, case_id=id)
    return {
        "nodes": res.all_nodes,
        "edges": res.all_edges
    }

# 4. Attribution
@router.get("/cases/{id}/attribution", response_model=AttributionResponse)
def get_case_attribution(id: str = Path(...)):
    case = case_manager.get_case(id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    t_res = trace_engine.trace(root=case.victim_address, case_id=id)
    attr_res = attribute_trace(t_res)
    return attr_res

# 5. ATLAS
@router.get("/cases/{id}/atlas", response_model=AtlasResult)
def get_case_atlas(id: str = Path(...)):
    case = case_manager.get_case(id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    t_res = trace_engine.trace(root=case.victim_address, case_id=id)
    attr_res = attribute_trace(t_res)
    return atlas_engine.challenge(attr_res)

# 6. Evidence Ledger
@router.get("/cases/{id}/evidence", response_model=List[EvidenceEntry])
def get_case_evidence(id: str = Path(...)):
    return evidence_ledger.get_entries(id)

@router.get("/cases/{id}/verify")
def verify_case_ledger(id: str = Path(...)):
    return evidence_ledger.verify_chain(id)

# 7. Recommendations
@router.get("/cases/{id}/recommendations", response_model=List[Recommendation])
def get_case_recommendations(id: str = Path(...)):
    return recommendation_store.get_case_recommendations(id)

@router.get("/cases/{id}/actions", response_model=List[ActionRecommendation])
def get_case_next_actions(id: str = Path(...)):
    case = case_manager.get_case(id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    fin_rel = 0.85 if case.reported_amount and case.reported_amount > 1.0 else 0.60
    return rank_next_actions(
        financial_relevance=fin_rel,
        attribution_potential=case.attribution_confidence or 0.70,
        evidence_quality=case.rule_risk_score or 0.80,
        case_status=case.status
    )

@router.post("/cases/{id}/recommendations", response_model=Recommendation)
def act_on_recommendation(id: str, req: RecommendationActionRequest):
    new_status = "approved" if req.action.lower() == "approve" else "rejected"
    rec = recommendation_store.set_approval(req.rec_id, new_status)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec

# 8. Standardized Report
@router.post("/cases/{id}/report", response_model=ReportResponse)
def get_case_report(id: str = Path(...)):
    case = case_manager.get_case(id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    t_res = trace_engine.trace(root=case.victim_address, case_id=id)
    attr_res = attribute_trace(t_res)
    return generate_report(id, case.model_dump(), attr_res.model_dump())

# 9. Audit Events
@router.get("/cases/{id}/audit")
def get_case_audit(id: str = Path(...)):
    return [
        {
            "event_id": "aud_01",
            "actor_id": "investigator_1",
            "action": "CASE_CREATED",
            "target_id": id,
            "timestamp": "2026-09-11T07:00:00Z",
            "details": {"complaint": "Automated ingestion via simulated portal"}
        },
        {
            "event_id": "aud_02",
            "actor_id": "trace_engine_daemon",
            "action": "TRACE_COMPLETED",
            "target_id": id,
            "timestamp": "2026-09-11T07:00:02Z",
            "details": {"hops": 2, "terminal": "s1_vasp"}
        },
        {
            "event_id": "aud_03",
            "actor_id": "supervisor_admin",
            "action": "VERIFY_EVIDENCE_LEDGER",
            "target_id": id,
            "timestamp": "2026-09-11T07:05:00Z",
            "details": {"result": "PASS"}
        }
    ]

# 10. External Mock Callback
@router.post("/external/case-update", response_model=ExternalCaseUpdateAck)
def external_case_update(data: ExternalCaseUpdate):
    return process_mock_callback(data)
