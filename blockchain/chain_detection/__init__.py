"""
Chain detection package for VAJRA.
"""

from blockchain.chain_detection.detect import (
    SupportedChain,
    detect_chain,
    is_valid_btc_address,
    is_valid_eth_address,
)

__all__ = [
    "SupportedChain",
    "detect_chain",
    "is_valid_btc_address",
    "is_valid_eth_address",
]
