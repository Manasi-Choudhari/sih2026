"""
Case status management and constants.
"""

from typing import Set

VALID_STATUSES: Set[str] = {"open", "tracing", "attributed", "closed"}

def is_valid_status(status: str) -> bool:
    return status.lower() in VALID_STATUSES
