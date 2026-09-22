"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, ShieldAlert, ShieldCheck } from "lucide-react";
import type { AuditEvent } from "@/lib/api/types";

interface AuditViewProps {
  initialEvents: AuditEvent[];
  caseId: string;
}

export default function AuditView({ initialEvents, caseId }: AuditViewProps) {
  const [filter, setFilter] = useState<"all" | "allowed" | "blocked">("all");

  const filtered = initialEvents.filter((ev) => {
    if (filter === "allowed") return ev.result === "allowed";
    if (filter === "blocked") return ev.result === "blocked";
    return true;
  });

  return (
    <div className="max-w-5xl mx-auto space-y-6">
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
              Immutable Audit Trail — {caseId}
            </h1>
            <p className="text-xs text-[#5A6373] font-mono-vajra">
              Cryptographic tracking of all officer, supervisor, and system enforcement activities
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 p-1 rounded-md bg-[#141415] border border-[#2B2B2E] text-xs">
          <button
            type="button"
            onClick={() => setFilter("all")}
            className={`px-2.5 py-1 rounded font-mono-vajra ${
              filter === "all" ? "bg-[#1B1B1D] text-[#E7EAEE]" : "text-[#8A93A3]"
            }`}
          >
            All ({initialEvents.length})
          </button>
          <button
            type="button"
            onClick={() => setFilter("allowed")}
            className={`px-2.5 py-1 rounded font-mono-vajra ${
              filter === "allowed" ? "bg-[#3FBE8B]/20 text-[#3FBE8B]" : "text-[#8A93A3]"
            }`}
          >
            Allowed
          </button>
          <button
            type="button"
            onClick={() => setFilter("blocked")}
            className={`px-2.5 py-1 rounded font-mono-vajra ${
              filter === "blocked" ? "bg-[#D5636A]/20 text-[#D5636A]" : "text-[#8A93A3]"
            }`}
          >
            Blocked (RBAC)
          </button>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="overflow-hidden rounded-lg border border-[#2B2B2E] bg-[#141415]">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#1B1B1D] border-b border-[#2B2B2E] text-[#5A6373]">
            <tr>
              <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Event ID & Time</th>
              <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Actor & Role</th>
              <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Action Requested</th>
              <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Policy Result</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#2B2B2E] font-mono-vajra">
            {filtered.map((ev) => {
              const isAllowed = ev.result === "allowed";

              return (
                <tr key={ev.event_id} className="hover:bg-[#1B1B1D] transition-colors">
                  <td className="px-4 py-3.5 whitespace-nowrap">
                    <p className="font-semibold text-[#E7EAEE]">{ev.event_id}</p>
                    <p className="text-[11px] text-[#5A6373]">
                      {new Date(ev.timestamp).toLocaleString("en-IN")}
                    </p>
                  </td>
                  <td className="px-4 py-3.5">
                    <p className="text-[#E7EAEE] font-medium">{ev.actor}</p>
                    <p className="text-[11px] text-[#8A93A3] capitalize font-sans">{ev.actor_role}</p>
                  </td>
                  <td className="px-4 py-3.5 font-sans">
                    <p className="text-[#E7EAEE] font-mono-vajra text-xs">{ev.action}</p>
                    {ev.reason && (
                      <p className="text-[11px] text-[#D5636A] mt-1 bg-[rgba(213,99,106,0.08)] border border-[rgba(213,99,106,0.2)] rounded px-2 py-1 max-w-lg">
                        <strong>Policy Block:</strong> {ev.reason}
                      </p>
                    )}
                  </td>
                  <td className="px-4 py-3.5">
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase ${
                        isAllowed
                          ? "bg-[rgba(63,190,139,0.15)] text-[#3FBE8B] border border-[rgba(63,190,139,0.3)]"
                          : "bg-[rgba(213,99,106,0.15)] text-[#D5636A] border border-[rgba(213,99,106,0.3)]"
                      }`}
                    >
                      {isAllowed ? (
                        <ShieldCheck className="h-3 w-3" />
                      ) : (
                        <ShieldAlert className="h-3 w-3" />
                      )}
                      <span>{ev.result}</span>
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
