"use client";

import { useState } from "react";
import { Split, Merge, Zap, Layers, ShieldOff, Link2, ChevronDown } from "lucide-react";
import type { PatternMatch, PatternType } from "@/lib/api/types";

const PATTERN_ICON: Record<PatternType, typeof Split> = {
  peel_chain: Layers,
  rapid_forwarding: Zap,
  fan_out: Split,
  fan_in: Merge,
  structuring: ShieldOff,
  mixer_privacy_boundary: ShieldOff,
  bridge_detected: Link2,
};

function PatternPill({ match }: { match: PatternMatch }) {
  const [open, setOpen] = useState(false);
  const Icon = PATTERN_ICON[match.pattern] ?? Layers;

  return (
    <div className="rounded-md border border-[#2B2B2E] bg-[#141415]">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-2 px-3 py-2 text-left"
      >
        <span className="inline-flex items-center gap-2 text-xs font-semibold text-[#E7EAEE]">
          <Icon className="h-3.5 w-3.5 text-[#60A5FA]" strokeWidth={2.2} />
          {match.label}
          {match.branch_id && (
            <span className="font-mono-vajra text-[10px] font-normal text-[#5A6373]">
              ({match.branch_id})
            </span>
          )}
        </span>
        <ChevronDown
          className={`h-3.5 w-3.5 text-[#5A6373] transition-transform ${open ? "rotate-180" : ""}`}
          strokeWidth={2}
        />
      </button>
      {open && (
        <p className="border-t border-[#2B2B2E] px-3 py-2 text-xs leading-relaxed text-[#8A93A3] bg-[#0A0A0B]">
          {match.explanation}
        </p>
      )}
    </div>
  );
}

export default function PatternBadges({ patterns }: { patterns: PatternMatch[] }) {
  if (patterns.length === 0) {
    return (
      <p className="text-xs text-[#5A6373]">No deterministic patterns matched on this case.</p>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
      {patterns.map((match, idx) => (
        <PatternPill key={`${match.pattern}-${match.branch_id ?? "none"}-${idx}`} match={match} />
      ))}
    </div>
  );
}