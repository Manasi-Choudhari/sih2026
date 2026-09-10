"""
Blockchain package for VAJRA (SIH 26183).
Owned by T2 (Blockchain Engineer).
"""

from blockchain.chain_detection.detect import detect_chain, is_valid_btc_address, is_valid_eth_address
from blockchain.normalization.normalize import NormalizedTransaction, CrossChainLink
from blockchain.adapters.btc.client import BlockchairBtcAdapter
from blockchain.adapters.eth.client import EtherscanAdapter
from blockchain.cross_chain.correlator import BridgeCorrelator
from blockchain.indexer.worker import GraphIndexer

__all__ = [
    "detect_chain",
    "is_valid_btc_address",
    "is_valid_eth_address",
    "NormalizedTransaction",
    "CrossChainLink",
    "BlockchairBtcAdapter",
    "EtherscanAdapter",
    "BridgeCorrelator",
    "GraphIndexer",
]
