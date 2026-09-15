// /frontend/lib/api/client.ts
// Mock API client implementing T1 OpenAPI contract & Task 2 multi-scenario support.

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
} from "./types";
import { getScenario, QUEUE_CASES } from "../scenarios/fixtures";

function delay<T>(data: T, ms = 400): Promise<T> {
  return new Promise((resolve) => {
    setTimeout(() => resolve(data), ms);
  });
}

export const CURRENT_USER: CurrentUser = {
  username: "inv_sharma",
  display_name: "R. Sharma",
  role: "investigator",
};

// In-memory store for recommendations approvals and dynamic cases
const approvedRecommendations = new Set<string>();
const dynamicAuditEvents: Record<string, AuditEvent[]> = {};

async function listCases(): Promise<QueueCaseItem[]> {
  return delay([...QUEUE_CASES], 300);
}

async function getCaseOverview(caseId: string): Promise<CaseSummary> {
  const scenario = getScenario(caseId);
  return delay({ ...scenario.summary, case_id: caseId }, 350);
}

async function getAttribution(caseId: string): Promise<AttributionResult> {
  const scenario = getScenario(caseId);
  return delay({ ...scenario.attribution, case_id: caseId }, 350);
}

async function getGraph(caseId: string): Promise<GraphData> {
  const scenario = getScenario(caseId);
  return delay({ ...scenario.graph, case_id: caseId }, 400);
}

async function getAtlas(caseId: string): Promise<AtlasResult> {
  const scenario = getScenario(caseId);
  return delay({ ...scenario.atlas, case_id: caseId }, 350);
}

async function getEvidenceLedger(caseId: string): Promise<EvidenceRecord[]> {
  const scenario = getScenario(caseId);
  return delay([...scenario.evidence], 300);
}

async function verifyEvidence(caseId: string): Promise<VerifyResult> {
  // Deliberate tamper demonstration logic: if caseId includes "tamper" or random 25% chance in test
  const isTampered = caseId.includes("tamper");
  const records = getScenario(caseId).evidence;

  if (isTampered) {
    return delay(
      {
        case_id: caseId,
        status: "FAIL",
        checked_records: records.length,
        failed_record_id: records[Math.min(2, records.length - 1)]?.record_id ?? "rec-0003",
        verified_at: new Date().toISOString(),
      },
      800
    );
  }

  return delay(
    {
      case_id: caseId,
      status: "PASS",
      checked_records: records.length,
      verified_at: new Date().toISOString(),
    },
    800
  );
}

async function getRecommendation(caseId: string): Promise<RecommendationItem> {
  const scenario = getScenario(caseId);
  const isApproved = approvedRecommendations.has(caseId);
  return delay(
    {
      ...scenario.recommendation,
      case_id: caseId,
      approval_status: isApproved ? "approved" : scenario.recommendation.approval_status,
      approved_by: isApproved ? "sup_verma (Supervisor)" : undefined,
      approved_at: isApproved ? new Date().toISOString() : undefined,
    },
    300
  );
}

async function approveRecommendation(
  caseId: string,
  supervisorPasscode: string
): Promise<{ success: boolean; error?: string }> {
  // Hardcoded demo check for supervisor passcode
  if (supervisorPasscode !== "VAJRA-SUPERVISOR-2026" && supervisorPasscode !== "admin") {
    // Record blocked audit event
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
    }, 500);
  }

  approvedRecommendations.add(caseId);

  // Record allowed audit event
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

  return delay({ success: true }, 600);
}

async function createCase(payload: IntakePayload): Promise<QueueCaseItem> {
  const newId = `CASE-2026-${Math.floor(1000 + Math.random() * 9000)}`;
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
  return delay(newItem, 600);
}

async function getReport(caseId: string): Promise<ReportMetadata> {
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
    400
  );
}

async function getAuditTrail(caseId: string): Promise<AuditEvent[]> {
  const baseEvents: AuditEvent[] = [
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
    {
      event_id: "audit-0004",
      case_id: caseId,
      actor: "sup_verma",
      actor_role: "supervisor",
      action: "evidence_verify_called",
      result: "allowed",
      timestamp: "2026-09-12T14:18:05Z",
    },
  ];

  const additional = dynamicAuditEvents[caseId] ?? [];
  return delay([...baseEvents, ...additional], 350);
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