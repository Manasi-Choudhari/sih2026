"""
Cross-chain package for VAJRA.
"""

from blockchain.cross_chain.correlator import (
    BridgeCorrelator,
    KNOWN_BRIDGES,
)

__all__ = [
    "BridgeCorrelator",
    "KNOWN_BRIDGES",
]
