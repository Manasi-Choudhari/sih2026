"use client";

import { Target } from "lucide-react";
import type { AtlasResult } from "@/lib/api/types";

interface AtlasPanelProps {
  atlas: AtlasResult;
  leadingCandidateName: string | null;
}

export default function AtlasPanel({ atlas, leadingCandidateName }: AtlasPanelProps) {
  const robustnessPct = Math.round(atlas.robustness_score * 100);
  const isFragile = atlas.robustness_score < 0.7;

  return (
    <div className="space-y-4">
      {/* Current Leading Claim */}
      <div className="flex items-center justify-between p-3.5 rounded-lg bg-[#141415] border border-[#2B2B2E]">
        <div className="flex items-center gap-2">
          <Target className="h-4 w-4 text-[#3B82F6]" />
          <span className="text-xs text-[#5A6373] uppercase tracking-wider">Hypothesis under test:</span>
          <span className="font-serif-vajra text-sm font-semibold text-[#E7EAEE]">
            {leadingCandidateName ?? "No definitive VASP candidate"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#8A93A3]">Robustness score:</span>
          <span className="font-mono-vajra text-sm font-bold text-[#E7EAEE]">{robustnessPct}%</span>
          {isFragile && (
            <span className="px-2 py-0.5 rounded text-[10px] uppercase font-mono-vajra bg-[rgba(227,174,62,0.12)] text-[#E3AE3E] border border-[rgba(227,174,62,0.3)]">
              Fragile
            </span>
          )}
        </div>
      </div>

      {/* Structured ATLAS Rows matching reference HTML */}
      <div className="rounded-lg border border-[#2B2B2E] bg-[#141415] divide-y divide-[#2B2B2E]">
        {/* Robustness Row */}
        <div className="p-4 grid grid-cols-1 md:grid-cols-[140px_1fr] gap-3 items-center">
          <div className="text-xs font-mono-vajra uppercase text-[#5A6373]">Robustness</div>
          <div>
            <div className="flex items-center justify-between text-xs text-[#E7EAEE]">
              <span>
                {atlas.robustness_score >= 0.7
                  ? "Attribution holds up well under automated adversarial challenges."
                  : "Attribution holds under 2 of 3 challenge scenarios."}
              </span>
              <span className="font-mono-vajra text-[#8A93A3]">{robustnessPct}%</span>
            </div>
            <div className="mt-2 h-1.5 w-full rounded-full bg-[#1B1B1D] overflow-hidden">
              <div
                className="h-full amber-gradient-bg rounded-full transition-all"
                style={{ width: `${robustnessPct}%` }}
              />
            </div>
          </div>
        </div>

        {/* Alternative Hypotheses */}
        {atlas.alternatives.map((alt, idx) => (
          <div key={`alt-${idx}`} className="p-4 grid grid-cols-1 md:grid-cols-[140px_1fr] gap-3">
            <div className="text-xs font-mono-vajra uppercase text-[#5A6373]">
              Alternative {idx + 1}
            </div>
            <div className="text-xs text-[#E7EAEE] space-y-1">
              <p>{alt.hypothesis}</p>
              <p className="text-[11.5px] text-[#8A93A3]">
                Plausibility weight: <span className="font-mono-vajra">{Math.round(alt.plausibility * 100)}%</span>
              </p>
            </div>
          </div>
        ))}

        {/* Contradictions */}
        {atlas.contradictions.map((contra, idx) => (
          <div key={`contra-${idx}`} className="p-4 grid grid-cols-1 md:grid-cols-[140px_1fr] gap-3 bg-[rgba(213,99,106,0.03)]">
            <div className="text-xs font-mono-vajra uppercase text-[#D5636A]">
              Contradiction
            </div>
            <div className="text-xs text-[#D5636A] space-y-1">
              <p className="font-medium">{contra}</p>
              <p className="text-[11.5px] text-[#8A93A3]">
                Weight: high — directly impacts evidentiary continuity.
              </p>
            </div>
          </div>
        ))}

        {/* Missing Evidence */}
        {atlas.missing_data.map((miss, idx) => (
          <div key={`miss-${idx}`} className="p-4 grid grid-cols-1 md:grid-cols-[140px_1fr] gap-3">
            <div className="text-xs font-mono-vajra uppercase text-[#5A6373]">
              Missing Evidence
            </div>
            <div className="text-xs text-[#E7EAEE] space-y-1">
              <p>{miss}</p>
              <p className="text-[11.5px] text-[#60A5FA]">
                Recommended next action: subpoena target entity transaction logs.
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
