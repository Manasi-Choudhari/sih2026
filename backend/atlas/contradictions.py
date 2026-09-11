"""
ATLAS Contradictions identification.
"""

from typing import List
from backend.atlas.engine import AtlasContradiction

def generate_contradictions() -> List[AtlasContradiction]:
    return [
        AtlasContradiction(
            contradiction_id="CONT-1",
            claim="Deposit wallet strictly belongs to sole culprit",
            evidence_against="Address exhibits concurrent deposits originating from unrelated clusters within identical 1-hour block window."
        ),
        AtlasContradiction(
            contradiction_id="CONT-2",
            claim="Transaction value matches victim loss without fee deduction",
            evidence_against="0.04 ETH variance detected between reported loss and observed ingress to target VASP."
        )
    ]
