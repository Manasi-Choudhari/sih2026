// /frontend/lib/api/types.ts
// Single source of truth for frontend types conforming to T1 OpenAPI & T3 handoff specifications.

export type MlDevice = "cuda" | "cpu";

export interface MlTopFeature {
  feature: string;
  importance: number;
}

/** Exact `ml` sub-object shape from BUILD_T1.md Task 5b / T3's handoff. */
export interface MlMetrics {
  output_label: "model_output";
  is_model_output: true;
  model_name: string;
  model_version: string;
  device: MlDevice;
  top_features: MlTopFeature[];
  disclaimer: string;
}

export interface ThreeNumberMetrics {
  rule_risk_score: number; // 0–1, deterministic rules (T1)
  attribution_confidence: number; // 0–1, VASP attribution engine (T1)
  ml_probability: number; // 0–1, T3's risk model output
  ml: MlMetrics;
}

export interface DisagreementCheck {
  disagrees: boolean;
  delta: number;
}

// ---------------------------------------------------------------------------
// VASP Attribution + Evidence Tiers
// ---------------------------------------------------------------------------

export type EvidenceTier = "Strong" | "Medium" | "Weak" | "Unknown";

export interface SupportingLabel {
  source: string;
  freshness: string;
  confidence_tier: EvidenceTier;
}

export interface VaspCandidate {
  candidate_id: string;
  vasp_name: string | null;
  branch_id: string;
  evidence_tier: EvidenceTier;
  supporting_evidence: string[];
  contradicting_evidence: string[];
  unknowns: string[];
  labels: SupportingLabel[];
  path_directness_score: number;
  corroboration_score: number;
}

export type PatternType =
  | "peel_chain"
  | "rapid_forwarding"
  | "fan_out"
  | "fan_in"
  | "structuring"
  | "mixer_privacy_boundary"
  | "bridge_detected";

export interface PatternMatch {
  pattern: PatternType;
  label: string;
  explanation: string;
  branch_id?: string;
}

export interface AttributionResult {
  case_id: string;
  candidates: VaspCandidate[];
  patterns: PatternMatch[];
  metrics: ThreeNumberMetrics;
}

// ---------------------------------------------------------------------------
// Trace Graph
// ---------------------------------------------------------------------------

export type ChainType = "BTC" | "ETH";

export type NodeKind = "wallet" | "vasp" | "mixer" | "bridge_contract";

export interface TraceNode {
  id: string;
  address: string;
  chain: ChainType;
  kind: NodeKind;
  label?: string | null;
  evidence_tier?: EvidenceTier;
  is_terminal: boolean;
  amount?: number;
}

export interface TraceEdge {
  id: string;
  source: string;
  target: string;
  type: "TRANSACTION" | "CROSS_CHAIN_LINK";
  amount: number;
  asset: string;
  timestamp: string;
  hop_index: number;
  value_retained_pct?: number;
  cross_chain_confidence?: number;
  bridge_contract?: string;
  asset_mapping?: string;
  tx_hash?: string;
}

export interface GraphData {
  case_id: string;
  nodes: TraceNode[];
  edges: TraceEdge[];
  termination_reason?:
    | "known_service_boundary"
    | "limit"
    | "evidentiary_break"
    | "mixer_scale_fanout";
}

// ---------------------------------------------------------------------------
// Evidence Ledger
// ---------------------------------------------------------------------------

export interface EvidenceRecord {
  record_id: string;
  case_id: string;
  record_type: string;
  content_hash: string;
  previous_hash: string;
  created_at: string;
  status: "PASS" | "FAIL" | "PENDING";
  is_simulated?: boolean;
}

export interface VerifyResult {
  case_id: string;
  status: "PASS" | "FAIL";
  checked_records: number;
  failed_record_id?: string;
  verified_at: string;
}

// ---------------------------------------------------------------------------
// ATLAS
// ---------------------------------------------------------------------------

export interface AtlasAlternative {
  hypothesis: string;
  plausibility: number;
}

export interface AtlasResult {
  case_id: string;
  alternatives: AtlasAlternative[];
  contradictions: string[];
  missing_data: string[];
  robustness_score: number;
}

// ---------------------------------------------------------------------------
// Case Overview & Queue
// ---------------------------------------------------------------------------

export interface CaseSummary {
  case_id: string;
  scenario_id?: string;
  status: "open" | "in_review" | "recommended" | "closed";
  created_at: string;
  reported_at_display?: string;
  amount_inr?: string;
  crypto_amount?: string;
  complaint_ref?: string;
  pattern_summary?: string;
  metrics: ThreeNumberMetrics;
  leading_candidate: VaspCandidate | null;
}

export interface QueueCaseItem {
  case_id: string;
  scenario_id: string;
  name: string;
  chain: ChainType;
  status: "open" | "in_review" | "recommended" | "closed";
  tier_dot: EvidenceTier;
  fraud_category: string;
  amount_inr: string;
  crypto_amount: string;
  pattern_type: string;
  reported_ago: string;
  complaint_id: string;
}

export interface IntakePayload {
  victim_wallet: string;
  chain: ChainType;
  reported_amount: number;
  currency: string;
  complaint_id?: string;
  fraud_category?: string;
}

// ---------------------------------------------------------------------------
// Recommendations
// ---------------------------------------------------------------------------

export interface RecommendationItem {
  rec_id: string;
  case_id: string;
  finding: string;
  target_vasp: string;
  target_address: string;
  suggested_action: "freeze_notice" | "kyc_request" | "extended_trace" | "close_unresolved";
  action_title: string;
  statutory_basis: string;
  confidence: number;
  approval_status: "pending" | "approved" | "rejected";
  approved_by?: string;
  approved_at?: string;
}

// ---------------------------------------------------------------------------
// RBAC, Report, Audit
// ---------------------------------------------------------------------------

export type UserRole = "investigator" | "supervisor" | "admin";

export interface CurrentUser {
  username: string;
  role: UserRole;
  display_name: string;
}

export interface ReportMetadata {
  report_id: string;
  case_id: string;
  generated_at: string;
  generated_by: UserRole;
  version: string;
  content_hash: string;
  format: "pdf" | "html";
  download_url: string;
}

export type AuditActionResult = "allowed" | "blocked";

export interface AuditEvent {
  event_id: string;
  case_id: string;
  actor: string;
  actor_role: UserRole;
  action: string;
  result: AuditActionResult;
  reason?: string;
  timestamp: string;
}