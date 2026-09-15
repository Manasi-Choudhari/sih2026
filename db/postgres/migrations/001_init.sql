-- VAJRA (SIH 26183) — Migration 001: Initial Schema Freeze
-- Strictly follows BUILD.md relational entities:
-- Complaint, Case, Wallet, VASP, Label, Evidence, Recommendation, Alert, AuditEvent

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Complaint
CREATE TABLE IF NOT EXISTS complaints (
    complaint_id VARCHAR(64) PRIMARY KEY,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fraud_category VARCHAR(100) NOT NULL,
    reported_amount NUMERIC(24, 8) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    victim_ref VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Case
CREATE TABLE IF NOT EXISTS cases (
    case_id VARCHAR(64) PRIMARY KEY,
    complaint_id VARCHAR(64) REFERENCES complaints(complaint_id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN',
    assigned_investigator VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Alias view for singular "case" to support queries expecting exact table name Case
CREATE OR REPLACE VIEW "case" AS SELECT * FROM cases;

-- 3. Wallet
CREATE TABLE IF NOT EXISTS wallets (
    wallet_id VARCHAR(64) PRIMARY KEY,
    address VARCHAR(255) NOT NULL UNIQUE,
    chain VARCHAR(20) NOT NULL,
    first_seen TIMESTAMPTZ,
    last_seen TIMESTAMPTZ,
    cluster_id VARCHAR(64),
    entity_type VARCHAR(50) DEFAULT 'eoa',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW wallet AS SELECT * FROM wallets;

-- 4. VASP
CREATE TABLE IF NOT EXISTS vasps (
    vasp_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    known_addresses TEXT[] DEFAULT '{}',
    last_verified TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW vasp AS SELECT * FROM vasps;

-- 5. Label
CREATE TABLE IF NOT EXISTS labels (
    label_id VARCHAR(64) PRIMARY KEY,
    wallet_id VARCHAR(64) REFERENCES wallets(wallet_id) ON DELETE CASCADE,
    source VARCHAR(100) NOT NULL,
    label_text VARCHAR(255) NOT NULL,
    confidence_tier VARCHAR(20) NOT NULL CHECK (confidence_tier IN ('Strong', 'Medium', 'Weak', 'Unknown')),
    first_seen TIMESTAMPTZ,
    last_verified TIMESTAMPTZ,
    confidence NUMERIC(5, 4) DEFAULT 1.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW label AS SELECT * FROM labels;

-- 6. Evidence
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    source VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    prev_hash VARCHAR(64) NOT NULL,
    software_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7. Recommendation
CREATE TABLE IF NOT EXISTS recommendations (
    rec_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    finding TEXT NOT NULL,
    evidence_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    confidence NUMERIC(5, 4) NOT NULL,
    action TEXT NOT NULL,
    approval_status VARCHAR(50) NOT NULL DEFAULT 'PENDING' CHECK (approval_status IN ('PENDING', 'APPROVED', 'REJECTED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE VIEW recommendation AS SELECT * FROM recommendations;

-- 8. Alert
CREATE TABLE IF NOT EXISTS alerts (
    alert_id VARCHAR(64) PRIMARY KEY,
    case_id VARCHAR(64) NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    triggered_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    rule_fired VARCHAR(100) NOT NULL,
    delivered_at TIMESTAMPTZ
);

CREATE OR REPLACE VIEW alert AS SELECT * FROM alerts;

-- 9. AuditEvent
CREATE TABLE IF NOT EXISTS audit_events (
    event_id VARCHAR(64) PRIMARY KEY,
    actor_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    target_id VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    details JSONB DEFAULT '{}'::jsonb
);

CREATE OR REPLACE VIEW audit_event AS SELECT * FROM audit_events;

-- Indices for common lookups
CREATE INDEX IF NOT EXISTS idx_cases_complaint_id ON cases(complaint_id);
CREATE INDEX IF NOT EXISTS idx_wallets_address ON wallets(address);
CREATE INDEX IF NOT EXISTS idx_wallets_cluster_id ON wallets(cluster_id);
CREATE INDEX IF NOT EXISTS idx_labels_wallet_id ON labels(wallet_id);
CREATE INDEX IF NOT EXISTS idx_evidence_case_id ON evidence(case_id);
CREATE INDEX IF NOT EXISTS idx_evidence_prev_hash ON evidence(prev_hash);
CREATE INDEX IF NOT EXISTS idx_recommendations_case_id ON recommendations(case_id);
CREATE INDEX IF NOT EXISTS idx_alerts_case_id ON alerts(case_id);
CREATE INDEX IF NOT EXISTS idx_audit_events_target ON audit_events(target_id);
