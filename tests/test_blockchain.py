"""
Unit and Contract tests for T2 (Blockchain Engineer).
Validates:
1. Chain detection (BTC vs ETH)
2. NormalizedTransaction schema
3. Cross-chain correlator rules (confidence <= 0.85, always lower than same-chain)
4. Adapter mock parsing
"""

import pytest
from blockchain.chain_detection.detect import (
    detect_chain,
    is_valid_btc_address,
    is_valid_eth_address,
)
from blockchain.normalization.normalize import (
    NormalizedTransaction,
    CrossChainLink,
)
from blockchain.cross_chain.correlator import (
    BridgeCorrelator,
)
from blockchain.adapters.eth.client import EtherscanAdapter
from blockchain.adapters.btc.client import BlockchairBtcAdapter


def test_chain_detection():
    # Valid ETH addresses
    eth_addr = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    assert is_valid_eth_address(eth_addr) is True
    assert detect_chain(eth_addr) == "ETH"

    # Valid BTC addresses (P2PKH, P2SH, Bech32)
    btc_p2pkh = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
    btc_p2sh = "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"
    btc_bech32 = "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"

    assert is_valid_btc_address(btc_p2pkh) is True
    assert detect_chain(btc_p2pkh) == "BTC"

    assert is_valid_btc_address(btc_p2sh) is True
    assert detect_chain(btc_p2sh) == "BTC"

    assert is_valid_btc_address(btc_bech32) is True
    assert detect_chain(btc_bech32) == "BTC"

    # Invalid / Unsupported chains (e.g. Tron or garbage)
    with pytest.raises(ValueError):
        detect_chain("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")  # Tron rejected per scope lock

    with pytest.raises(ValueError):
        detect_chain("invalid_random_string")


def test_normalized_transaction_schema():
    tx = NormalizedTransaction(
        tx_hash="0xabc123",
        chain="ETH",
        from_address="0x1111111111111111111111111111111111111111",
        to_address="0x2222222222222222222222222222222222222222",
        block_height=123456,
        timestamp="2026-09-10T12:00:00Z",
        amount=1.5,
        asset="ETH",
        direction="out",
        is_bridge_leg=False,
        confidence_of_link=1.0,
    )

    neo4j_props = tx.to_neo4j_edge_properties()
    assert neo4j_props["tx_hash"] == "0xabc123"
    assert neo4j_props["amount"] == 1.5
    assert neo4j_props["confidence_of_link"] == 1.0


def test_cross_chain_correlator_rule():
    """Rule check: Cross-chain confidence must always be lower than same-chain (<= 0.85)."""
    correlator = BridgeCorrelator()

    source_lock_tx = NormalizedTransaction(
        tx_hash="btc_lock_tx_001",
        chain="BTC",
        from_address="s3_btc_lock",
        to_address="s3_bridge_custody",  # known bridge
        block_height=800000,
        timestamp="2026-09-10T12:00:00+00:00",
        amount=1.0,
        asset="BTC",
        direction="out",
        is_bridge_leg=True,
        confidence_of_link=1.0,
    )

    candidate_dest_tx = NormalizedTransaction(
        tx_hash="eth_mint_tx_001",
        chain="ETH",
        from_address="0x0000000000000000000000000000000000000000",
        to_address="s3_eth_mint",
        block_height=19000000,
        timestamp="2026-09-10T12:15:00+00:00",  # 15 minutes later
        amount=0.995,  # 0.5% fee
        asset="WBTC",
        direction="in",
        is_bridge_leg=True,
        confidence_of_link=1.0,
    )

    link = correlator.correlate(source_lock_tx, [candidate_dest_tx])
    assert link is not None
    assert isinstance(link, CrossChainLink)
    assert link.source_wallet == "s3_btc_lock"
    assert link.dest_wallet == "s3_eth_mint"
    # Non-negotiable constraint: confidence < 1.0, max 0.85
    assert link.correlation_confidence <= 0.85
    assert link.correlation_confidence > 0.0


def test_adapter_mock_injection():
    eth_adapter = EtherscanAdapter()
    dummy_tx = NormalizedTransaction(
        tx_hash="0xdeadbeef",
        chain="ETH",
        from_address="0xvictim",
        to_address="0xhop1",
        block_height=100,
        timestamp="2026-09-10T00:00:00Z",
        amount=5.0,
        asset="ETH",
        direction="out",
        is_bridge_leg=False,
        confidence_of_link=1.0,
    )
    eth_adapter.inject_mock_transactions("0xvictim", [dummy_tx])
    results = eth_adapter.get_address_transactions("0xvictim")
    assert len(results) == 1
    assert results[0].tx_hash == "0xdeadbeef"
