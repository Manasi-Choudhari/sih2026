"use client";

import { X, ExternalLink, ShieldCheck, Link2, Copy, Check } from "lucide-react";
import { useState } from "react";
import type { TraceNode, TraceEdge } from "@/lib/api/types";

interface PathDetailProps {
  selectedNode: TraceNode | null;
  selectedEdge: TraceEdge | null;
  onClose: () => void;
}

export default function PathDetail({ selectedNode, selectedEdge, onClose }: PathDetailProps) {
  const [copied, setCopied] = useState(false);

  if (!selectedNode && !selectedEdge) return null;

  function copyText(text: string) {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="absolute right-3 top-3 bottom-3 w-84 md:w-96 bg-[#141415] border border-[#2B2B2E] rounded-lg shadow-2xl p-5 z-30 flex flex-col justify-between animate-in slide-in-from-right duration-200">
      <div className="space-y-4 overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#2B2B2E] pb-3">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#49C7BE]" />
            <h3 className="font-serif-vajra text-sm font-semibold text-[#E7EAEE]">
              {selectedNode ? "Node Inspection" : "Hop Inspection"}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded text-[#8A93A3] hover:text-[#E7EAEE] hover:bg-[#1B1B1D]"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Node Content */}
        {selectedNode && (
          <div className="space-y-3.5 text-xs">
            <div>
              <p className="text-[11px] text-[#5A6373] uppercase tracking-wider">Address</p>
              <div className="mt-1 flex items-center justify-between p-2 rounded bg-[#0A0A0B] border border-[#2B2B2E] font-mono-vajra text-[#E7EAEE]">
                <span className="truncate pr-2">{selectedNode.address}</span>
                <button
                  type="button"
                  onClick={() => copyText(selectedNode.address)}
                  className="text-[#8A93A3] hover:text-[#49C7BE] shrink-0"
                  title="Copy address"
                >
                  {copied ? <Check className="h-3.5 w-3.5 text-[#3FBE8B]" /> : <Copy className="h-3.5 w-3.5" />}
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="p-2.5 rounded bg-[#0A0A0B] border border-[#2B2B2E]">
                <p className="text-[11px] text-[#5A6373]">Entity Type</p>
                <p className="mt-0.5 font-medium text-[#E7EAEE] capitalize">{selectedNode.kind}</p>
              </div>
              <div className="p-2.5 rounded bg-[#0A0A0B] border border-[#2B2B2E]">
                <p className="text-[11px] text-[#5A6373]">Blockchain</p>
                <p className="mt-0.5 font-mono-vajra text-[#E7EAEE]">{selectedNode.chain}</p>
              </div>
            </div>

            {selectedNode.label && (
              <div>
                <p className="text-[11px] text-[#5A6373] uppercase tracking-wider">Entity Label</p>
                <p className="mt-1 text-sm font-semibold text-[#E7EAEE]">{selectedNode.label}</p>
              </div>
            )}

            {selectedNode.evidence_tier && (
              <div className="p-3 rounded bg-[#1B1B1D] border border-[#2B2B2E]">
                <div className="flex items-center gap-1.5 text-[11px] text-[#3FBE8B]">
                  <ShieldCheck className="h-3.5 w-3.5" />
                  <span>Attribution Tier: {selectedNode.evidence_tier}</span>
                </div>
                <p className="mt-1 text-[11.5px] text-[#8A93A3]">
                  Corroborated by independent label provenance records.
                </p>
              </div>
            )}

            {selectedNode.amount !== undefined && (
              <div className="p-2.5 rounded bg-[#0A0A0B] border border-[#2B2B2E]">
                <p className="text-[11px] text-[#5A6373]">Cumulative Hop Value</p>
                <p className="mt-0.5 font-mono-vajra text-sm font-semibold text-[#49C7BE]">
                  {selectedNode.amount} {selectedNode.chain}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Edge Content */}
        {selectedEdge && (
          <div className="space-y-3.5 text-xs">
            <div className="p-3 rounded bg-[#1B1B1D] border border-[#2B2B2E]">
              <div className="flex items-center justify-between">
                <span className="font-mono-vajra text-[11px] text-[#5A6373]">Hop Index {selectedEdge.hop_index}</span>
                <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-mono-vajra bg-[#0A0A0B] text-[#8A93A3]">
                  {selectedEdge.type}
                </span>
              </div>
              <p className="mt-2 font-mono-vajra text-lg font-bold text-[#E7EAEE]">
                {selectedEdge.amount} {selectedEdge.asset}
              </p>
            </div>

            {selectedEdge.type === "CROSS_CHAIN_LINK" && (
              <div className="p-3 rounded bg-[rgba(227,174,62,0.1)] border border-[rgba(227,174,62,0.3)] space-y-1.5">
                <div className="flex items-center gap-1.5 text-[#E3AE3E] font-medium">
                  <Link2 className="h-4 w-4" />
                  <span>Cross-Chain Correlation</span>
                </div>
                <p className="text-[11.5px] text-[#E7EAEE]">
                  Bridge contract: <code className="font-mono-vajra">{selectedEdge.bridge_contract ?? "Lock/Mint"}</code>
                </p>
                <p className="text-[11.5px] text-[#8A93A3]">
                  Confidence: {Math.round((selectedEdge.cross_chain_confidence ?? 0.6) * 100)}% (Explicit uncertainty applied)
                </p>
              </div>
            )}

            <div>
              <p className="text-[11px] text-[#5A6373] uppercase tracking-wider">Timestamp</p>
              <p className="mt-0.5 font-mono-vajra text-[#8A93A3]">{new Date(selectedEdge.timestamp).toUTCString()}</p>
            </div>

            {selectedEdge.tx_hash && (
              <div>
                <p className="text-[11px] text-[#5A6373] uppercase tracking-wider">Transaction Hash</p>
                <div className="mt-1 flex items-center justify-between p-2 rounded bg-[#0A0A0B] border border-[#2B2B2E] font-mono-vajra text-[#8A93A3]">
                  <span className="truncate pr-2">{selectedEdge.tx_hash}</span>
                  <ExternalLink className="h-3.5 w-3.5 shrink-0" />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="pt-3 border-t border-[#2B2B2E]">
        <button
          type="button"
          onClick={onClose}
          className="w-full py-1.5 px-3 rounded bg-[#1B1B1D] hover:bg-[#2B2B2E] text-xs font-medium text-[#E7EAEE] transition-colors"
        >
          Close Inspector
        </button>
      </div>
    </div>
  );
}
