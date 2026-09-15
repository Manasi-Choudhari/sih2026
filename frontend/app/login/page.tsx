"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, User, KeyRound } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<"investigator" | "supervisor" | "admin">("investigator");
  const [username, setUsername] = useState("inv_sharma");
  const [password, setPassword] = useState("••••••••");
  const [loading, setLoading] = useState(false);

  function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      router.push("/queue");
    }, 600);
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="w-full max-w-md rounded-2xl border border-[#2B2B2E] bg-[#141415] p-8 shadow-2xl space-y-6 relative overflow-hidden">
        {/* Accent Bar */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#49C7BE] via-[#E3AE3E] to-[#3FBE8B]" />

        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2.5">
            <span className="w-5 h-5 rounded-[4px] trace-gradient-bg shadow-[0_0_10px_rgba(73,199,190,0.5)]" />
            <span className="font-serif-vajra text-2xl font-bold tracking-wider text-[#E7EAEE]">
              VAJRA
            </span>
          </div>
          <p className="text-xs text-[#8A93A3]">
            Crypto Fraud Attribution & Law Enforcement Terminal
          </p>
          <p className="font-mono-vajra text-[11px] text-[#5A6373]">
            SIH 26183 · CERT-In / NCRP Compliant
          </p>
        </div>

        {/* Role Selector Pill Tabs */}
        <div className="grid grid-cols-3 gap-1.5 p-1 rounded-lg bg-[#0A0A0B] border border-[#2B2B2E] text-xs">
          {(["investigator", "supervisor", "admin"] as const).map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => {
                setRole(r);
                setUsername(r === "supervisor" ? "sup_verma" : r === "admin" ? "admin_delhi" : "inv_sharma");
              }}
              className={`py-1.5 rounded text-center capitalize font-medium transition-all ${
                role === r
                  ? "bg-[#1B1B1D] text-[#49C7BE] shadow border border-[#2B2B2E]"
                  : "text-[#8A93A3] hover:text-[#E7EAEE]"
              }`}
            >
              {r}
            </button>
          ))}
        </div>

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-4 text-xs">
          <div className="space-y-1.5">
            <label className="block text-[#8A93A3] font-medium">User Identifier</label>
            <div className="relative">
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md px-3.5 py-2.5 pl-9 text-xs font-mono-vajra text-[#E7EAEE] focus:outline-none focus:border-[#49C7BE]"
              />
              <User className="absolute left-3 top-2.5 h-4 w-4 text-[#5A6373]" />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="block text-[#8A93A3] font-medium">Authentication Token / Key</label>
            <div className="relative">
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md px-3.5 py-2.5 pl-9 text-xs font-mono-vajra text-[#E7EAEE] focus:outline-none focus:border-[#49C7BE]"
              />
              <Lock className="absolute left-3 top-2.5 h-4 w-4 text-[#5A6373]" />
            </div>
          </div>

          <div className="p-3 rounded-lg bg-[#1B1B1D] border border-[#2B2B2E] space-y-1 text-[11px] text-[#8A93A3]">
            <p className="flex items-center gap-1.5 text-[#E7EAEE] font-medium">
              <KeyRound className="h-3.5 w-3.5 text-[#E3AE3E]" />
              Role Tier Capabilities:
            </p>
            <p>
              {role === "investigator"
                ? "Can query blockchain traces, run graph BFS, and propose VASP notices."
                : role === "supervisor"
                ? "Authorized to dual-sign and release Section 91 CrPC freeze notices."
                : "Full tenant administration and cryptographic audit key management."}
            </p>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 rounded-md trace-gradient-bg text-[#08201E] text-xs font-bold uppercase tracking-wider hover:opacity-90 transition-opacity shadow-[0_0_15px_rgba(73,199,190,0.3)] disabled:opacity-50"
          >
            {loading ? "Authenticating Session…" : "Enter Investigation Console"}
          </button>
        </form>

        <p className="text-center text-[10.5px] text-[#5A6373]">
          Authorized government law enforcement and cyber-crime cell personnel only.
        </p>
      </div>
    </div>
  );
}
