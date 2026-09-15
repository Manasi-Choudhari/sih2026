import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { mockApiClient } from "@/lib/api/client";
import VerifyButton from "@/components/evidence/VerifyButton";
import LedgerList from "@/components/evidence/LedgerList";

interface EvidencePageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function EvidencePage({ params }: EvidencePageProps) {
  const { id } = await params;
  const records = await mockApiClient.getEvidenceLedger(id);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header className="flex items-center justify-between border-b border-[#2B2B2E] pb-4">
        <div className="flex items-center gap-3">
          <Link
            href={`/cases/${id}/overview`}
            className="p-1.5 rounded-md border border-[#2B2B2E] bg-[#141415] hover:bg-[#1B1B1D] text-[#8A93A3] hover:text-[#E7EAEE]"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <h1 className="font-serif-vajra text-xl font-bold text-[#E7EAEE]">
              Cryptographic Evidence Ledger — {id}
            </h1>
            <p className="text-xs text-[#5A6373] font-mono-vajra">
              {records.length} append-only records · Hash-chained from GENESIS block
            </p>
          </div>
        </div>
      </header>

      <section className="rounded-lg border border-[#2B2B2E] bg-[#141415] p-5 space-y-3">
        <p className="text-xs font-semibold uppercase tracking-wider text-[#5A6373]">
          Chain Integrity Verification Gate
        </p>
        <VerifyButton caseId={id} />
      </section>

      <LedgerList records={records} />
    </div>
  );
}