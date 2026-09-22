"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, CheckCircle2, FileText } from "lucide-react";
import type { RecommendationItem } from "@/lib/api/types";
import ApprovalModal from "@/components/recommendation/ApprovalModal";

interface RecommendationsClientProps {
  initialRecommendation: RecommendationItem;
  caseId: string;
}

export default function RecommendationsClient({
  initialRecommendation,
  caseId,
}: RecommendationsClientProps) {
  const [recommendation, setRecommendation] = useState(initialRecommendation);
  const [modalOpen, setModalOpen] = useState(false);

  const isApproved = recommendation.approval_status === "approved";

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#2B2B2E] pb-4">
        <div className="flex items-center gap-3">
          <Link
            href={`/cases/${caseId}/overview`}
            className="p-1.5 rounded-md border border-[#2B2B2E] bg-[#141415] hover:bg-[#1B1B1D] text-[#8A93A3] hover:text-[#E7EAEE]"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <h1 className="font-serif-vajra text-xl font-bold text-[#E7EAEE]">
              Investigation Finding & Recommendation
            </h1>
            <p className="text-xs text-[#5A6373] font-mono-vajra">Case {caseId} · Rec ID: {recommendation.rec_id}</p>
          </div>
        </div>

        <span
          className={`px-3 py-1 rounded-full font-mono-vajra text-xs font-semibold uppercase ${
            isApproved ? "bg-[#3FBE8B]/20 text-[#3FBE8B] border border-[#3FBE8B]/30" : "bg-[#E3AE3E]/20 text-[#E3AE3E] border border-[#E3AE3E]/30"
          }`}
        >
          {recommendation.approval_status}
        </span>
      </div>

      {/* Main Finding Card */}
      <div className="rounded-lg border border-[#2B2B2E] bg-[#141415] p-6 space-y-5">
        <div>
          <span className="text-[11px] font-mono-vajra uppercase tracking-wider text-[#60A5FA]">
            Automated Next-Best Action
          </span>
          <h2 className="font-serif-vajra text-lg font-semibold text-[#E7EAEE] mt-1">
            {recommendation.action_title}
          </h2>
        </div>

        <div className="p-4 rounded bg-[#1B1B1D] border border-[#2B2B2E] text-xs text-[#8A93A3] leading-relaxed">
          <strong className="text-[#E7EAEE] block mb-1">Evidentiary Finding:</strong>
          {recommendation.finding}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3.5 rounded bg-[#0A0A0B] border border-[#2B2B2E] space-y-1">
            <span className="text-[#5A6373] uppercase font-mono-vajra text-[10.5px]">Target Entity (VASP)</span>
            <p className="text-sm font-semibold text-[#E7EAEE]">{recommendation.target_vasp}</p>
          </div>
          <div className="p-3.5 rounded bg-[#0A0A0B] border border-[#2B2B2E] space-y-1">
            <span className="text-[#5A6373] uppercase font-mono-vajra text-[10.5px]">Target Wallet / Custody Leg</span>
            <p className="font-mono-vajra text-xs text-[#60A5FA] truncate">{recommendation.target_address}</p>
          </div>
        </div>

        {/* Section 91 CrPC Formal Draft Notice Simulation */}
        <div className="rounded-lg border border-[#2B2B2E] bg-[#0A0A0B] p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-[#2B2B2E] pb-2 text-xs">
            <span className="font-semibold text-[#E7EAEE] flex items-center gap-1.5">
              <FileText className="h-4 w-4 text-[#E3AE3E]" />
              Statutory Notice Draft Preview (Simulated NCRP / Section 91 CrPC)
            </span>
            <span className="text-[10px] text-[#5A6373] font-mono-vajra">Draft v1.0</span>
          </div>

          <div className="font-mono-vajra text-[11px] text-[#8A93A3] leading-relaxed space-y-2">
            <p>
              NOTICE UNDER SECTION 91 OF CODE OF CRIMINAL PROCEDURE, 1973 r/w THE INFORMATION TECHNOLOGY ACT, 2000.
            </p>
            <p>
              TO: Legal Compliance & Law Enforcement Inquiries Officer, {recommendation.target_vasp}.
            </p>
            <p>
              REF: NCRP Cyber Crime Complaint Investigation regarding wallet {recommendation.target_address}.
            </p>
            <p>
              Pursuant to ongoing investigation by the Law Enforcement Cyber Unit, you are hereby requested to urgently freeze/hold all accounts, wallets, and KYC documents associated with the aforementioned address pending further judicial directions.
            </p>
          </div>
        </div>

        {/* Approval status banner or Action button */}
        {isApproved ? (
          <div className="p-4 rounded-lg bg-[#3FBE8B]/10 border border-[#3FBE8B]/30 flex items-center justify-between text-xs text-[#3FBE8B]">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>
                Authorized & Digitally Signed by <strong>{recommendation.approved_by}</strong> on{" "}
                {new Date(recommendation.approved_at ?? "").toLocaleString("en-IN")}.
              </span>
            </div>
            <Link
              href={`/cases/${caseId}/report`}
              className="px-3 py-1.5 rounded bg-[#16A34A] hover:bg-[#15803D] text-white font-semibold text-xs transition-colors"
            >
              Export Signed Notice
            </Link>
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-lg bg-[#1B1B1D] border border-[#2B2B2E]">
            <div className="text-xs text-[#8A93A3]">
              <p className="font-medium text-[#E7EAEE]">Requires Supervisor Clearance</p>
              <p className="text-[11.5px] text-[#5A6373]">
                Section 91 freeze notices commit formal law enforcement communication and require supervisor dual-control authorization.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setModalOpen(true)}
              className="px-4 py-2 rounded bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-semibold shrink-0 transition-colors"
            >
              Authorize & Issue Notice
            </button>
          </div>
        )}
      </div>

      <ApprovalModal
        caseId={caseId}
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
