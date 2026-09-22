"""
Fan-out pattern detection rule.
"""

from typing import List, Dict, Any, Optional
from backend.patterns.engine import PatternExplanation

def detect_fanout(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Optional[PatternExplanation]:
    if len(edges) >= 4 and len(set(e["source"] for e in edges)) == 1:
        source_w = list(set(e["source"] for e in edges))[0]
        return PatternExplanation(
            pattern_name="fan_out",
            description=f"Fan-out dispersion observed: single source wallet {source_w} distributing funds across multiple distinct destinations.",
            confidence=0.80,
            affected_wallets=[source_w] + [e["target"] for e in edges]
        )
    return None
