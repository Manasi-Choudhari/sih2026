"""
Indexer and Neo4j graph writer for VAJRA.
Ingests NormalizedTransaction and CrossChainLink instances into Neo4j graph
strictly matching the Neo4j schema defined in BUILD.md:

(:Wallet {address, chain, first_seen, last_seen, cluster_id, entity_type})
(:VASP {name, known_addresses, last_verified})
(:Label {source, label_text, confidence, first_seen, last_verified})

(:Wallet)-[:TRANSACTION {
    tx_hash, chain, block_height, timestamp, amount, asset,
    direction, is_bridge_leg, confidence_of_link
}]->(:Wallet)

(:Wallet)-[:CROSS_CHAIN_LINK {
    source_chain_tx, dest_chain_tx, bridge_contract,
    correlation_method, correlation_confidence
}]->(:Wallet)
"""

from __future__ import annotations
import os
from typing import List, Optional
from neo4j import GraphDatabase, Driver
from blockchain.normalization.normalize import NormalizedTransaction, CrossChainLink


class GraphIndexer:
    """Writes normalized blockchain transactions and wallets into Neo4j."""

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "")
        self.database = database or os.getenv("NEO4J_DATABASE", "sih2026")
        self._driver: Optional[Driver] = None

    def connect(self) -> Driver:
        if self._driver is None:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        return self._driver

    def close(self):
        if self._driver is not None:
            self._driver.close()
            self._driver = None

    def write_transaction(self, tx: NormalizedTransaction) -> None:
        """Write a single NormalizedTransaction edge and its source/dest Wallet nodes into Neo4j."""
        driver = self.connect()
        cypher = """
        MERGE (from_w:Wallet {address: $from_address})
        ON CREATE SET
            from_w.chain = $chain,
            from_w.first_seen = $timestamp,
            from_w.last_seen = $timestamp,
            from_w.cluster_id = 'c_' + $from_address,
            from_w.entity_type = 'eoa'
        ON MATCH SET
            from_w.last_seen = CASE WHEN from_w.last_seen < $timestamp THEN $timestamp ELSE from_w.last_seen END

        MERGE (to_w:Wallet {address: $to_address})
        ON CREATE SET
            to_w.chain = $chain,
            to_w.first_seen = $timestamp,
            to_w.last_seen = $timestamp,
            to_w.cluster_id = 'c_' + $to_address,
            to_w.entity_type = 'eoa'
        ON MATCH SET
            to_w.last_seen = CASE WHEN to_w.last_seen < $timestamp THEN $timestamp ELSE to_w.last_seen END

        MERGE (from_w)-[r:TRANSACTION {tx_hash: $tx_hash}]->(to_w)
        SET
            r.chain = $chain,
            r.block_height = $block_height,
            r.timestamp = $timestamp,
            r.amount = $amount,
            r.asset = $asset,
            r.direction = $direction,
            r.is_bridge_leg = $is_bridge_leg,
            r.confidence_of_link = $confidence_of_link
        """
        params = {
            "from_address": tx.from_address,
            "to_address": tx.to_address,
            "tx_hash": tx.tx_hash,
            "chain": tx.chain,
            "block_height": tx.block_height,
            "timestamp": tx.timestamp,
            "amount": tx.amount,
            "asset": tx.asset,
            "direction": tx.direction,
            "is_bridge_leg": tx.is_bridge_leg,
            "confidence_of_link": tx.confidence_of_link,
        }
        with driver.session(database=self.database) as session:
            session.run(cypher, **params)

    def write_transactions_batch(self, txs: List[NormalizedTransaction]) -> None:
        """Batch write normalized transactions."""
        for tx in txs:
            self.write_transaction(tx)

    def write_cross_chain_link(self, link: CrossChainLink) -> None:
        """Write a CROSS_CHAIN_LINK relationship between source and destination wallets."""
        driver = self.connect()
        cypher = """
        MATCH (src:Wallet {address: $source_wallet})
        MATCH (dst:Wallet {address: $dest_wallet})
        MERGE (src)-[r:CROSS_CHAIN_LINK {
            source_chain_tx: $source_chain_tx,
            dest_chain_tx: $dest_chain_tx
        }]->(dst)
        SET
            r.bridge_contract = $bridge_contract,
            r.correlation_method = $correlation_method,
            r.correlation_confidence = $correlation_confidence
        """
        params = {
            "source_wallet": link.source_wallet,
            "dest_wallet": link.dest_wallet,
            "source_chain_tx": link.source_chain_tx,
            "dest_chain_tx": link.dest_chain_tx,
            "bridge_contract": link.bridge_contract,
            "correlation_method": link.correlation_method,
            "correlation_confidence": link.correlation_confidence,
        }
        with driver.session(database=self.database) as session:
            session.run(cypher, **params)

    def get_wallet_outgoing_transactions(self, address: str) -> List[dict]:
        """Support neighborhood lookups for T1's trace engine."""
        driver = self.connect()
        cypher = """
        MATCH (w:Wallet {address: $address})-[r:TRANSACTION]->(neighbor:Wallet)
        RETURN
            r.tx_hash AS tx_hash,
            r.chain AS chain,
            r.block_height AS block_height,
            r.timestamp AS timestamp,
            r.amount AS amount,
            r.asset AS asset,
            r.direction AS direction,
            r.is_bridge_leg AS is_bridge_leg,
            r.confidence_of_link AS confidence_of_link,
            neighbor.address AS neighbor_address,
            neighbor.entity_type AS neighbor_entity_type
        ORDER BY r.timestamp ASC
        """
        with driver.session(database=self.database) as session:
            result = session.run(cypher, address=address)
            return [record.data() for record in result]
