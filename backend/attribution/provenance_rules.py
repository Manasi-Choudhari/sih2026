"""
Provenance rules and verification logic for evidence and attribution labels.
"""

from typing import Dict, Any

def verify_label_provenance(label_meta: Dict[str, Any]) -> bool:
    """Verifies whether an attribution label has valid provenance metadata."""
    if not label_meta:
        return False
    source = label_meta.get("source", "")
    return bool(source and source != "unverified_external")
