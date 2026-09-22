-- VAJRA (SIH 26183) — Migration 002: Label Provenance Storage
-- Enhances label schema for T1 attribution engine and provenance scoring

ALTER TABLE labels ADD COLUMN IF NOT EXISTS source_type VARCHAR(50) DEFAULT 'CROWDSOURCE';
ALTER TABLE labels ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE labels ADD COLUMN IF NOT EXISTS provenance_details JSONB DEFAULT '{}'::jsonb;
ALTER TABLE labels ADD COLUMN IF NOT EXISTS decay_half_life_days INTEGER DEFAULT 180;

-- Composite indices for high-speed attribution queries
CREATE INDEX IF NOT EXISTS idx_labels_wallet_tier ON labels(wallet_id, confidence_tier);
CREATE INDEX IF NOT EXISTS idx_labels_wallet_verified ON labels(wallet_id, last_verified DESC);
CREATE INDEX IF NOT EXISTS idx_labels_source ON labels(source);
