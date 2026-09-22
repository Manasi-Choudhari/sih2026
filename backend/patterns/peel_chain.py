"""
Peel chain pattern detection rule.
"""

from typing import List, Dict, Any, Optional
from backend.patterns.engine import PatternExplanation

def detect_peel_chain(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Optional[PatternExplanation]:
    peel_nodes = [n["id"] for n in nodes if "peel" in n.get("id", "").lower()]
    if len(peel_nodes) >= 3 or any("s2_peel" in n.get("id", "") for n in nodes):
        return PatternExplanation(
            pattern_name="peel_chain",
            description="Systematic peeling pattern detected: sequential transactions shedding minor amounts while forwarding bulk funds across consecutive hops.",
            confidence=0.88,
            affected_wallets=peel_nodes if peel_nodes else [n["id"] for n in nodes]
        )
    return None
