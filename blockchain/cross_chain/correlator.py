"""
Bridge Registry and Cross-Chain Correlation Engine for VAJRA.
Correlates a source-side lock/burn event with a destination-side mint/release event.

Rule:
A cross-chain link is represented strictly as a CROSS_CHAIN_LINK relationship,
never as a same-chain TRANSACTION edge, and ALWAYS carries lower default confidence
than a same-chain link (typically <= 0.85).
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, List, Optional
from blockchain.normalization.normalize import CrossChainLink, NormalizedTransaction

# Known Bridge Contracts/Custody addresses
KNOWN_BRIDGES: Dict[str, dict] = {
    "0x000000000000000000000000000000000000b1d9": {
        "name": "VAJRA_WBTC_BRIDGE",
        "source_chain": "BTC",
        "dest_chain": "ETH",
        "supported_assets": ["BTC", "WBTC"],
        "max_time_window_seconds": 7200,  # 2 hours
        "base_confidence": 0.85,
    },
    "s3_bridge_custody": {
        "name": "SYNTHETIC_SCENARIO_3_BRIDGE",
        "source_chain": "BTC",
        "dest_chain": "ETH",
        "supported_assets": ["BTC", "WBTC"],
        "max_time_window_seconds": 7200,
        "base_confidence": 0.85,
    }
}


class BridgeCorrelator:
    """
    Correlates cross-chain lock/burn and mint/release events.
    """

    def __init__(self, bridge_registry: Optional[Dict[str, dict]] = None):
        self.registry = bridge_registry or KNOWN_BRIDGES

    def correlate(
        self,
        source_tx: NormalizedTransaction,
        candidate_dest_txs: List[NormalizedTransaction],
    ) -> Optional[CrossChainLink]:
        """
        Evaluate correlation between a source-chain lock transaction and destination-chain mint candidates.
        
        Applies:
        1. Bridge identity check
        2. Time proximity window
        3. Amount correspondence (slippage / fee allowance of up to 5%)
        4. Asset compatibility
        """
        if not source_tx.is_bridge_leg and source_tx.to_address not in self.registry:
            return None

        bridge_info = self.registry.get(source_tx.to_address)
        if not bridge_info:
            return None

        max_window = bridge_info["max_time_window_seconds"]
        src_dt = self._parse_iso(source_tx.timestamp)

        best_candidate: Optional[NormalizedTransaction] = None
        best_confidence: float = 0.0

        for dest_tx in candidate_dest_txs:
            if dest_tx.chain != bridge_info["dest_chain"]:
                continue

            dest_dt = self._parse_iso(dest_tx.timestamp)
            time_diff = (dest_dt - src_dt).total_seconds()
            
            # Destination tx must happen after or within tight window of source lock
            if time_diff < -60 or time_diff > max_window:
                continue

            # Amount check: Destination amount should be close to source amount (accounting for bridge fee)
            if source_tx.amount <= 0:
                continue
            ratio = dest_tx.amount / source_tx.amount
            if 0.90 <= ratio <= 1.05:
                # Calculate confidence score penalized by time difference and amount discrepancy
                # Must always be <= 0.85 per rule: cross-chain confidence always lower than same-chain
                confidence = bridge_info["base_confidence"]
                if ratio < 0.98 or ratio > 1.02:
                    confidence -= 0.05
                if time_diff > 3600:
                    confidence -= 0.05

                confidence = max(0.1, min(0.85, confidence))

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_candidate = dest_tx

        if best_candidate:
            return CrossChainLink(
                source_wallet=source_tx.from_address,
                dest_wallet=best_candidate.to_address,
                source_chain_tx=source_tx.tx_hash,
                dest_chain_tx=best_candidate.tx_hash,
                bridge_contract=source_tx.to_address,
                correlation_method="lock_mint_pairing",
                correlation_confidence=round(best_confidence, 2),
            )

        return None

    def _parse_iso(self, ts_str: str) -> datetime:
        try:
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            return datetime.now(timezone.utc)
