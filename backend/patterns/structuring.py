"""
Structuring pattern detection rule.
"""

from typing import List, Dict, Any, Optional
from backend.patterns.engine import PatternExplanation

def detect_structuring(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Optional[PatternExplanation]:
    structuring_candidates = [
        e for e in edges
        if 9000 <= float(e.get("value", 0)) < 10000 or (0.9 <= float(e.get("value", 0)) <= 0.99 and e.get("currency") == "ETH")
    ]
    if len(structuring_candidates) >= 2:
        return PatternExplanation(
            pattern_name="structuring",
            description="Transaction amounts clustered deliberately just below standard statutory reporting thresholds.",
            confidence=0.75,
            affected_wallets=list({e["source"] for e in structuring_candidates} | {e["target"] for e in structuring_candidates})
        )
    return None
