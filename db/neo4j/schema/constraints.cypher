// ==============================================================================
// VAJRA (SIH 26183) — Neo4j Constraints
// Strictly follows BUILD.md graph entities:
// (:Wallet), (:VASP), (:Label)
// ==============================================================================

// 1. Wallet Address Uniqueness
CREATE CONSTRAINT wallet_address IF NOT EXISTS
FOR (w:Wallet)
REQUIRE w.address IS UNIQUE;

// 2. VASP Name Uniqueness
CREATE CONSTRAINT vasp_name IF NOT EXISTS
FOR (v:VASP)
REQUIRE v.name IS UNIQUE;

// 3. Label property indexes (Community Edition compatible)
// NOTE: Multi-property uniqueness requires Enterprise; using individual indexes instead.
CREATE INDEX label_source_constraint_idx IF NOT EXISTS
FOR (l:Label)
ON (l.source);

CREATE INDEX label_text_constraint_idx IF NOT EXISTS
FOR (l:Label)
ON (l.label_text);
