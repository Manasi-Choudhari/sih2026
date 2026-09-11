"""
Case Queue and Status helper routines.
"""

from typing import List, Optional
from backend.case_management.case import case_manager, CaseRecord

def get_investigation_queue(status: Optional[str] = None) -> List[CaseRecord]:
    return case_manager.list_cases(status=status)

def update_case_status(case_id: str, new_status: str) -> Optional[CaseRecord]:
    return case_manager.update_status(case_id, new_status)
