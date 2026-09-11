-- VAJRA (SIH 26183) — Migration 003: ATLAS Persistence
-- Storage for ATLAS result records: alternatives, contradictions, missing evidence, robustness score

CREATE TABLE IF NOT EXISTS atlas_results (
    atlas_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    alternatives JSONB NOT NULL DEFAULT '[]'::jsonb,
    contradictions JSONB NOT NULL DEFAULT '[]'::jsonb,
    missing_evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
    robustness_score NUMERIC(5, 4) NOT NULL,
    challenger_hypothesis TEXT,
    evaluated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW atlas_result AS SELECT * FROM atlas_results;

CREATE INDEX IF NOT EXISTS idx_atlas_case_id ON atlas_results(case_id);
CREATE INDEX IF NOT EXISTS idx_atlas_evaluated_at ON atlas_results(evaluated_at DESC);
