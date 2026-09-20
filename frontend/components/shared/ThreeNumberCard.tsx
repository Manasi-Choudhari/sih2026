"use client";

import { useState } from "react";
import { AlertTriangle, ChevronDown, ChevronUp } from "lucide-react";
import type { ThreeNumberMetrics } from "@/lib/api/types";

interface ThreeNumberCardProps {
  metrics: ThreeNumberMetrics;
}

export default function ThreeNumberCard({ metrics }: ThreeNumberCardProps) {
  const [expanded, setExpanded] = useState(false);
  const delta = Math.abs(metrics.rule_risk_score - metrics.ml_probability);
  const disagrees = delta > 0.05 || (metrics.rule_risk_score < 0.8 && metrics.ml_probability > 0.75);

  const confidenceTierLabel =
    metrics.attribution_confidence >= 0.8
      ? "Strong"
      : metrics.attribution_confidence >= 0.5
      ? "Medium"
      : metrics.attribution_confidence >= 0.25
      ? "Weak"
      : "Unknown";

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        {/* Signal 1: Rule-based risk score */}
        <div className="bg-[#141415] border border-[#2B2B2E] rounded-lg p-4">
          <div className="text-xs text-[#8A93A3] mb-1.5 font-medium">
            Rule-based risk score
          </div>
          <div className="font-serif-vajra text-2xl font-semibold text-[#E7EAEE] flex items-baseline gap-1.5">
            {metrics.rule_risk_score.toFixed(2)}
            <span className="font-sans text-xs text-[#5A6373] font-normal">/ 1.00</span>
          </div>
          <div className="text-[11.5px] text-[#5A6373] mt-2">
            Deterministic graph rules · Always takes legal precedence
          </div>
        </div>

        {/* Signal 2: Attribution confidence */}
        <div className="bg-[#141415] border border-[#2B2B2E] rounded-lg p-4">
          <div className="text-xs text-[#8A93A3] mb-1.5 font-medium">
            Attribution confidence
          </div>
          <div className="font-serif-vajra text-2xl font-semibold text-[#E7EAEE] flex items-baseline gap-1.5">
            {confidenceTierLabel}
            <span className="font-sans text-xs text-[#5A6373] font-normal">tier ({Math.round(metrics.attribution_confidence * 100)}%)</span>
          </div>
          <div className="text-[11.5px] text-[#5A6373] mt-2">
            Path directness + corroboration across terminal VASP
          </div>
        </div>

        {/* Signal 3: ML probability (Model Output) */}
        <div
          className={[
            "bg-[#141415] rounded-lg p-4 border transition-colors relative",
            disagrees ? "border-[#D5636A] bg-[#D5636A]/5" : "border-[#2B2B2E]",
          ].join(" ")}
        >
          <div className="text-xs text-[#8A93A3] mb-1.5 font-medium flex items-center justify-between">
            <span>ML probability</span>
            <span className="text-[10px] uppercase tracking-wider font-mono-vajra px-1.5 py-0.5 rounded bg-[#1B1B1D] text-[#8A93A3] border border-[#2B2B2E]">
              model_output
            </span>
          </div>
          <div className="font-serif-vajra text-2xl font-semibold text-[#E7EAEE] flex items-baseline gap-1.5">
            {metrics.ml_probability.toFixed(2)}
            <span className="font-sans text-xs text-[#5A6373] font-normal">
              {metrics.ml.model_name} ({metrics.ml.device})
            </span>
          </div>
          <div className="text-[11.5px] text-[#5A6373] mt-2">
            Top feature: {metrics.ml.top_features[0]?.feature ?? "graph_features"} ({Math.round((metrics.ml.top_features[0]?.importance ?? 0) * 100)}%)
          </div>

          {/* Disagreement Badge & Toggle */}
          {disagrees && (
            <button
              type="button"
              onClick={() => setExpanded(!expanded)}
              className="mt-2.5 w-full flex items-center justify-between px-2 py-1 rounded bg-[rgba(213,99,106,0.1)] border border-[rgba(213,99,106,0.35)] text-[#D5636A] text-[11px] font-medium hover:bg-[rgba(213,99,106,0.15)] transition-colors"
            >
              <span className="flex items-center gap-1.5">
                <AlertTriangle className="h-3 w-3 shrink-0" strokeWidth={2.4} />
                Rules and model disagree on verdict
              </span>
              {expanded ? (
                <ChevronUp className="h-3.5 w-3.5" />
              ) : (
                <ChevronDown className="h-3.5 w-3.5" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Disagreement Expanded Details */}
      {disagrees && expanded && (
        <div className="p-4 rounded-lg bg-[#141415] border border-[#D5636A]/50 space-y-2.5 text-xs animate-in fade-in duration-150">
          <div className="flex items-center justify-between border-b border-[#2B2B2E] pb-2 text-[#8A93A3]">
            <span>Deterministic rule verdict:</span>
            <strong className="text-[#E7EAEE] font-mono-vajra">
              {metrics.rule_risk_score >= 0.7 ? "High Risk" : "Moderate Risk"} ({metrics.rule_risk_score.toFixed(2)}) — WINS BY DEFAULT
            </strong>
          </div>
          <div className="flex items-center justify-between border-b border-[#2B2B2E] pb-2 text-[#8A93A3]">
            <span>Statistical model estimate:</span>
            <strong className="text-[#D5636A] font-mono-vajra">
              Probability {metrics.ml_probability.toFixed(2)} ({metrics.ml.top_features[0]?.feature})
            </strong>
          </div>
          <p className="text-[11.5px] text-[#8A93A3] pt-1 leading-relaxed">
            <strong>Investigator Advisory:</strong> The rule-based tier always wins by default for legal and statutory filings. The machine learning probability is surfaced as an assistive anomaly lens for prioritization; it is never a second voting authority and does not override deterministic graph evidence.
          </p>
        </div>
      )}
    </div>
  );
}
