"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Plus, ArrowRight, Search, Filter, ShieldCheck, Globe } from "lucide-react";
import type { QueueCaseItem } from "@/lib/api/types";
import { mockApiClient } from "@/lib/api/client";

interface QueueViewProps {
  initialCases: QueueCaseItem[];
}

export default function QueueView({ initialCases }: QueueViewProps) {
  const [cases, setCases] = useState(initialCases);
  const [search, setSearch] = useState("");
  const [intakeOpen, setIntakeOpen] = useState(false);
  const [newWallet, setNewWallet] = useState("");
  const [newAmount, setNewAmount] = useState("500000");
  const [newChain, setNewChain] = useState<"BTC" | "ETH">("ETH");
  const [creating, setCreating] = useState(false);
  const [lastSyncedAt, setLastSyncedAt] = useState<Date>(new Date());

  // Live Auto-Refresh: Polls backend every 3.5s to capture real-time complaints filed via NCRP portal / webhook
  useEffect(() => {
    let mounted = true;

    const pollCases = async () => {
      try {
        const latest = await mockApiClient.listCases();
        if (mounted && Array.isArray(latest) && latest.length > 0) {
          setCases(latest);
          setLastSyncedAt(new Date());
        }
      } catch (err) {
        console.warn("Queue auto-poll notice:", err);
      }
    };

    const interval = setInterval(pollCases, 3500);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const filtered = cases.filter(
    (c) =>
      c.case_id.toLowerCase().includes(search.toLowerCase()) ||
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.fraud_category.toLowerCase().includes(search.toLowerCase()) ||
      (c.complaint_id && c.complaint_id.toLowerCase().includes(search.toLowerCase()))
  );

  async function handleIntake(e: React.FormEvent) {
    e.preventDefault();
    if (!newWallet) return;

    setCreating(true);
    const created = await mockApiClient.createCase({
      victim_wallet: newWallet,
      chain: newChain,
      reported_amount: parseFloat(newAmount) || 100000,
      currency: newChain,
      fraud_category: "Simulated Intake Complaint",
    });

    setCases([created, ...cases]);
    setCreating(false);
    setIntakeOpen(false);
    setNewWallet("");
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#2B2B2E] pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="font-serif-vajra text-2xl md:text-3xl font-bold text-[#E7EAEE]">
              Investigation Queue
            </h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-[#3B82F6]/30 bg-[#3B82F6]/10 text-[11px] font-mono-vajra text-[#60A5FA]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#3B82F6]" />
              NCRP Gateway Live
            </span>
          </div>
          <p className="mt-1 text-xs text-[#8A93A3]">
            {filtered.length} active complaints prioritized by automated graph rules and anomaly models · Auto-synced from 1930 National Helpline
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link
            href="/ncrp"
            className="flex items-center gap-2 px-3.5 py-2 rounded-md border border-[#2B2B2E] bg-[#141415] hover:bg-[#1B1B1D] text-[#E7EAEE] text-xs font-medium transition-colors"
          >
            <Globe className="h-4 w-4 text-[#60A5FA]" />
            <span>Lodge on NCRP Portal (1930)</span>
          </Link>

          <button
            type="button"
            onClick={() => setIntakeOpen(true)}
            className="flex items-center gap-2 px-4 py-2 rounded-md bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-semibold transition-colors"
          >
            <Plus className="h-4 w-4" />
            <span>New Case Intake</span>
          </button>
        </div>
      </div>

      {/* Live NCRP Gateway Banner */}
      <div className="flex items-center justify-between px-4 py-2.5 rounded-lg border border-[#2B2B2E] bg-[#141415]/80 text-xs">
        <div className="flex items-center gap-2.5 text-[#8A93A3]">
          <ShieldCheck className="h-4 w-4 text-[#3B82F6]" />
          <span>
            <strong className="text-[#E7EAEE]">I4C / CFCFRMS Zero-Second Pipeline:</strong> All complaints lodged via the National Portal (or 1930 Helpline) are auto-triaged, traced through multi-hop chains, and assigned to this queue with instant freeze recommendations.
          </span>
        </div>
        <span className="hidden md:inline font-mono-vajra text-[11px] text-[#5A6373]">
          Synced {lastSyncedAt.toLocaleTimeString()}
        </span>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-[#5A6373]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter by Case ID, name, or fraud typology…"
            className="w-full pl-9 pr-3 py-2 rounded-md bg-[#141415] border border-[#2B2B2E] text-xs text-[#E7EAEE] placeholder-[#5A6373] focus:outline-none focus:border-[#3B82F6]"
          />
        </div>

        <div className="flex items-center gap-2 text-xs text-[#8A93A3]">
          <Filter className="h-3.5 w-3.5 text-[#5A6373]" />
          <span>Prioritized by:</span>
          <span className="font-mono-vajra text-[#E7EAEE]">Risk Score (Deterministic)</span>
        </div>
      </div>

      {/* Triage Cases Table */}
      <div className="overflow-hidden rounded-lg border border-[#2B2B2E] bg-[#141415]">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#1B1B1D] border-b border-[#2B2B2E] text-[#5A6373]">
              <tr>
                <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Case ID</th>
                <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Status & Tier</th>
                <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Typology</th>
                <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Amount (INR)</th>
                <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Crypto Leg</th>
                <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Reported</th>
                <th className="px-4 py-3 text-right font-medium uppercase font-mono-vajra">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#2B2B2E]">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center text-xs text-[#8A93A3]">
                    <div className="max-w-md mx-auto space-y-2">
                      <p className="text-sm font-semibold text-[#E7EAEE]">No complaints found in investigation queue</p>
                      <p className="text-[11px] text-[#5A6373]">
                        The queue is currently empty. Start the FastAPI backend (<code className="text-[#60A5FA]">localhost:8000</code>) to access seeded cases, or use the <strong>New Intake Case</strong> button above to create one.
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                filtered.map((item) => {
                  const dotColor =
                    item.tier_dot === "Strong"
                      ? "#3FBE8B"
                      : item.tier_dot === "Medium"
                      ? "#E3AE3E"
                      : item.tier_dot === "Weak"
                      ? "#C56A4B"
                      : "#5C6675";

                  return (
                    <tr key={item.case_id} className="hover:bg-[#1B1B1D] transition-colors">
                      <td className="px-4 py-3.5 font-mono-vajra font-semibold text-[#E7EAEE]">
                        <Link
                          href={`/cases/${item.case_id}/overview`}
                          className="hover:text-[#60A5FA] hover:underline"
                        >
                          {item.case_id}
                        </Link>
                        <div className="text-[10px] text-[#5A6373] font-normal">{item.complaint_id}</div>
                      </td>
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-2">
                          <span
                            className="w-2 h-2 rounded-full shrink-0"
                            style={{ backgroundColor: dotColor }}
                          />
                          <span className="capitalize text-[#E7EAEE] font-medium">{item.status.replace("_", " ")}</span>
                          <span className="font-mono-vajra text-[10px] text-[#5A6373]">({item.tier_dot})</span>
                        </div>
                      </td>
                      <td className="px-4 py-3.5">
                        <p className="text-[#E7EAEE] font-medium">{item.name}</p>
                        <p className="text-[11px] text-[#5A6373]">{item.pattern_type}</p>
                      </td>
                      <td className="px-4 py-3.5 font-mono-vajra font-bold text-[#E7EAEE]">
                        {item.amount_inr}
                      </td>
                      <td className="px-4 py-3.5 font-mono-vajra text-[#8A93A3]">
                        <span className="px-1.5 py-0.5 rounded border border-[#2B2B2E] bg-[#0A0A0B] mr-1.5 text-[10px] text-[#60A5FA]">
                          {item.chain}
                        </span>
                        {item.crypto_amount}
                      </td>
                      <td className="px-4 py-3.5 text-[#8A93A3] whitespace-nowrap">
                        {item.reported_ago}
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <Link
                          href={`/cases/${item.case_id}/overview`}
                          className="inline-flex items-center gap-1 px-3 py-1.5 rounded border border-[#2B2B2E] bg-[#141415] hover:bg-[#2B2B2E] text-xs text-[#60A5FA] font-medium transition-colors"
                        >
                          <span>Investigate</span>
                          <ArrowRight className="h-3 w-3" />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Intake Modal */}
      {intakeOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-xl border border-[#2B2B2E] bg-[#141415] p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-[#2B2B2E] pb-3">
              <h3 className="font-serif-vajra text-base font-semibold text-[#E7EAEE]">
                Initiate New Wallet Investigation
              </h3>
              <button
                type="button"
                onClick={() => setIntakeOpen(false)}
                className="text-[#8A93A3] hover:text-[#E7EAEE]"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleIntake} className="space-y-3.5 text-xs">
              <div>
                <label className="block text-[#8A93A3] mb-1">Victim / Reporting Wallet Address</label>
                <input
                  type="text"
                  required
                  placeholder="0x... (ETH) or bc1q... (BTC)"
                  value={newWallet}
                  onChange={(e) => setNewWallet(e.target.value)}
                  className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded p-2 text-xs font-mono-vajra text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#8A93A3] mb-1">Blockchain</label>
                  <select
                    value={newChain}
                    onChange={(e) => setNewChain(e.target.value as "BTC" | "ETH")}
                    className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded p-2 text-xs text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
                  >
                    <option value="ETH">Ethereum (ETH)</option>
                    <option value="BTC">Bitcoin (BTC)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[#8A93A3] mb-1">Reported Amount (INR)</label>
                  <input
                    type="number"
                    value={newAmount}
                    onChange={(e) => setNewAmount(e.target.value)}
                    className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded p-2 text-xs font-mono-vajra text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
                  />
                </div>
              </div>

              <div className="p-3 rounded bg-[#1B1B1D] border border-[#2B2B2E] text-[11px] text-[#8A93A3]">
                Starting a trace queries the normalized graph and initiates bounded BFS path exploration up to 8 hops.
              </div>

              <div className="flex justify-end gap-2.5 pt-2">
                <button
                  type="button"
                  onClick={() => setIntakeOpen(false)}
                  className="px-3 py-1.5 rounded border border-[#2B2B2E] text-[#8A93A3]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating || !newWallet}
                  className="px-4 py-1.5 rounded bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-semibold disabled:opacity-50 transition-colors"
                >
                  {creating ? "Tracing Graph…" : "Begin Trace Engine"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
