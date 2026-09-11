"""
Approval gate logic for investigator recommendations.
"""

from typing import Optional
from backend.recommendation.engine import recommendation_store, Recommendation

def set_recommendation_approval(rec_id: str, new_status: str) -> Optional[Recommendation]:
    """Approve or reject a recommendation through the human approval gate."""
    return recommendation_store.set_approval(rec_id, new_status)
