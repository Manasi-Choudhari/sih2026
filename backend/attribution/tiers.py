"""
VASP Attribution Evidence Tier rules (BUILD.md):
- Strong: Direct 0–1 hop to independently confirmed active VASP address, recent/reliable source, no obfuscation.
- Medium: Single crowdsourced label OR clean multi-hop path to a strong label with good timing/amount correlation.
- Weak: Stale/low-reputation label, conflicting labels, weak clustering, or indirect path.
- Unknown: No reliable label at terminal point — must be shown explicitly, never hidden.
"""

from typing import Literal

EvidenceTier = Literal["Strong", "Medium", "Weak", "Unknown"]

def determine_evidence_tier(
    hops: int,
    source_type: str,  # "official", "crowdsource", "inferred", "unknown"
    has_conflicting_labels: bool,
    has_obfuscation: bool,
    is_stale: bool = False
) -> EvidenceTier:
    if source_type == "unknown" or not source_type:
        return "Unknown"
        
    if has_conflicting_labels or is_stale or (source_type == "crowdsource" and hops > 2):
        return "Weak"

    if source_type == "official" and hops <= 2 and not has_obfuscation:
        return "Strong"

    if source_type in ["official", "crowdsource"] and not has_conflicting_labels:
        return "Medium"

    return "Weak"
