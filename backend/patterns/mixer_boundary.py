"""
Mixer boundary pattern detection rule.
"""

from typing import List, Dict, Any, Optional
from backend.patterns.engine import PatternExplanation

def detect_mixer_boundary(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Optional[PatternExplanation]:
    mixer_nodes = [n["id"] for n in nodes if n.get("entity_type") == "mixer" or "mixer" in n.get("id", "").lower()]
    if mixer_nodes:
        return PatternExplanation(
            pattern_name="mixer_boundary",
            description="Transaction flow enters an obfuscation service (privacy pool/mixer). Evidentiary continuity terminates at this boundary.",
            confidence=0.95,
            affected_wallets=mixer_nodes
        )
    return None
