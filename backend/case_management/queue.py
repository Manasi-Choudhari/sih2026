"""
Case queue retrieval and priority sorting helpers.
"""

from typing import List, Optional
from backend.case_management.case import case_manager, CaseRecord

def get_case_queue(status: Optional[str] = None) -> List[CaseRecord]:
    """Retrieve filtered case queue."""
    return case_manager.list_cases(status=status)
