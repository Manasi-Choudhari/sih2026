"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  ShieldCheck,
  Building2,
  FileCheck2,
  Send,
  Layers,
  ArrowRight,
  RefreshCw,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import { mockApiClient } from "@/lib/api/client";

interface Presets {
  name: string;
  category: string;
  crypto_asset: "ETH" | "BTC" | "USDT";
  crypto_amount: number;
  reported_loss_inr: number;
  suspect_wallet: string;
  victim_wallet: string;
  tx_hash: string;
  police_station: string;
  description: string;
}

const PRESETS: Record<string, Presets> = {
  scenario_1: {
    name: "Phishing / Seed Drain (Direct Binance 14 VASP)",
    category: "Phishing / Seed Drain",
    crypto_asset: "ETH",
    crypto_amount: 2.5,
    reported_loss_inr: 650000,
    suspect_wallet: "0x71C67930752b516538b1d97767F296aD55836882",
    victim_wallet: "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    tx_hash: "0xd81ea91807e318f5c50040524799cec1174a284266e43b2247ac58976d00195b",
    police_station: "Cyber Police Station New Delhi",
    description: "Complainant clicked a malicious Telegram staking link. Wallet private keys drained and transferred through intermediary hop into a Binance deposit address within 40 minutes.",
  },
  scenario_2: {
    name: "Bitcoin Peel Chain (Multi-Hop Layering)",
    category: "Investment / Ponzi Fraud",
    crypto_asset: "BTC",
    crypto_amount: 3.0,
    reported_loss_inr: 21500000,
    suspect_wallet: "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
    victim_wallet: "bc1q9victimfakeaddress00188924018241",
    tx_hash: "9b7d8c01f3e76a4b5d2c1e0f8a9b6c4d2e1f0a8b7c5d3e2f1a0b9c8d7e6f5a4b",
    police_station: "Cyber Crime Branch Mumbai",
    description: "Fake WhatsApp algorithmic trading group. Bitcoin peeled into small unspent change outputs to evade single-threshold exchange KYC traps.",
  },
  scenario_3: {
    name: "Cross-Chain Bridge Evasion (WBTC / BTC)",
    category: "Telegram Task Scam",
    crypto_asset: "BTC",
    crypto_amount: 1.2,
    reported_loss_inr: 8600000,
    suspect_wallet: "bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksns5",
    victim_wallet: "bc1qvictimtask9948281047192",
    tx_hash: "4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b",
    police_station: "Bengaluru City Cyber Cell",
    description: "Victim lured into high-yield ratings tasks. Funds bridged across decentralized liquidity pools before attempting off-ramp on an Indian exchange.",
  },
  scenario_4: {
    name: "Mixer Boundary (Tornado / Blender Obstruction)",
    category: "Ransomware / Extortion",
    crypto_asset: "BTC",
    crypto_amount: 4.0,
    reported_loss_inr: 28800000,
    suspect_wallet: "bc1q5d7rjq7g6rdk2yhzks9smlaqtedr4dekq08ge",
    victim_wallet: "bc1qextortvictimwallet11029",
    tx_hash: "1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d",
    police_station: "Cyberabad Police Station Hyderabad",
    description: "Enterprise extortion demanding cryptocurrency. Trace proceeds into zero-knowledge mixing protocol boundary with counter-hypothesis ambiguity.",
  },
};

export default function NcrpPortalPage() {
  const [activePreset, setActivePreset] = useState<string>("scenario_1");
  const [complainantName, setComplainantName] = useState("Vikramaditya Rao");
  const [contactMasked, setContactMasked] = useState("+91-98710****4");
  const [stateCode, setStateCode] = useState("DL");
  const [policeStation, setPoliceStation] = useState("Cyber Police Station New Delhi");
  
  const [category, setCategory] = useState("Phishing / Seed Drain");
  const [cryptoAsset, setCryptoAsset] = useState<"ETH" | "BTC" | "USDT">("ETH");
  const [cryptoAmount, setCryptoAmount] = useState("2.5");
  const [reportedLossInr, setReportedLossInr] = useState("650000");
  const [suspectWallet, setSuspectWallet] = useState("0x71C67930752b516538b1d97767F296aD55836882");
  const [victimWallet, setVictimWallet] = useState("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045");
  const [txHash, setTxHash] = useState("0xd81ea91807e318f5c50040524799cec1174a284266e43b2247ac58976d00195b");
  const [description, setDescription] = useState(PRESETS.scenario_1.description);

  const [submitting, setSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleNewManualComplaint = () => {
    setActivePreset("manual");
    setComplainantName("");
    setContactMasked("");
    setStateCode("DL");
    setPoliceStation("Cyber Police Station");
    setCategory("Investment / Ponzi Fraud");
    setCryptoAsset("ETH");
    setCryptoAmount("");
    setReportedLossInr("");
    setSuspectWallet("");
    setVictimWallet("");
    setTxHash("");
    setDescription("");
    setSubmissionResult(null);
    setErrorMsg(null);
  };

  const applyPreset = (key: string) => {
    const p = PRESETS[key];
    if (!p) return;
    setActivePreset(key);
    setCategory(p.category);
    setCryptoAsset(p.crypto_asset);
    setCryptoAmount(p.crypto_amount.toString());
    setReportedLossInr(p.reported_loss_inr.toString());
    setSuspectWallet(p.suspect_wallet);
    setVictimWallet(p.victim_wallet);
    setTxHash(p.tx_hash);
    setPoliceStation(p.police_station);
    setDescription(p.description);
    setSubmissionResult(null);
    setErrorMsg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!suspectWallet) {
      setErrorMsg("Please specify the suspect wallet address.");
      return;
    }

    setSubmitting(true);
    setErrorMsg(null);

    const ackNo = `2026/NCRP/${stateCode}/${Math.floor(100000 + Math.random() * 900000)}`;

    const payload = {
      event: "COMPLAINT_REGISTERED",
      portal_source: "NCRP_1930",
      complaint_ack_no: ackNo,
      state_code: stateCode,
      police_station: policeStation,
      filing_timestamp: new Date().toISOString(),
      victim_details: {
        name: complainantName,
        contact_masked: contactMasked,
        state: stateCode === "DL" ? "Delhi" : stateCode === "MH" ? "Maharashtra" : "Karnataka",
      },
      fraud_metadata: {
        category,
        sub_category: "Cryptocurrency Theft / Laundering",
        reported_loss_inr: parseFloat(reportedLossInr) || 500000,
        crypto_asset: cryptoAsset,
        crypto_amount: parseFloat(cryptoAmount) || 1.0,
        transaction_hash: txHash,
        suspect_wallet_address: suspectWallet,
        victim_wallet_address: victimWallet,
        description,
      },
    };

    try {
      const res = await mockApiClient.submitNcrpWebhook(payload);
      if (res && res.status) {
        setSubmissionResult(res);
      } else {
        // Fallback local acknowledgment if offline
        setSubmissionResult({
          status: "INGESTED_AND_TRIAGED",
          case_id: `case_${Math.random().toString(36).substring(2, 10)}`,
          complaint_ack_no: ackNo,
          hops_traced: 2,
          top_vasp: "Binance (Hot Wallet 14)",
          rule_risk_score: 0.85,
          attribution_confidence: 0.92,
          ml_probability: 0.81,
          simulation_mode: true,
          notice: "Simulated NCRP / 1930 Portal Integration (I4C / CFCFRMS compliant)",
        });
      }
    } catch (err: any) {
      setErrorMsg(err?.message || "Failed to dispatch complaint to VAJRA ingestion gateway.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      {/* Gov Official Header Banner */}
      <div className="rounded-xl border border-[#2B2B2E] bg-[#141415] overflow-hidden shadow-2xl">
        {/* Tricolor Accent Strip */}
        <div className="h-1.5 w-full flex">
          <div className="flex-1 bg-[#FF9933]" />
          <div className="flex-1 bg-[#FFFFFF]" />
          <div className="flex-1 bg-[#138808]" />
        </div>

        <div className="p-6 md:p-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            {/* Emblem / Badge representation */}
            <div className="w-14 h-14 rounded-lg bg-[#1B1B1D] border border-[#2B2B2E] flex flex-col items-center justify-center text-center p-1 shrink-0 shadow-inner">
              <Building2 className="h-6 w-6 text-[#E3AE3E]" />
              <span className="text-[9px] font-mono-vajra text-[#8A93A3] mt-0.5">I4C / MHA</span>
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono-vajra uppercase tracking-wider text-[#E3AE3E] font-semibold">
                  GOVERNMENT OF INDIA · MINISTRY OF HOME AFFAIRS
                </span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-[#E3AE3E]/15 border border-[#E3AE3E]/30 text-[#E3AE3E] font-medium">
                  SIMULATION / DEMO
                </span>
              </div>
              <h1 className="font-serif-vajra text-2xl md:text-3xl font-bold text-[#E7EAEE] mt-1">
                National Cybercrime Reporting Portal (NCRP)
              </h1>
              <p className="text-xs text-[#8A93A3] mt-1">
                Citizen Financial Cyber Fraud Reporting & Management System (CFCFRMS) · National Helpline 1930
              </p>
            </div>
          </div>

          <div className="flex flex-col items-start md:items-end gap-1.5 text-xs text-[#8A93A3] border-t md:border-t-0 md:border-l border-[#2B2B2E] pt-3 md:pt-0 md:pl-6">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#3B82F6]" />
              <span className="text-[#E7EAEE] font-mono-vajra font-medium">VAJRA API Gateway: ONLINE</span>
            </div>
            <p className="text-[11px] text-[#5A6373]">
              Direct Ingestion Endpoint: <code className="text-[#60A5FA]">/api/v1/external/ncrp/webhook</code>
            </p>
            <Link
              href="/queue"
              className="inline-flex items-center gap-1.5 text-xs text-[#60A5FA] hover:underline mt-1 font-medium"
            >
              <span>Switch to VAJRA Officer Queue</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Preset Selector */}
      <div className="rounded-xl border border-[#2B2B2E] bg-[#141415] p-5 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-[#3B82F6]" />
            <h2 className="text-sm font-semibold text-[#E7EAEE]">
              Investigation Lodging Mode & Typology Presets
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleNewManualComplaint}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md border text-xs font-semibold transition-all ${
                activePreset === "manual"
                  ? "border-[#2563EB] bg-[#2563EB] text-white"
                  : "border-[#3B82F6]/40 bg-[#3B82F6]/10 text-[#60A5FA] hover:bg-[#3B82F6]/20"
              }`}
            >
              <span>➕ New Complaint / Manual Entry</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2.5">
          {Object.entries(PRESETS).map(([key, p]) => {
            const isSelected = activePreset === key;
            return (
              <button
                key={key}
                type="button"
                onClick={() => applyPreset(key)}
                className={`text-left p-3 rounded-lg border transition-all ${
                  isSelected
                    ? "border-[#3B82F6] bg-[#1E3A8A]/25"
                    : "border-[#2B2B2E] bg-[#1B1B1D] hover:border-[#5A6373] text-[#8A93A3]"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono-vajra text-[11px] font-bold text-[#E7EAEE] uppercase">
                    {key.replace("_", " ")}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#0A0A0B] border border-[#2B2B2E] text-[#60A5FA] font-mono-vajra">
                    {p.crypto_asset}
                  </span>
                </div>
                <p className="text-xs font-medium text-[#E7EAEE] line-clamp-1">{p.name}</p>
                <p className="text-[10px] text-[#5A6373] mt-1 font-mono-vajra">
                  {p.crypto_amount} {p.crypto_asset} (₹{(p.reported_loss_inr / 100000).toFixed(1)}L)
                </p>
              </button>
            );
          })}

          {/* 5th Card: Manual Custom Filing */}
          <button
            type="button"
            onClick={handleNewManualComplaint}
            className={`text-left p-3 rounded-lg border transition-all ${
              activePreset === "manual"
                ? "border-[#3B82F6] bg-[#1E3A8A]/25 ring-1 ring-[#3B82F6]"
                : "border-dashed border-[#5A6373] bg-[#141415] hover:border-[#3B82F6] text-[#8A93A3]"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-mono-vajra text-[11px] font-bold text-[#60A5FA] uppercase">
                MANUAL
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#3B82F6]/20 text-[#60A5FA] font-mono-vajra">
                BLANK
              </span>
            </div>
            <p className="text-xs font-medium text-[#E7EAEE] line-clamp-1">➕ New Complaint</p>
            <p className="text-[10px] text-[#8A93A3] mt-1">
              Custom victim & suspect wallet
            </p>
          </button>
        </div>
      </div>

      {/* Submission Success Screen */}
      {submissionResult && (
        <div className="rounded-xl border border-[#3FBE8B]/40 bg-[#3FBE8B]/10 p-6 md:p-8 space-y-5 shadow-2xl animate-in fade-in duration-300">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#3FBE8B]/20 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[#3FBE8B]/20 flex items-center justify-center text-[#3FBE8B]">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <div>
                <h3 className="font-serif-vajra text-lg md:text-xl font-bold text-[#E7EAEE]">
                  Complaint Lodged & Triaged Successfully
                </h3>
                <p className="text-xs text-[#8A93A3]">
                  Acknowledgment Receipt Generated · Reverse Callback Dispatched to 1930 CFCFRMS
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => setSubmissionResult(null)}
                className="px-3 py-1.5 rounded border border-[#2B2B2E] bg-[#141415] text-xs text-[#8A93A3] hover:text-[#E7EAEE]"
              >
                File Another Complaint
              </button>
              <Link
                href={`/cases/${submissionResult.case_id}/overview`}
                className="flex items-center gap-2 px-4 py-1.5 rounded-md bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-semibold transition-colors"
              >
                <span>Open Case in VAJRA</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>

          {/* Official Acknowledgment Details Card */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-[#141415] border border-[#2B2B2E]">
              <span className="text-[10px] text-[#5A6373] uppercase font-mono-vajra">Complaint Ack No</span>
              <p className="text-sm font-bold text-[#60A5FA] font-mono-vajra mt-0.5">
                {submissionResult.complaint_ack_no}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-[#141415] border border-[#2B2B2E]">
              <span className="text-[10px] text-[#5A6373] uppercase font-mono-vajra">Assigned VAJRA ID</span>
              <p className="text-sm font-bold text-[#E7EAEE] font-mono-vajra mt-0.5">
                {submissionResult.case_id}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-[#141415] border border-[#2B2B2E]">
              <span className="text-[10px] text-[#5A6373] uppercase font-mono-vajra">Attributed Destination</span>
              <p className="text-sm font-bold text-[#E3AE3E] font-medium mt-0.5 truncate">
                {submissionResult.top_vasp || "Binance Hot Wallet"}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-[#141415] border border-[#2B2B2E]">
              <span className="text-[10px] text-[#5A6373] uppercase font-mono-vajra">Multi-Hop Path</span>
              <p className="text-sm font-bold text-[#3FBE8B] font-mono-vajra mt-0.5">
                {submissionResult.hops_traced || 2} Hops Traced
              </p>
            </div>
          </div>

          {/* Three-Number Confidence Framework */}
          <div className="p-4 rounded-lg bg-[#141415] border border-[#2B2B2E] space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[#E7EAEE] uppercase font-mono-vajra tracking-wider">
                Automated Zero-Second Attribution Assessment
              </span>
              <span className="text-[10px] text-[#5A6373] font-mono-vajra">Section 5 Integration Engine</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded bg-[#1B1B1D] border border-[#2B2B2E]">
                <div className="flex items-center justify-between text-[#8A93A3] text-[11px]">
                  <span>Rule Risk Score (Deterministic)</span>
                  <span className="font-mono-vajra text-[#E7EAEE]">
                    {((submissionResult.rule_risk_score || 0.72) * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-[#0A0A0B] h-1.5 rounded-full mt-2 overflow-hidden">
                  <div
                    className="bg-[#3FBE8B] h-full rounded-full"
                    style={{ width: `${(submissionResult.rule_risk_score || 0.72) * 100}%` }}
                  />
                </div>
              </div>

              <div className="p-3 rounded bg-[#1B1B1D] border border-[#2B2B2E]">
                <div className="flex items-center justify-between text-[#8A93A3] text-[11px]">
                  <span>Attribution Confidence</span>
                  <span className="font-mono-vajra text-[#60A5FA]">
                    {((submissionResult.attribution_confidence || 0.92) * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-[#0A0A0B] h-1.5 rounded-full mt-2 overflow-hidden">
                  <div
                    className="bg-[#2563EB] h-full rounded-full"
                    style={{ width: `${(submissionResult.attribution_confidence || 0.92) * 100}%` }}
                  />
                </div>
              </div>

              <div className="p-3 rounded bg-[#1B1B1D] border border-[#2B2B2E]">
                <div className="flex items-center justify-between text-[#8A93A3] text-[11px]">
                  <span>ML Anomaly Probability</span>
                  <span className="font-mono-vajra text-[#E3AE3E]">
                    {((submissionResult.ml_probability || 0.82) * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-[#0A0A0B] h-1.5 rounded-full mt-2 overflow-hidden">
                  <div
                    className="bg-[#E3AE3E] h-full rounded-full"
                    style={{ width: `${(submissionResult.ml_probability || 0.82) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-[#2B2B2E] text-xs">
              <span className="text-[#8A93A3]">
                Section 91 CrPC freeze notice auto-drafted and queued for supervisor authorization.
              </span>
              <Link
                href="/queue"
                className="text-[#60A5FA] hover:underline font-medium inline-flex items-center gap-1"
              >
                <span>View All Complaints in Queue</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Main Complaint Filing Form */}
      <form onSubmit={handleSubmit} className="rounded-xl border border-[#2B2B2E] bg-[#141415] p-6 md:p-8 space-y-6">
        <div className="border-b border-[#2B2B2E] pb-4">
          <h2 className="font-serif-vajra text-lg font-bold text-[#E7EAEE]">
            Lodge Citizen Cryptocurrency Cyber Fraud Incident
          </h2>
          <p className="text-xs text-[#8A93A3] mt-0.5">
            Submit suspect wallet coordinates. The VAJRA engine will automatically trace transaction hops, query known VASP boundaries, and synchronize attribution findings.
          </p>
        </div>

        {errorMsg && (
          <div className="p-3.5 rounded-lg border border-[#C56A4B]/40 bg-[#C56A4B]/10 text-xs text-[#C56A4B] flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Manual Mode Notification Banner */}
        {activePreset === "manual" && (
          <div className="p-3.5 rounded-lg border border-[#3B82F6]/30 bg-[#3B82F6]/10 text-xs text-[#E7EAEE] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <FileCheck2 className="h-4 w-4 text-[#3B82F6] shrink-0" />
              <span>
                <strong>Manual Complaint Filing Mode Active:</strong> Form fields are cleared. Enter custom suspect and victim wallet coordinates. For Ethereum addresses, VAJRA will utilize the configured <code className="text-[#60A5FA]">EXPLORER_API_KEY_ETH</code> to fetch live on-chain transactions and construct the investigation graph.
              </span>
            </div>
            <button
              type="button"
              onClick={() => applyPreset("scenario_1")}
              className="text-[11px] text-[#60A5FA] hover:underline font-mono-vajra shrink-0"
            >
              Load Preset S1
            </button>
          </div>
        )}

        {/* Section 1: Complainant Details */}
        <div className="space-y-4">
          <h3 className="text-xs font-semibold uppercase tracking-wider font-mono-vajra text-[#60A5FA]">
            Part 1: Complainant & Jurisdictional Police Station
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-[#8A93A3] mb-1.5 font-medium">Complainant / Citizen Name</label>
              <input
                type="text"
                required
                placeholder="e.g. Vikramaditya Rao or Anonymous Citizen"
                value={complainantName}
                onChange={(e) => setComplainantName(e.target.value)}
                className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md p-2.5 text-xs text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>

            <div>
              <label className="block text-[#8A93A3] mb-1.5 font-medium">Contact Number (Masked)</label>
              <input
                type="text"
                required
                placeholder="e.g. +91-98710****4"
                value={contactMasked}
                onChange={(e) => setContactMasked(e.target.value)}
                className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md p-2.5 text-xs font-mono-vajra text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>

            <div>
              <label className="block text-[#8A93A3] mb-1.5 font-medium">Cyber Police Station / Unit</label>
              <input
                type="text"
                required
                placeholder="e.g. Cyber Crime Unit Delhi / Mumbai / Bengaluru"
                value={policeStation}
                onChange={(e) => setPoliceStation(e.target.value)}
                className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md p-2.5 text-xs text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Incident Modus Operandi */}
        <div className="space-y-4 pt-4 border-t border-[#2B2B2E]">
          <h3 className="text-xs font-semibold uppercase tracking-wider font-mono-vajra text-[#60A5FA]">
            Part 2: Cyber Fraud Classification
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-[#8A93A3] mb-1.5 font-medium">Fraud Typology / Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md p-2.5 text-xs text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
              >
                <option value="Phishing / Seed Drain">Phishing / Seed Drain</option>
                <option value="Investment / Ponzi Fraud">Investment / Ponzi Fraud</option>
                <option value="Telegram Task Scam">Telegram Task Scam</option>
                <option value="Ransomware / Extortion">Ransomware / Extortion</option>
                <option value="Fake Crypto Exchange">Fake Crypto Exchange</option>
                <option value="P2P Escrow Fraud">P2P Escrow Fraud</option>
              </select>
            </div>

            <div>
              <label className="block text-[#8A93A3] mb-1.5 font-medium">Reported Financial Loss (INR Equivalent)</label>
              <input
                type="number"
                required
                placeholder="e.g. 650000"
                value={reportedLossInr}
                onChange={(e) => setReportedLossInr(e.target.value)}
                className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md p-2.5 text-xs font-mono-vajra text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>
          </div>

          <div>
            <label className="block text-[#8A93A3] mb-1.5 font-medium">Incident Brief / Modus Operandi</label>
            <textarea
              rows={2}
              placeholder="Provide context regarding fraud lure, communications, or deceptive links..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md p-2.5 text-xs text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
            />
          </div>
        </div>

        {/* Section 3: Blockchain Evidence Coordinates */}
        <div className="space-y-4 pt-4 border-t border-[#2B2B2E]">
          <h3 className="text-xs font-semibold uppercase tracking-wider font-mono-vajra text-[#60A5FA]">
            Part 3: Blockchain Coordinates (Auto-Traced by VAJRA Engine)
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-[#8A93A3] mb-1.5 font-medium">Crypto Asset Protocol</label>
              <select
                value={cryptoAsset}
                onChange={(e) => setCryptoAsset(e.target.value as any)}
                className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md p-2.5 text-xs text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
              >
                <option value="ETH">Ethereum (ETH / ERC-20)</option>
                <option value="BTC">Bitcoin (BTC / UTXO)</option>
                <option value="USDT">Tether USD (USDT)</option>
              </select>
            </div>

            <div>
              <label className="block text-[#8A93A3] mb-1.5 font-medium">Crypto Loss Quantity</label>
              <input
                type="number"
                step="0.0001"
                required
                placeholder="e.g. 2.5"
                value={cryptoAmount}
                onChange={(e) => setCryptoAmount(e.target.value)}
                className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md p-2.5 text-xs font-mono-vajra text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>
          </div>

          <div>
            <label className="block text-[#8A93A3] mb-1.5 font-medium">
              Suspect / Beneficiary Wallet Address <span className="text-[#E3AE3E]">*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. 0x71C67930752b516538b1d97767F296aD55836882 or any Ethereum/Bitcoin address"
              value={suspectWallet}
              onChange={(e) => setSuspectWallet(e.target.value)}
              className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md p-2.5 text-xs font-mono-vajra text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-[#8A93A3] mb-1.5 font-medium">Victim Source Wallet (Optional)</label>
              <input
                type="text"
                placeholder="e.g. 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
                value={victimWallet}
                onChange={(e) => setVictimWallet(e.target.value)}
                className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md p-2.5 text-xs font-mono-vajra text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>

            <div>
              <label className="block text-[#8A93A3] mb-1.5 font-medium">Initial Transfer Transaction Hash (Optional)</label>
              <input
                type="text"
                placeholder="e.g. 0xd81ea91807e318f5c50040524799cec1174a284266e43b2247ac58976d00195b"
                value={txHash}
                onChange={(e) => setTxHash(e.target.value)}
                className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md p-2.5 text-xs font-mono-vajra text-[#E7EAEE] focus:outline-none focus:border-[#3B82F6]"
              />
            </div>
          </div>
        </div>

        {/* Form Submission Action */}
        <div className="pt-4 border-t border-[#2B2B2E] flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-xs text-[#8A93A3]">
            <FileCheck2 className="h-4 w-4 text-[#3FBE8B]" />
            <span>Standardized Section 5 Webhook Integration with 1930 / I4C National Gateway</span>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-2.5 rounded-md bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs font-bold transition-colors disabled:opacity-50"
          >
            {submitting ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Ingesting & Running Zero-Second Triage…</span>
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                <span>Lodge Complaint & Auto-Triage on VAJRA</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
