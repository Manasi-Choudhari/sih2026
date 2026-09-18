import type { Metadata } from "next";
import Link from "next/link";
import {
  Inbox,
  Clock,
  FileText,
  ShieldAlert,
} from "lucide-react";
import { IBM_Plex_Serif, IBM_Plex_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import { mockApiClient } from "@/lib/api/client";

const ibmPlexSerif = IBM_Plex_Serif({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  variable: "--font-ibm-plex-serif",
  display: "swap",
});

const ibmPlexSans = IBM_Plex_Sans({
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  variable: "--font-ibm-plex-sans",
  display: "swap",
});

const ibmPlexMono = IBM_Plex_Mono({
  weight: ["400", "500"],
  subsets: ["latin"],
  variable: "--font-ibm-plex-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "VAJRA — Real-Time Crypto Fraud Attribution Console",
  description: "Evidence-tiered VASP attribution and cryptographic tamper-evident ledger (SIH 26183)",
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const openCases = await mockApiClient.listCases();
  const firstCaseId = openCases[0]?.case_id;

  const workspaceNav = [
    { href: "/queue", label: "Case queue", icon: Inbox },
    { href: "/queue", label: "Recent activity", icon: Clock },
    { href: firstCaseId ? `/cases/${firstCaseId}/report` : "/queue", label: "Reports", icon: FileText },
  ] as const;

  return (
    <html
      lang="en"
      className={`${ibmPlexSerif.variable} ${ibmPlexSans.variable} ${ibmPlexMono.variable}`}
    >
      <body className="min-h-screen bg-[#0A0A0B] text-[#E7EAEE] font-sans antialiased">
        {/* Sticky Simulated Banner per shared contract */}
        <div
          role="alert"
          className="sticky top-0 z-50 flex items-center justify-center gap-2 border-b border-[#2B2B2E] bg-[#141415] px-4 py-1.5 text-center text-xs font-medium text-[#8A93A3]"
        >
          <ShieldAlert className="h-3.5 w-3.5 text-[#E3AE3E]" strokeWidth={2.2} />
          <span>
            <strong className="text-[#E7EAEE]">SIMULATED NCRP / SAHYOG DATA ACTIVE</strong> — Demo mode for competition evaluation. No external enforcement triggers are live.
          </span>
        </div>

        {/* Shell */}
        <div className="flex flex-col min-h-[calc(100vh-2rem)]">
          {/* Top Bar matching reference */}
          <header className="h-14 border-b border-[#2B2B2E] bg-[#141415] px-6 flex items-center justify-between gap-6 shrink-0">
            <div className="flex items-center gap-8">
              <Link href="/queue" className="flex items-center gap-2.5">
                <span className="w-5 h-5 rounded-[4px] trace-gradient-bg flex-shrink-0 shadow-[0_0_8px_rgba(73,199,190,0.4)]" />
                <span className="font-serif-vajra font-semibold text-lg tracking-wide text-[#E7EAEE]">
                  VAJRA
                </span>
                <span className="text-[11px] font-mono-vajra px-1.5 py-0.5 rounded border border-[#2B2B2E] text-[#8A93A3] bg-[#0A0A0B]">
                  SIH 26183
                </span>
              </Link>

              {/* Global search input */}
              <div className="w-80 md:w-96 relative">
                <input
                  type="text"
                  placeholder="Search wallet address, case ID, or VASP name"
                  className="w-full bg-[#0A0A0B] border border-[#2B2B2E] rounded-md px-3 py-1.5 text-xs text-[#E7EAEE] placeholder-[#5A6373] focus:outline-none focus:border-[#49C7BE] transition-colors"
                />
              </div>
            </div>

            {/* Topbar right items */}
            <div className="flex items-center gap-4 text-xs text-[#8A93A3]">
              <Link
                href="/login"
                className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-[#2B2B2E] text-[#8A93A3] hover:border-[#49C7BE] hover:text-[#E7EAEE] transition-colors"
                title="Switch Role / Login"
              >
                <span className="w-2 h-2 rounded-full bg-[#3FBE8B]" />
                Role: Investigator
              </Link>
              <Link
                href="/login"
                title="R. Sharma (Senior Cyber Analyst) — Click to Switch User"
                className="w-7 h-7 rounded-full bg-[#1B1B1D] border border-[#2B2B2E] hover:border-[#49C7BE] flex items-center justify-center font-mono-vajra text-xs text-[#E7EAEE] font-medium transition-colors"
              >
                RS
              </Link>
            </div>
          </header>

          {/* Main Layout (Sidebar + Content) */}
          <div className="flex flex-1 overflow-hidden">
            {/* Sidebar matching reference */}
            <aside className="w-64 shrink-0 border-r border-[#2B2B2E] bg-[#141415] flex flex-col justify-between py-4 px-3 overflow-y-auto">
              <div className="space-y-5">
                {/* Workspace Nav */}
                <div>
                  <p className="px-2 mb-1.5 text-[11px] font-medium uppercase tracking-wider text-[#5A6373]">
                    Workspace
                  </p>
                  <nav className="space-y-0.5">
                    {workspaceNav.map(({ href, label, icon: Icon }) => (
                      <Link
                        key={label}
                        href={href}
                        className="flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-[13px] text-[#8A93A3] hover:text-[#E7EAEE] hover:bg-[#1B1B1D] transition-colors"
                      >
                        <Icon className="h-4 w-4 opacity-80" strokeWidth={2} />
                        <span>{label}</span>
                      </Link>
                    ))}
                  </nav>
                </div>

                {/* Open Cases */}
                <div>
                  <div className="px-2 mb-1.5 flex items-center justify-between">
                    <p className="text-[11px] font-medium uppercase tracking-wider text-[#5A6373]">
                      Open Cases · {openCases.length}
                    </p>
                    <Link
                      href="/queue"
                      className="text-[10px] text-[#49C7BE] hover:underline"
                    >
                      View All
                    </Link>
                  </div>

                  <div className="space-y-1">
                    {openCases.length === 0 ? (
                      <div className="px-2.5 py-4 text-center border border-dashed border-[#2B2B2E] rounded-md space-y-1">
                        <p className="text-xs text-[#8A93A3] font-medium">No open cases</p>
                        <p className="text-[10px] text-[#5A6373]">Backend unseeded or offline</p>
                      </div>
                    ) : (
                      openCases.map((c) => {
                        const dotColor =
                          c.tier_dot === "Strong"
                            ? "#3FBE8B"
                            : c.tier_dot === "Medium"
                            ? "#E3AE3E"
                            : c.tier_dot === "Weak"
                            ? "#C56A4B"
                            : "#5C6675";

                        return (
                          <Link
                            key={c.case_id}
                            href={`/cases/${c.case_id}/overview`}
                            className="group flex flex-col gap-0.5 px-2.5 py-2 rounded-md border border-transparent hover:border-[#2B2B2E] hover:bg-[#1B1B1D] transition-all"
                          >
                            <div className="flex items-center justify-between text-xs font-mono-vajra text-[#8A93A3] group-hover:text-[#E7EAEE]">
                              <span>{c.case_id}</span>
                              <span
                                className="w-1.5 h-1.5 rounded-full"
                                style={{ backgroundColor: dotColor }}
                              />
                            </div>
                            <div className="flex items-center justify-between text-[11px] text-[#5A6373]">
                              <span className="truncate pr-1">{c.name}</span>
                              <span className="font-mono-vajra shrink-0 text-[#8A93A3]">
                                {c.amount_inr}
                              </span>
                            </div>
                          </Link>
                        );
                      })
                    )}
                  </div>
                </div>
              </div>

              {/* Sidebar Footer */}
              <div className="pt-4 border-t border-[#2B2B2E] px-2 space-y-1 text-[11px] text-[#5A6373]">
                <div className="flex items-center justify-between">
                  <span>Engine status:</span>
                  <span className={openCases.length > 0 ? "text-[#3FBE8B] font-mono-vajra" : "text-[#8A93A3] font-mono-vajra"}>
                    {openCases.length > 0 ? "ONLINE" : "STANDBY"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Model:</span>
                  <span className="text-[#8A93A3] font-mono-vajra">XGBoost GPU</span>
                </div>
              </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 overflow-y-auto bg-[#0A0A0B] p-6 lg:p-8">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
