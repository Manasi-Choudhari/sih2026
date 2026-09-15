-- VAJRA (SIH 26183) — Migration 005: Recommendation Approval Gate & Report Persistence
-- Adds approval gate audit fields to recommendations and table for generated report metadata

-- 1. Recommendation approval gate additions
ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS approved_by VARCHAR(255);
ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS approved_at TIMESTAMPTZ;
ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- 2. Report Metadata Table
CREATE TABLE IF NOT EXISTS case_reports (
    report_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    report_hash VARCHAR(64) NOT NULL,
    version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    format VARCHAR(20) NOT NULL DEFAULT 'JSON',
    report_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    summary TEXT,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW case_report AS SELECT * FROM case_reports;

CREATE INDEX IF NOT EXISTS idx_case_reports_case_id ON case_reports(case_id);
CREATE INDEX IF NOT EXISTS idx_case_reports_generated ON case_reports(generated_at DESC);
