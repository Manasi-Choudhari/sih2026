"use client";

import { useState } from "react";
import { CheckCircle2, XCircle, HelpCircle } from "lucide-react";
import EvidenceTierBadge from "./EvidenceTierBadge";
import type { VaspCandidate, SupportingLabel } from "@/lib/api/types";

interface AttributionCardProps {
  candidate: VaspCandidate;
}

function LabelsTable({ labels }: { labels: SupportingLabel[] }) {
  if (labels.length === 0) {
    return <p className="text-xs text-[#5A6373]">No external provenance labels recorded.</p>;
  }

  return (
    <div className="overflow-hidden rounded border border-[#2B2B2E]">
      <table className="w-full text-left text-xs">
        <thead className="bg-[#141415] text-[#5A6373]">
          <tr>
            <th className="px-3 py-1.5 font-medium uppercase font-mono-vajra">Source</th>
            <th className="px-3 py-1.5 font-medium uppercase font-mono-vajra">Freshness</th>
            <th className="px-3 py-1.5 font-medium uppercase font-mono-vajra">Tier</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[#2B2B2E]">
          {labels.map((label, idx) => (
            <tr key={`${label.source}-${idx}`} className="bg-[#0A0A0B]">
              <td className="px-3 py-1.5 font-mono-vajra text-[#E7EAEE]">{label.source}</td>
              <td className="px-3 py-1.5 text-[#8A93A3]">{label.freshness}</td>
              <td className="px-3 py-1.5">
                <EvidenceTierBadge tier={label.confidence_tier} className="text-[10px]" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function AttributionCard({ candidate }: AttributionCardProps) {
  const [labelsOpen, setLabelsOpen] = useState(false);

  return (
    <article className="rounded-lg border border-[#2B2B2E] bg-[#141415] p-4.5 space-y-3.5">
      {/* Top Header: Tier + Branch */}
      <div className="flex items-center justify-between gap-3">
        <EvidenceTierBadge tier={candidate.evidence_tier} />
        <span className="text-xs font-mono-vajra text-[#5A6373]">
          Branch: <strong className="text-[#8A93A3]">{candidate.branch_id}</strong>
        </span>
      </div>

      {/* VASP Name */}
      <div>
        <h3 className="font-serif-vajra text-base font-semibold text-[#E7EAEE]">
          {candidate.vasp_name ?? <span className="italic text-[#5A6373]">Terminal — no reliable label</span>}
        </h3>
      </div>

      {/* Supporting Evidence */}
      {candidate.supporting_evidence.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-[11px] font-medium uppercase tracking-wider text-[#5A6373]">
            Supporting Evidence
          </p>
          <ul className="space-y-1">
            {candidate.supporting_evidence.map((item) => (
              <li
                key={item}
                className="flex items-start gap-2 text-xs text-[#8A93A3] rounded bg-[#1B1B1D]/60 border border-[#2B2B2E] px-2.5 py-1.5"
              >
                <CheckCircle2 className="h-3.5 w-3.5 text-[#3FBE8B] shrink-0 mt-0.5" />
                <span className="flex-1">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Contradicting Evidence */}
      {candidate.contradicting_evidence.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-[11px] font-medium uppercase tracking-wider text-[#D5636A]">
            Contradicting Evidence
          </p>
          <ul className="space-y-1">
            {candidate.contradicting_evidence.map((item) => (
              <li
                key={item}
                className="flex items-start gap-2 text-xs text-[#D5636A] rounded bg-[rgba(213,99,106,0.08)] border border-[rgba(213,99,106,0.3)] px-2.5 py-1.5"
              >
                <XCircle className="h-3.5 w-3.5 text-[#D5636A] shrink-0 mt-0.5" />
                <span className="flex-1">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Unknowns */}
      {candidate.unknowns.length > 0 && (
        <div className="space-y-1.5">
          <p className="text-[11px] font-medium uppercase tracking-wider text-[#5A6373]">
            Open Unknowns (Unresolved Gaps)
          </p>
          <ul className="space-y-1">
            {candidate.unknowns.map((item) => (
              <li
                key={item}
                className="flex items-start gap-2 text-xs text-[#8A93A3] rounded bg-[#0A0A0B] border border-[#2B2B2E] px-2.5 py-1.5"
              >
                <HelpCircle className="h-3.5 w-3.5 text-[#5C6675] shrink-0 mt-0.5" />
                <span className="flex-1">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Toggle Labels */}
      {candidate.labels.length > 0 && (
        <div className="pt-1">
          <button
            type="button"
            onClick={() => setLabelsOpen(!labelsOpen)}
            className="text-[11px] font-mono-vajra text-[#60A5FA] hover:underline"
          >
            {labelsOpen ? "▲ Hide label provenance sources" : `▼ View ${candidate.labels.length} label provenance sources`}
          </button>
          {labelsOpen && (
            <div className="mt-2">
              <LabelsTable labels={candidate.labels} />
            </div>
          )}
        </div>
      )}

      {/* Mathematical Sub-Scores */}
      <div className="flex items-center justify-between border-t border-[#2B2B2E] pt-2 text-[10.5px] font-mono-vajra text-[#5A6373]">
        <span>Path directness: <strong className="text-[#8A93A3]">{candidate.path_directness_score.toFixed(2)}</strong></span>
        <span>Corroboration index: <strong className="text-[#8A93A3]">{candidate.corroboration_score.toFixed(2)}</strong></span>
      </div>
    </article>
  );
}
