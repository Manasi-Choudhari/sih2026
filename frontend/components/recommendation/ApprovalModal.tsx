"use client";

import { useState } from "react";
import { ShieldCheck, AlertTriangle, X, Lock, Check } from "lucide-react";
import { mockApiClient } from "@/lib/api/client";

interface ApprovalModalProps {
  caseId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function ApprovalModal({
  caseId,
  isOpen,
  onClose,
  onSuccess,
}: ApprovalModalProps) {
  const [passcode, setPasscode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const res = await mockApiClient.approveRecommendation(caseId, passcode);
    setLoading(false);

    if (res.success) {
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        onSuccess();
        onClose();
      }, 1500);
    } else {
      setError(res.error ?? "Authorization rejected");
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg rounded-xl border border-[#2B2B2E] bg-[#141415] p-6 shadow-2xl space-y-5 animate-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#2B2B2E] pb-3.5">
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#E3AE3E]" />
            <h2 className="font-serif-vajra text-base font-semibold text-[#E7EAEE]">
              Supervisor Approval Gate
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded text-[#8A93A3] hover:text-[#E7EAEE]"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Irreversible Warning */}
        <div className="p-3.5 rounded-lg border border-[#E3AE3E]/30 bg-[#E3AE3E]/10 flex items-start gap-3 text-xs">
          <AlertTriangle className="h-4 w-4 text-[#E3AE3E] shrink-0 mt-0.5" />
          <div className="space-y-1 text-[#E7EAEE]">
            <strong className="text-[#E3AE3E]">Statutory Notice Authorization:</strong>
            <p className="text-[#8A93A3]">
              Approving this action locks the case findings, appends an immutable record to the Evidence Ledger, and prepares Section 91 CrPC freeze requests. This operation cannot be rolled back.
            </p>
          </div>
        </div>

        {success ? (
          <div className="p-6 text-center space-y-2">
            <div className="w-10 h-10 rounded-full bg-[#3FBE8B]/20 text-[#3FBE8B] mx-auto flex items-center justify-center">
              <Check className="h-5 w-5" strokeWidth={2.5} />
            </div>
            <p className="font-serif-vajra text-sm font-semibold text-[#E7EAEE]">
              Recommendation Approved & Signed
            </p>
            <p className="text-xs text-[#8A93A3]">
              Audit event recorded with supervisor credentials.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-[#8A93A3] mb-1.5">
                Supervisor Authorization Code
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={passcode}
                  onChange={(e) => setPasscode(e.target.value)}
                  placeholder="Enter passcode (e.g. admin or VAJRA-SUPERVISOR-2026)"
                  className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md px-3.5 py-2 text-xs font-mono-vajra text-[#E7EAEE] placeholder-[#5A6373] focus:outline-none focus:border-[#3B82F6]"
                  autoFocus
                />
                <Lock className="absolute right-3 top-2.5 h-4 w-4 text-[#5A6373]" />
              </div>
              <p className="mt-1.5 text-[11px] text-[#5A6373]">
                Demo passcodes: <code className="font-mono-vajra text-[#8A93A3]">admin</code> or <code className="font-mono-vajra text-[#8A93A3]">VAJRA-SUPERVISOR-2026</code>
              </p>
            </div>

            {error && (
              <div className="p-3 rounded bg-[rgba(213,99,106,0.1)] border border-[rgba(213,99,106,0.3)] text-xs text-[#D5636A]">
                {error}
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3.5 py-2 rounded border border-[#2B2B2E] bg-[#141415] hover:bg-[#1B1B1D] text-xs font-medium text-[#8A93A3]"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading || !passcode}
                className="flex items-center gap-2 px-4 py-2 rounded bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-semibold transition-colors disabled:opacity-40"
              >
                <ShieldCheck className="h-4 w-4" />
                <span>{loading ? "Authenticating…" : "Authorize & Sign"}</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
