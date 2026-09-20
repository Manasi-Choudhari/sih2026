"use client";

import { useState } from "react";
import { ShieldCheck, ShieldAlert, Loader2, RefreshCw } from "lucide-react";
import { mockApiClient } from "@/lib/api/client";
import type { VerifyResult } from "@/lib/api/types";

interface VerifyButtonProps {
  caseId: string;
}

export default function VerifyButton({ caseId }: VerifyButtonProps) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VerifyResult | null>(null);

  async function handleVerify(tamperMode = false) {
    setLoading(true);
    setResult(null);

    const testId = tamperMode ? `${caseId}-tamper` : caseId;
    const res = await mockApiClient.verifyEvidence(testId);
    setResult(res);
    setLoading(false);
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={() => handleVerify(false)}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 rounded-md bg-[#1B1B1D] border border-[#2B2B2E] text-xs font-semibold text-[#E7EAEE] hover:bg-[#2B2B2E] hover:border-[#3B82F6] transition-all disabled:opacity-50"
        >
          {loading ? (
            <>
              <Loader2 className="h-3.5 w-3.5 animate-spin text-[#3B82F6]" />
              <span>Recomputing hash chain…</span>
            </>
          ) : (
            <>
              <RefreshCw className="h-3.5 w-3.5 text-[#3B82F6]" />
              <span>Verify Cryptographic Ledger</span>
            </>
          )}
        </button>

        <button
          type="button"
          onClick={() => handleVerify(true)}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-2 rounded-md bg-[#1B1B1D]/50 border border-[#D5636A]/40 text-xs font-medium text-[#D5636A] hover:bg-[#D5636A]/10 transition-all disabled:opacity-50"
          title="Simulate a tampered record to demonstrate judge verification differentiator"
        >
          <span>Test Tamper Simulation (FAIL state)</span>
        </button>
      </div>

      {/* Loading state indicator */}
      {loading && (
        <div className="flex items-center gap-2 text-xs text-[#8A93A3] font-mono-vajra pt-1">
          <div className="w-3.5 h-3.5 rounded-full border-2 border-[#2B2B2E] border-t-[#3B82F6] animate-spin" />
          <span>Recomputing cryptographic SHA-256 state from GENESIS block…</span>
        </div>
      )}

      {/* PASS State matching reference */}
      {result && result.status === "PASS" && (
        <div className="p-3.5 rounded-lg border border-[rgba(63,190,139,0.4)] bg-[rgba(63,190,139,0.08)] flex items-start gap-3">
          <ShieldCheck className="h-5 w-5 text-[#3FBE8B] shrink-0 mt-0.5" />
          <div className="space-y-1 text-xs">
            <p className="font-semibold text-[#3FBE8B] font-mono-vajra">
              ✓ Chain verified — {result.checked_records} records unbroken
            </p>
            <p className="text-[#8A93A3]">
              Every previous hash matches the parent record content hash. Mathematical immutability confirmed at {new Date(result.verified_at).toLocaleTimeString("en-IN")}.
            </p>
          </div>
        </div>
      )}

      {/* FAIL State matching reference */}
      {result && result.status === "FAIL" && (
        <div className="p-4 rounded-lg border-2 border-[#D5636A] bg-[rgba(213,99,106,0.12)] flex items-start gap-3 shadow-lg">
          <ShieldAlert className="h-6 w-6 text-[#D5636A] shrink-0 mt-0.5" />
          <div className="space-y-1 text-xs">
            <p className="font-bold text-[#D5636A] uppercase font-mono-vajra tracking-wide text-sm">
              ✕ Chain broken at record {result.failed_record_id} — Hash mismatch detected
            </p>
            <p className="text-[#E7EAEE]">
              Record <code className="font-mono-vajra font-bold text-[#D5636A]">{result.failed_record_id}</code> stored hash does not match its recomputed SHA-256 payload.
            </p>
            <p className="text-[#8A93A3] pt-1">
              <strong>Forensic consequence:</strong> Everything before {result.failed_record_id} is intact; everything at and after has been compromised and cannot be submitted to judicial proceedings.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
