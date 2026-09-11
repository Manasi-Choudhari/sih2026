-- VAJRA (SIH 26183) — Migration 004: Model Estimate Storage
-- Persists versioned ML risk scoring outputs per case/wallet (T3 handoff contract)

CREATE TABLE IF NOT EXISTS model_estimates (
    estimate_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    wallet_id VARCHAR(64),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(100) NOT NULL,
    score NUMERIC(5, 4) NOT NULL,
    label VARCHAR(50) NOT NULL,
    top_features JSONB NOT NULL DEFAULT '[]'::jsonb,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_model_output BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE OR REPLACE VIEW model_estimate AS SELECT * FROM model_estimates;

CREATE INDEX IF NOT EXISTS idx_model_estimates_case_id ON model_estimates(case_id);
CREATE INDEX IF NOT EXISTS idx_model_estimates_wallet_id ON model_estimates(wallet_id);
CREATE INDEX IF NOT EXISTS idx_model_estimates_generated ON model_estimates(generated_at DESC);
