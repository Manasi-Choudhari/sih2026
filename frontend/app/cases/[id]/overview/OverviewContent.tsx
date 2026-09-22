"use client";

import { useState } from "react";
import Link from "next/link";
import { Maximize2, CheckCircle2, FileText, Check } from "lucide-react";
import type {
  CaseSummary,
  GraphData,
  AttributionResult,
  AtlasResult,
  EvidenceRecord,
  RecommendationItem,
  AuditEvent,
} from "@/lib/api/types";
import ThreeNumberCard from "@/components/shared/ThreeNumberCard";
import GraphView from "@/components/graph/GraphView";
import EvidenceTierBadge from "@/components/attribution/EvidenceTierBadge";
import AtlasPanel from "@/components/atlas/AtlasPanel";
import LedgerList from "@/components/evidence/LedgerList";
import VerifyButton from "@/components/evidence/VerifyButton";
import ApprovalModal from "@/components/recommendation/ApprovalModal";

interface OverviewContentProps {
  summary: CaseSummary;
  graph: GraphData;
  attribution: AttributionResult;
  atlas: AtlasResult;
  evidence: EvidenceRecord[];
  recommendation: RecommendationItem;
  auditTrail: AuditEvent[];
}

type TabKey = "atlas" | "evidence" | "recommendation" | "audit";

export default function OverviewContent({
  summary,
  graph,
  attribution,
  atlas,
  evidence,
  recommendation: initialRecommendation,
  auditTrail,
}: OverviewContentProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("atlas");
  const [modalOpen, setModalOpen] = useState(false);
  const [recommendation, setRecommendation] = useState(initialRecommendation);

  const robustnessPct = Math.round(atlas.robustness_score * 100);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* 1. Case Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#2B2B2E] pb-5">
        <div>
          <h1 className="font-serif-vajra text-2xl md:text-3xl font-bold tracking-tight text-[#E7EAEE]">
            {summary.case_id}
          </h1>
          <div className="mt-1.5 flex flex-wrap items-center gap-4 text-xs text-[#8A93A3]">
            <span>Reported <strong>{summary.reported_at_display ?? "3 days ago"}</strong></span>
            <span>Amount <strong className="text-[#E7EAEE] font-mono-vajra">{summary.amount_inr ?? "₹4,20,000"}</strong></span>
            <span>
              Origin <strong className="text-[#E7EAEE]">{summary.complaint_ref ?? "NCRP complaint #88213"}</strong>{" "}
              <em className="font-normal text-[#5A6373]">(simulated)</em>
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href={`/cases/${summary.case_id}/report`}
            className="flex items-center gap-2 px-3.5 py-2 rounded-md border border-[#2B2B2E] bg-[#141415] hover:bg-[#1B1B1D] text-xs font-medium text-[#E7EAEE] transition-colors"
          >
            <FileText className="h-3.5 w-3.5 text-[#8A93A3]" />
            <span>Export report</span>
          </Link>

          {recommendation.approval_status === "approved" ? (
            <span className="flex items-center gap-1.5 px-3.5 py-2 rounded-md bg-[#3FBE8B]/15 border border-[#3FBE8B]/30 text-xs font-semibold text-[#3FBE8B]">
              <Check className="h-3.5 w-3.5" />
              <span>Recommendation Approved</span>
            </span>
          ) : (
            <button
              type="button"
              onClick={() => setModalOpen(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-md bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-semibold transition-colors"
            >
              <span>Approve recommendation</span>
            </button>
          )}
        </div>
      </div>

      {/* 2. Three Numbers Strip — Permanently separate */}
      <section>
        <ThreeNumberCard metrics={summary.metrics} />
      </section>

      {/* 3. Trace Path Hero (Dedicated full-width section with signature clean accent) */}
      <section className="relative rounded-lg border border-[#2B2B2E] bg-[#141415] overflow-hidden">
        <div className="flex items-center justify-between p-4 border-b border-[#2B2B2E] bg-[#141415]">
          <div>
            <h2 className="text-sm font-semibold text-[#E7EAEE]">Trace path</h2>
            <p className="text-xs text-[#5A6373] font-mono-vajra">
              {graph.edges.length} hops · terminated at service boundary
            </p>
          </div>

          <div className="flex items-center gap-4">
            <span className="hidden sm:inline text-xs text-[#5A6373] font-mono-vajra">
              Depth limit 8 · value floor 1%
            </span>
            <Link
              href={`/cases/${summary.case_id}/graph`}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded bg-[#1B1B1D] border border-[#2B2B2E] text-xs font-medium text-[#E7EAEE] hover:bg-[#2B2B2E] transition-colors"
            >
              <Maximize2 className="h-3.5 w-3.5 text-[#8A93A3]" />
              <span>Expand</span>
            </Link>
          </div>
        </div>

        <div className="h-[420px] w-full">
          <GraphView graphData={graph} compact />
        </div>
      </section>

      {/* 4. Attribution Rail & Robustness Summary (Secondary Grid) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* VASP Attribution Candidates Preview */}
        <div className="lg:col-span-2 rounded-lg border border-[#2B2B2E] bg-[#141415] p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-[#2B2B2E] pb-3">
            <div>
              <h3 className="text-sm font-semibold text-[#E7EAEE]">VASP attribution candidates</h3>
              <p className="text-xs text-[#5A6373]">{attribution.candidates.length} branches traced</p>
            </div>
            <Link
              href={`/cases/${summary.case_id}/attribution`}
              className="text-xs text-[#60A5FA] hover:underline"
            >
              Deep view →
            </Link>
          </div>

          <div className="divide-y divide-[#2B2B2E]">
            {attribution.candidates.map((cand) => (
              <div key={cand.candidate_id} className="py-3 flex items-start justify-between gap-4">
                <div>
                  <h4 className="text-xs font-semibold text-[#E7EAEE]">
                    {cand.vasp_name ?? <span className="italic text-[#5A6373]">Terminal — no reliable label</span>}
                  </h4>
                  <p className="font-mono-vajra text-[11px] text-[#5A6373] mt-0.5">
                    Branch {cand.branch_id} · directness {cand.path_directness_score.toFixed(2)}
                  </p>
                </div>
                <EvidenceTierBadge tier={cand.evidence_tier} />
              </div>
            ))}
          </div>
        </div>

        {/* Robustness ATLAS Summary Gauge */}
        <div className="rounded-lg border border-[#2B2B2E] bg-[#141415] p-5 flex flex-col justify-between">
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-[#E7EAEE]">Robustness</h3>
            <p className="text-xs text-[#5A6373]">ATLAS challenge summary</p>
            <p className="text-xs text-[#8A93A3] pt-2">
              Holds under {robustnessPct > 70 ? "3 of 3" : "2 of 3"} challenge scenarios
            </p>
            <div className="h-2 w-full rounded-full bg-[#1B1B1D] overflow-hidden">
              <div
                className="h-full amber-gradient-bg rounded-full"
                style={{ width: `${robustnessPct}%` }}
              />
            </div>
          </div>
          <p className="text-[11.5px] text-[#5A6373] pt-4">
            See the ATLAS challenge tab below for adversarial alternatives and missing evidence.
          </p>
        </div>
      </div>

      {/* 5. Deep Tabs Panel: ATLAS / Evidence / Recommendation / Audit */}
      <section className="rounded-lg border border-[#2B2B2E] bg-[#141415] overflow-hidden">
        <div className="border-b border-[#2B2B2E] px-4 pt-3 flex items-center gap-2 overflow-x-auto">
          {(
            [
              { key: "atlas", label: "ATLAS challenge" },
              { key: "evidence", label: "Evidence ledger" },
              { key: "recommendation", label: "Recommendation" },
              { key: "audit", label: "Audit trail" },
            ] as const
          ).map(({ key, label }) => {
            const active = activeTab === key;
            return (
              <button
                key={key}
                type="button"
                onClick={() => setActiveTab(key)}
                className={[
                  "px-4 py-2.5 text-xs font-medium border-b-2 whitespace-nowrap transition-colors",
                  active
                    ? "border-[#3B82F6] text-[#E7EAEE]"
                    : "border-transparent text-[#8A93A3] hover:text-[#E7EAEE]",
                ].join(" ")}
              >
                {label}
              </button>
            );
          })}
        </div>

        <div className="p-5">
          {activeTab === "atlas" && (
            <AtlasPanel
              atlas={atlas}
              leadingCandidateName={summary.leading_candidate?.vasp_name ?? null}
            />
          )}

          {activeTab === "evidence" && (
            <div className="space-y-4">
              <div className="p-4 rounded-lg border border-[#2B2B2E] bg-[#1B1B1D] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold text-[#E7EAEE]">
                    Cryptographic Evidence Verification
                  </p>
                  <p className="text-[11.5px] text-[#8A93A3]">
                    Recomputes SHA-256 state from genesis block to test mathematical immutability.
                  </p>
                </div>
                <VerifyButton caseId={summary.case_id} />
              </div>
              <LedgerList records={evidence} />
            </div>
          )}

          {activeTab === "recommendation" && (
            <div className="space-y-4 text-xs">
              <div className="p-4 rounded-lg border border-[#2B2B2E] bg-[#1B1B1D] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono-vajra text-[#5A6373]">
                    Recommendation ID: {recommendation.rec_id}
                  </span>
                  <span className={`px-2 py-0.5 rounded-full font-mono-vajra text-[10px] ${
                    recommendation.approval_status === "approved"
                      ? "bg-[#3FBE8B]/20 text-[#3FBE8B]"
                      : "bg-[#E3AE3E]/20 text-[#E3AE3E]"
                  }`}>
                    {recommendation.approval_status.toUpperCase()}
                  </span>
                </div>

                <h4 className="font-serif-vajra text-sm font-semibold text-[#E7EAEE]">
                  {recommendation.action_title}
                </h4>

                <p className="text-[#8A93A3] leading-relaxed">
                  {recommendation.finding}
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-[11.5px]">
                  <div className="p-2.5 rounded bg-[#0A0A0B] border border-[#2B2B2E]">
                    <p className="text-[#5A6373]">Target Custodian</p>
                    <p className="mt-0.5 font-medium text-[#E7EAEE]">{recommendation.target_vasp}</p>
                  </div>
                  <div className="p-2.5 rounded bg-[#0A0A0B] border border-[#2B2B2E]">
                    <p className="text-[#5A6373]">Statutory Basis</p>
                    <p className="mt-0.5 font-medium text-[#E7EAEE]">{recommendation.statutory_basis}</p>
                  </div>
                </div>

                {recommendation.approved_by && (
                  <div className="p-2.5 rounded bg-[#3FBE8B]/10 border border-[#3FBE8B]/30 flex items-center gap-2 text-[#3FBE8B]">
                    <CheckCircle2 className="h-4 w-4 shrink-0" />
                    <span>Authorized by {recommendation.approved_by}</span>
                  </div>
                )}
              </div>

              {recommendation.approval_status !== "approved" && (
                <div className="flex justify-end">
                  <button
                    type="button"
                    onClick={() => setModalOpen(true)}
                    className="px-4 py-2 rounded bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-semibold transition-colors"
                  >
                    Authorize Recommendation (Supervisor Gate)
                  </button>
                </div>
              )}
            </div>
          )}

          {activeTab === "audit" && (
            <div className="space-y-3">
              <div className="rounded border border-[#2B2B2E] overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#1B1B1D] text-[#5A6373]">
                    <tr>
                      <th className="px-3 py-2 font-mono-vajra">Timestamp</th>
                      <th className="px-3 py-2 font-mono-vajra">Actor</th>
                      <th className="px-3 py-2 font-mono-vajra">Action</th>
                      <th className="px-3 py-2 font-mono-vajra">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#2B2B2E] font-mono-vajra">
                    {auditTrail.map((ev) => (
                      <tr key={ev.event_id} className="bg-[#141415]">
                        <td className="px-3 py-2 text-[#8A93A3] whitespace-nowrap">
                          {new Date(ev.timestamp).toLocaleTimeString("en-IN")}
                        </td>
                        <td className="px-3 py-2 text-[#E7EAEE]">
                          {ev.actor} ({ev.actor_role})
                        </td>
                        <td className="px-3 py-2 text-[#8A93A3]">
                          {ev.action}
                          {ev.reason && (
                            <p className="text-[10.5px] text-[#D5636A] font-sans pt-0.5">{ev.reason}</p>
                          )}
                        </td>
                        <td className="px-3 py-2">
                          <span
                            className={`px-1.5 py-0.5 rounded text-[10px] uppercase ${
                              ev.result === "allowed"
                                ? "bg-[#3FBE8B]/20 text-[#3FBE8B]"
                                : "bg-[#D5636A]/20 text-[#D5636A]"
                            }`}
                          >
                            {ev.result}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Supervisor Approval Modal */}
      <ApprovalModal
        caseId={summary.case_id}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSuccess={() => {
          setRecommendation((prev) => ({
            ...prev,
            approval_status: "approved",
            approved_by: "sup_verma (Supervisor)",
            approved_at: new Date().toISOString(),
          }));
        }}
      />
    </div>
  );
}
