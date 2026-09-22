"""
Transaction normalization schema for VAJRA.
Defines the shared NormalizedTransaction and related data structures
matching Neo4j (:Wallet)-[:TRANSACTION]->(:Wallet) and [:CROSS_CHAIN_LINK] shapes.
"""

from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

ChainType = Literal["BTC", "ETH"]
DirectionType = Literal["in", "out"]


class NormalizedTransaction(BaseModel):
    """
    Standardized cross-chain transaction representation matching the Neo4j schema:
    (:Wallet)-[:TRANSACTION {
        tx_hash, chain, block_height, timestamp, amount, asset,
        direction, is_bridge_leg, confidence_of_link
    }]->(:Wallet)
    """
    tx_hash: str = Field(..., description="Unique transaction identifier/hash")
    chain: ChainType = Field(..., description="Blockchain (BTC or ETH)")
    from_address: str = Field(..., description="Sender wallet address")
    to_address: str = Field(..., description="Recipient wallet address")
    block_height: int = Field(..., ge=0, description="Block number/height")
    timestamp: str = Field(..., description="ISO 8601 formatted timestamp (UTC)")
    amount: float = Field(..., ge=0.0, description="Transaction amount in native units (e.g. BTC or ETH)")
    asset: str = Field(..., description="Asset symbol, e.g., 'BTC', 'ETH', 'WBTC', 'USDT'")
    direction: DirectionType = Field("out", description="Direction relative to source node")
    is_bridge_leg: bool = Field(False, description="True if this transaction represents a bridge deposit or release")
    confidence_of_link: float = Field(1.0, ge=0.0, le=1.0, description="Confidence of link (1.0 for on-chain direct)")

    def to_neo4j_edge_properties(self) -> dict:
        """Returns attributes dictionary formatted for Neo4j relationship creation."""
        return {
            "tx_hash": self.tx_hash,
            "chain": self.chain,
            "block_height": self.block_height,
            "timestamp": self.timestamp,
            "amount": self.amount,
            "asset": self.asset,
            "direction": self.direction,
            "is_bridge_leg": self.is_bridge_leg,
            "confidence_of_link": self.confidence_of_link,
        }


class CrossChainLink(BaseModel):
    """
    Cross-chain link representation matching Neo4j schema:
    (:Wallet)-[:CROSS_CHAIN_LINK {
        source_chain_tx, dest_chain_tx, bridge_contract,
        correlation_method, correlation_confidence
    }]->(:Wallet)
    """
    source_wallet: str = Field(..., description="Source wallet address")
    dest_wallet: str = Field(..., description="Destination wallet address")
    source_chain_tx: str = Field(..., description="Originating transaction hash on source chain")
    dest_chain_tx: str = Field(..., description="Mint/release transaction hash on destination chain")
    bridge_contract: str = Field(..., description="Bridge contract or identifier")
    correlation_method: str = Field("lock_mint_pairing", description="Correlation method")
    correlation_confidence: float = Field(
        ...,
        ge=0.0,
        le=0.95,
        description="Cross-chain link confidence (strictly < 1.0, always lower than same-chain)"
    )

    def to_neo4j_relationship_properties(self) -> dict:
        """Returns attributes dictionary formatted for Neo4j CROSS_CHAIN_LINK relationship."""
        return {
            "source_chain_tx": self.source_chain_tx,
            "dest_chain_tx": self.dest_chain_tx,
            "bridge_contract": self.bridge_contract,
            "correlation_method": self.correlation_method,
            "correlation_confidence": self.correlation_confidence,
        }
