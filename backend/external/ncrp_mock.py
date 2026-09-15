"""
Simulated NCRP / SAHYOG external integration adapter (BUILD.md):
- Mock adapter only
- Visibly labeled 'Simulated' everywhere it appears in UI/reports.
"""

from datetime import datetime, timezone
from typing import Dict, Any
from pydantic import BaseModel

class ExternalCaseUpdate(BaseModel):
    case_id: str
    external_ref: str
    status_update: str
    source: str = "NCRP_MOCK"
    payload: Dict[str, Any]

class ExternalCaseUpdateAck(BaseModel):
    status: str
    case_id: str
    acknowledged_at: str
    simulation_mode: bool = True
    notice: str = "Simulated NCRP/SAHYOG adapter — no live police portal transmission occurred."

def process_mock_callback(data: ExternalCaseUpdate) -> ExternalCaseUpdateAck:
    return ExternalCaseUpdateAck(
        status="PROCESSED_SIMULATED",
        case_id=data.case_id,
        acknowledged_at=datetime.now(timezone.utc).isoformat(),
        simulation_mode=True
    )
