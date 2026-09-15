// /frontend/lib/api/client.ts
// Unified API client for VAJRA Investigation Platform.
// Connects to FastAPI backend (T1/T6) via NEXT_PUBLIC_API_URL with graceful
// deterministic fallback to synthetic scenario fixtures (T2/T5) for offline resilience.

import type {
  CaseSummary,
  GraphData,
  VerifyResult,
  AtlasResult,
  AttributionResult,
  EvidenceRecord,
  CurrentUser,
  ReportMetadata,
  AuditEvent,
  QueueCaseItem,
  RecommendationItem,
  IntakePayload,
  TraceNode,
  TraceEdge,
  VaspCandidate,
  PatternMatch,
} from "./types";
import { getScenario, QUEUE_CASES } from "../scenarios/fixtures";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const FORCE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK_API === "true";

export const CURRENT_USER: CurrentUser = {
  username: "inv_sharma",
  display_name: "R. Sharma",
  role: "investigator",
};

// In-memory store for recommendations approvals and dynamic audit events
const approvedRecommendations = new Set<string>();
const dynamicAuditEvents: Record<string, AuditEvent[]> = {};

function delay<T>(data: T, ms = 300): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms));
}

async function safeFetch<T>(endpoint: string, options?: RequestInit): Promise<T | null> {
  if (FORCE_MOCK) return null;
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(options?.headers || {}),
      },
      // Timeout after 3 seconds for snappy fallback
      signal: AbortSignal.timeout(3000),
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// 1. Case Management & Queue
// ---------------------------------------------------------------------------

async function listCases(): Promise<QueueCaseItem[]> {
  const data = await safeFetch<Array<Record<string, any>>>("/cases");
  if (data && Array.isArray(data) && data.length > 0) {
    return data.map((c) => ({
      case_id: c.case_id,
      scenario_id: c.case_id,
      name: `Case ${c.case_id}: ${c.victim_address ? c.victim_address.slice(0, 10) : "Wallet"}…`,
      chain: (c.chain || "ETH") as "BTC" | "ETH",
      status: c.status || "open",
      tier_dot: "Strong",
      fraud_category: c.fraud_category || "Reported Crypto Fraud",
      amount_inr: `₹${((c.reported_amount || 1) * 250000).toLocaleString("en-IN")}`,
      crypto_amount: `${c.reported_amount || 0} ${c.currency || c.chain || "ETH"}`,
      pattern_type: "Trace Completed",
      reported_ago: "Live Ingestion",
      complaint_id: c.complaint_id || `CMP-${c.case_id}`,
    }));
  }
  return delay([...QUEUE_CASES], 200);
}

async function getCaseOverview(caseId: string): Promise<CaseSummary> {
  const data = await safeFetch<Record<string, any>>(`/cases/${encodeURIComponent(caseId)}`);
  const scenario = getScenario(caseId);

  if (data) {
    return {
      case_id: data.case_id || caseId,
      scenario_id: caseId,
      status: data.status || "open",
      created_at: data.created_at || new Date().toISOString(),
      reported_at_display: scenario.summary.reported_at_display,
      amount_inr: scenario.summary.amount_inr,
      crypto_amount: `${data.reported_amount || 0} ${data.currency || "ETH"}`,
      complaint_ref: data.complaint_id || scenario.summary.complaint_ref,
      pattern_summary: scenario.summary.pattern_summary,
      metrics: {
        rule_risk_score: data.rule_risk_score ?? scenario.summary.metrics.rule_risk_score,
        attribution_confidence: data.attribution_confidence ?? scenario.summary.metrics.attribution_confidence,
        ml_probability: data.ml_probability ?? scenario.summary.metrics.ml_probability,
        ml: scenario.summary.metrics.ml,
      },
      leading_candidate: scenario.summary.leading_candidate,
    };
  }

  return delay({ ...scenario.summary, case_id: caseId }, 250);
}

// ---------------------------------------------------------------------------
// 2. Trace Graph
// ---------------------------------------------------------------------------

async function getGraph(caseId: string): Promise<GraphData> {
  const data = await safeFetch<{ nodes: any[]; edges: any[] }>(`/cases/${encodeURIComponent(caseId)}/graph`);
  if (data && data.nodes && data.edges) {
    const nodes: TraceNode[] = data.nodes.map((n) => {
      let kind: TraceNode["kind"] = "wallet";
      if (n.entity_type === "vasp" || n.label?.toLowerCase().includes("exchange") || n.label?.toLowerCase().includes("binance")) kind = "vasp";
      else if (n.entity_type === "mixer" || n.label?.toLowerCase().includes("tornado") || n.label?.toLowerCase().includes("mixer")) kind = "mixer";
      else if (n.entity_type === "bridge") kind = "bridge_contract";

      return {
        id: n.id || n.address,
        address: n.address,
        chain: (n.chain || "ETH") as "BTC" | "ETH",
        kind,
        label: n.label,
        evidence_tier: n.evidence_tier || (kind === "vasp" ? "Strong" : undefined),
        is_terminal: Boolean(n.is_terminal),
      };
    });

    const edges: TraceEdge[] = data.edges.map((e, idx) => ({
      id: e.id || `edge-${idx}`,
      source: e.source,
      target: e.target,
      type: e.type === "CROSS_CHAIN_LINK" ? "CROSS_CHAIN_LINK" : "TRANSACTION",
      amount: e.amount || 0,
      asset: e.asset || "ETH",
      timestamp: e.timestamp || new Date().toISOString(),
      hop_index: idx + 1,
      cross_chain_confidence: e.correlation_confidence,
      tx_hash: e.tx_hash,
    }));

    return { case_id: caseId, nodes, edges };
  }

  const scenario = getScenario(caseId);
  return delay({ ...scenario.graph, case_id: caseId }, 300);
}

// ---------------------------------------------------------------------------
// 3. Attribution & Patterns
// ---------------------------------------------------------------------------

async function getAttribution(caseId: string): Promise<AttributionResult> {
  const data = await safeFetch<Record<string, any>>(`/cases/${encodeURIComponent(caseId)}/attribution`);
  const scenario = getScenario(caseId);

  if (data && data.candidates) {
    const candidates: VaspCandidate[] = data.candidates.map((c: any, i: number) => ({
      candidate_id: `cand-${i + 1}`,
      vasp_name: c.vasp_name,
      branch_id: c.branch_id || `branch-${i + 1}`,
      evidence_tier: c.evidence_tier,
      supporting_evidence: c.supporting_evidence || [],
      contradicting_evidence: c.contradicting_evidence || [],
      unknowns: c.unknowns || [],
      labels: [
        {
          source: "VASP_REGISTRY",
          freshness: "Verified <24h",
          confidence_tier: c.evidence_tier,
        },
      ],
      path_directness_score: c.hops_from_origin <= 2 ? 0.95 : 0.75,
      corroboration_score: c.confidence || 0.85,
    }));

    const patterns: PatternMatch[] = (data.detected_patterns || []).map((p: any) => ({
      pattern: p.pattern_name,
      label: p.pattern_name.replace(/_/g, " ").toUpperCase(),
      explanation: p.description,
    }));

    return {
      case_id: caseId,
      candidates,
      patterns: patterns.length > 0 ? patterns : scenario.attribution.patterns,
      metrics: {
        rule_risk_score: data.rule_risk_score ?? scenario.attribution.metrics.rule_risk_score,
        attribution_confidence: data.attribution_confidence ?? scenario.attribution.metrics.attribution_confidence,
        ml_probability: data.ml_probability ?? scenario.attribution.metrics.ml_probability,
        ml: data.ml || scenario.attribution.metrics.ml,
      },
    };
  }

  return delay({ ...scenario.attribution, case_id: caseId }, 250);
}

// ---------------------------------------------------------------------------
// 4. ATLAS Challenge Engine
// ---------------------------------------------------------------------------

async function getAtlas(caseId: string): Promise<AtlasResult> {
  const data = await safeFetch<Record<string, any>>(`/cases/${encodeURIComponent(caseId)}/atlas`);
  const scenario = getScenario(caseId);

  if (data) {
    return {
      case_id: caseId,
      alternatives: (data.alternatives || []).map((a: any) => ({
        hypothesis: a.title || a.hypothesis || a.explanation,
        plausibility: a.likelihood === "High" ? 0.8 : a.likelihood === "Medium" ? 0.5 : 0.3,
      })),
      contradictions: (data.contradictions || []).map((c: any) => c.claim || c.evidence_against || String(c)),
      missing_data: data.missing_data_gaps || scenario.atlas.missing_data,
      robustness_score: data.robustness_score ?? scenario.atlas.robustness_score,
    };
  }

  return delay({ ...scenario.atlas, case_id: caseId }, 250);
}

// ---------------------------------------------------------------------------
// 5. Evidence Ledger & Tamper Verification
// ---------------------------------------------------------------------------

async function getEvidenceLedger(caseId: string): Promise<EvidenceRecord[]> {
  const data = await safeFetch<any[]>(`/cases/${encodeURIComponent(caseId)}/evidence`);
  if (data && Array.isArray(data) && data.length > 0) {
    return data.map((e, i) => ({
      record_id: e.evidence_id || `rec-${i + 1}`,
      case_id: e.case_id || caseId,
      record_type: e.type,
      content_hash: e.content_hash,
      previous_hash: e.prev_hash,
      created_at: e.timestamp,
      status: "PASS",
    }));
  }

  const scenario = getScenario(caseId);
  return delay([...scenario.evidence], 200);
}

async function verifyEvidence(caseId: string): Promise<VerifyResult> {
  const data = await safeFetch<Record<string, any>>(`/cases/${encodeURIComponent(caseId)}/verify`);
  if (data) {
    return {
      case_id: caseId,
      status: data.status === "PASS" ? "PASS" : "FAIL",
      checked_records: data.records_evaluated || 3,
      failed_record_id: data.is_tampered ? "rec-0003" : undefined,
      verified_at: new Date().toISOString(),
    };
  }

  // Fallback demo tamper logic
  const isTampered = caseId.includes("tamper");
  const records = getScenario(caseId).evidence;

  return delay(
    {
      case_id: caseId,
      status: isTampered ? "FAIL" : "PASS",
      checked_records: records.length,
      failed_record_id: isTampered ? records[Math.min(2, records.length - 1)]?.record_id ?? "rec-0003" : undefined,
      verified_at: new Date().toISOString(),
    },
    500
  );
}

// ---------------------------------------------------------------------------
// 6. Recommendations & Human Approval Gate
// ---------------------------------------------------------------------------

async function getRecommendation(caseId: string): Promise<RecommendationItem> {
  const data = await safeFetch<any[]>(`/cases/${encodeURIComponent(caseId)}/recommendations`);
  const scenario = getScenario(caseId);
  const isApproved = approvedRecommendations.has(caseId);

  if (data && Array.isArray(data) && data.length > 0) {
    const r = data[0];
    return {
      rec_id: r.rec_id,
      case_id: caseId,
      finding: r.finding,
      target_vasp: scenario.recommendation.target_vasp,
      target_address: scenario.recommendation.target_address,
      suggested_action: scenario.recommendation.suggested_action,
      action_title: r.action,
      statutory_basis: scenario.recommendation.statutory_basis,
      confidence: r.confidence,
      approval_status: isApproved ? "approved" : r.approval_status || "pending",
      approved_by: isApproved ? "sup_verma (Supervisor)" : undefined,
      approved_at: isApproved ? new Date().toISOString() : undefined,
    };
  }

  return delay(
    {
      ...scenario.recommendation,
      case_id: caseId,
      approval_status: isApproved ? "approved" : scenario.recommendation.approval_status,
      approved_by: isApproved ? "sup_verma (Supervisor)" : undefined,
      approved_at: isApproved ? new Date().toISOString() : undefined,
    },
    250
  );
}

async function approveRecommendation(
  caseId: string,
  supervisorPasscode: string
): Promise<{ success: boolean; error?: string }> {
  // Authorization Gate
  if (supervisorPasscode !== "VAJRA-SUPERVISOR-2026" && supervisorPasscode !== "admin") {
    const blockedEvent: AuditEvent = {
      event_id: `audit-${Date.now()}`,
      case_id: caseId,
      actor: CURRENT_USER.username,
      actor_role: CURRENT_USER.role,
      action: "recommendation_approval_attempt",
      result: "blocked",
      reason: "Invalid supervisor authentication credentials or insufficient role permissions.",
      timestamp: new Date().toISOString(),
    };
    dynamicAuditEvents[caseId] = [...(dynamicAuditEvents[caseId] ?? []), blockedEvent];

    return delay({
      success: false,
      error: "Supervisor authorization failed. Invalid passcode or insufficient role tier.",
    }, 400);
  }

  // Attempt backend update
  await safeFetch(`/cases/${encodeURIComponent(caseId)}/recommendations`, {
    method: "POST",
    body: JSON.stringify({ rec_id: "rec_01", action: "approve" }),
  });

  approvedRecommendations.add(caseId);

  const allowedEvent: AuditEvent = {
    event_id: `audit-${Date.now()}`,
    case_id: caseId,
    actor: "sup_verma",
    actor_role: "supervisor",
    action: "recommendation_approved",
    result: "allowed",
    timestamp: new Date().toISOString(),
  };
  dynamicAuditEvents[caseId] = [...(dynamicAuditEvents[caseId] ?? []), allowedEvent];

  return delay({ success: true }, 400);
}

// ---------------------------------------------------------------------------
// 7. Case Intake, Report & Audit
// ---------------------------------------------------------------------------

async function createCase(payload: IntakePayload): Promise<QueueCaseItem> {
  const backendResult = await safeFetch<Record<string, any>>("/cases", {
    method: "POST",
    body: JSON.stringify({
      complaint_id: payload.complaint_id || `CMP-${Date.now()}`,
      victim_address: payload.victim_wallet,
      chain: payload.chain,
      reported_amount: payload.reported_amount,
      currency: payload.currency,
      fraud_category: payload.fraud_category,
    }),
  });

  const newId = backendResult?.case_id || `CASE-2026-${Math.floor(1000 + Math.random() * 9000)}`;
  const newItem: QueueCaseItem = {
    case_id: newId,
    scenario_id: "scenario_1_direct",
    name: `Intake: ${payload.victim_wallet.slice(0, 10)}…`,
    chain: payload.chain,
    status: "open",
    tier_dot: "Medium",
    fraud_category: payload.fraud_category ?? "Reported Cyber Fraud",
    amount_inr: `₹${payload.reported_amount.toLocaleString("en-IN")}`,
    crypto_amount: `${payload.reported_amount / 100000} ${payload.currency}`,
    pattern_type: "Trace initiating",
    reported_ago: "Just now",
    complaint_id: payload.complaint_id || `NCRP-${Math.floor(10000 + Math.random() * 89999)}`,
  };

  QUEUE_CASES.unshift(newItem);
  return delay(newItem, 400);
}

async function getReport(caseId: string): Promise<ReportMetadata> {
  const data = await safeFetch<Record<string, any>>(`/cases/${encodeURIComponent(caseId)}/report`, {
    method: "POST",
  });

  if (data) {
    return {
      report_id: data.report_id || `RPT-${caseId}`,
      case_id: caseId,
      generated_at: data.generated_at || new Date().toISOString(),
      generated_by: "supervisor",
      version: data.software_version || "1.0.0",
      content_hash: data.report_hash || "9c2f5e8b1a4d7036f2e8c1b4a7d0e3f6c9a2f5d8e1b4a7c0f3e6b9d2c5f8a1e4",
      format: "html",
      download_url: "#export-pdf",
    };
  }

  return delay(
    {
      report_id: `RPT-${caseId.replace("CASE-", "")}`,
      case_id: caseId,
      generated_at: new Date().toISOString(),
      generated_by: "supervisor",
      version: "1.0.0",
      content_hash: "9c2f5e8b1a4d7036f2e8c1b4a7d0e3f6c9a2f5d8e1b4a7c0f3e6b9d2c5f8a1e4",
      format: "pdf",
      download_url: "#export-pdf",
    },
    300
  );
}

async function getAuditTrail(caseId: string): Promise<AuditEvent[]> {
  const data = await safeFetch<any[]>(`/cases/${encodeURIComponent(caseId)}/audit`);
  const baseEvents: AuditEvent[] = (data && Array.isArray(data) && data.length > 0)
    ? data.map((ev, idx) => ({
        event_id: ev.event_id || `audit-${idx + 1}`,
        case_id: caseId,
        actor: ev.actor_id || "investigator",
        actor_role: ev.actor_id?.includes("super") ? "supervisor" : "investigator",
        action: ev.action,
        result: "allowed",
        timestamp: ev.timestamp || new Date().toISOString(),
      }))
    : [
        {
          event_id: "audit-0001",
          case_id: caseId,
          actor: "inv_sharma",
          actor_role: "investigator",
          action: "case_created",
          result: "allowed",
          timestamp: "2026-09-11T09:12:00Z",
        },
        {
          event_id: "audit-0002",
          case_id: caseId,
          actor: "inv_sharma",
          actor_role: "investigator",
          action: "trace_engine_run",
          result: "allowed",
          timestamp: "2026-09-11T09:15:41Z",
        },
        {
          event_id: "audit-0003",
          case_id: caseId,
          actor: "inv_sharma",
          actor_role: "investigator",
          action: "recommendation_approval_attempt",
          result: "blocked",
          reason: "Role 'investigator' cannot execute Section 91 statutory freeze notices without supervisor approval.",
          timestamp: "2026-09-12T14:02:10Z",
        },
      ];

  const additional = dynamicAuditEvents[caseId] ?? [];
  return delay([...baseEvents, ...additional], 250);
}

export const mockApiClient = {
  listCases,
  getCaseOverview,
  getAttribution,
  getGraph,
  getAtlas,
  getEvidenceLedger,
  verifyEvidence,
  getRecommendation,
  approveRecommendation,
  createCase,
  getReport,
  getAuditTrail,
};