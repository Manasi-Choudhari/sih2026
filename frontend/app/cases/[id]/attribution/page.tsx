import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { mockApiClient } from "@/lib/api/client";
import AttributionCard from "@/components/attribution/AttributionCard";
import PatternBadges from "@/components/attribution/PatternBadge";

interface AttributionPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function AttributionPage({ params }: AttributionPageProps) {
  const { id } = await params;
  const attribution = await mockApiClient.getAttribution(id);

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
              Evidence-Tiered VASP Attribution — {id}
            </h1>
            <p className="text-xs text-[#5A6373]">
              {attribution.candidates.length} candidate{attribution.candidates.length === 1 ? "" : "s"} across independently traced branches
            </p>
          </div>
        </div>
      </header>

      <section className="space-y-2.5">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-[#5A6373]">
          Matched Topological Patterns
        </h2>
        <PatternBadges patterns={attribution.patterns} />
      </section>

      <section className="space-y-4">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-[#5A6373]">
          Attribution Candidates by Branch
        </h2>
        {attribution.candidates.map((candidate) => (
          <AttributionCard key={candidate.candidate_id} candidate={candidate} />
        ))}
      </section>
    </div>
  );
}