// ==============================================================================
// VAJRA (SIH 26183) — Neo4j Indexes
// Optimized for T1 bounded BFS/priority trace and T2 neighborhood lookup
// ==============================================================================

// 1. Wallet Node Indexes
CREATE INDEX wallet_cluster_idx IF NOT EXISTS
FOR (w:Wallet)
ON (w.cluster_id);

CREATE INDEX wallet_chain_idx IF NOT EXISTS
FOR (w:Wallet)
ON (w.chain);

CREATE INDEX wallet_entity_type_idx IF NOT EXISTS
FOR (w:Wallet)
ON (w.entity_type);

CREATE INDEX wallet_scenario_idx IF NOT EXISTS
FOR (w:Wallet)
ON (w.scenario_id);

CREATE INDEX wallet_case_idx IF NOT EXISTS
FOR (w:Wallet)
ON (w.case_id);

// 2. VASP & Label Node Indexes
CREATE INDEX vasp_last_verified_idx IF NOT EXISTS
FOR (v:VASP)
ON (v.last_verified);

CREATE INDEX label_text_idx IF NOT EXISTS
FOR (l:Label)
ON (l.label_text);

CREATE INDEX label_source_idx IF NOT EXISTS
FOR (l:Label)
ON (l.source);

// 3. Transaction Relationship Property Indexes (Neo4j 4.3+)
CREATE INDEX tx_hash_idx IF NOT EXISTS
FOR ()-[r:TRANSACTION]-()
ON (r.tx_hash);

CREATE INDEX tx_timestamp_idx IF NOT EXISTS
FOR ()-[r:TRANSACTION]-()
ON (r.timestamp);

CREATE INDEX tx_chain_idx IF NOT EXISTS
FOR ()-[r:TRANSACTION]-()
ON (r.chain);

CREATE INDEX tx_bridge_leg_idx IF NOT EXISTS
FOR ()-[r:TRANSACTION]-()
ON (r.is_bridge_leg);

// 4. Cross-Chain Relationship Property Indexes
CREATE INDEX cross_chain_source_tx_idx IF NOT EXISTS
FOR ()-[r:CROSS_CHAIN_LINK]-()
ON (r.source_chain_tx);

CREATE INDEX cross_chain_dest_tx_idx IF NOT EXISTS
FOR ()-[r:CROSS_CHAIN_LINK]-()
ON (r.dest_chain_tx);

CREATE INDEX cross_chain_bridge_contract_idx IF NOT EXISTS
FOR ()-[r:CROSS_CHAIN_LINK]-()
ON (r.bridge_contract);
