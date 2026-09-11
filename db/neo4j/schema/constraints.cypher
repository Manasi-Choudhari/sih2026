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

// 3. Label text + source uniqueness (optional or node key constraint where supported)
// In Neo4j Community, property existence/uniqueness constraints:
CREATE CONSTRAINT label_composite IF NOT EXISTS
FOR (l:Label)
REQUIRE (l.source, l.label_text) IS UNIQUE;
