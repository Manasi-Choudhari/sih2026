import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { mockApiClient } from "@/lib/api/client";
import AtlasPanel from "@/components/atlas/AtlasPanel";

interface AtlasPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function AtlasPage({ params }: AtlasPageProps) {
  const { id } = await params;
  const [summary, atlas] = await Promise.all([
    mockApiClient.getCaseOverview(id),
    mockApiClient.getAtlas(id),
  ]);

  const leadingCandidateName = summary.leading_candidate?.vasp_name ?? null;

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
              ATLAS: Adversarial Threat & Logic Assessment System — {id}
            </h1>
            <p className="text-xs text-[#5A6373]">
              Automated adversarial testing designed to disprove attribution before formal legal notices are issued
            </p>
          </div>
        </div>
      </header>

      <AtlasPanel atlas={atlas} leadingCandidateName={leadingCandidateName} />
    </div>
  );
}
