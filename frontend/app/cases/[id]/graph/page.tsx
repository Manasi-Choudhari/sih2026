import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { mockApiClient } from "@/lib/api/client";
import GraphView from "@/components/graph/GraphView";

interface GraphPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function GraphPage({ params }: GraphPageProps) {
  const { id } = await params;
  const graphData = await mockApiClient.getGraph(id);

  return (
    <div className="max-w-7xl mx-auto space-y-4 h-[calc(100vh-7rem)] flex flex-col">
      <div className="flex items-center justify-between border-b border-[#2B2B2E] pb-3 shrink-0">
        <div className="flex items-center gap-3">
          <Link
            href={`/cases/${id}/overview`}
            className="p-1.5 rounded-md border border-[#2B2B2E] bg-[#141415] hover:bg-[#1B1B1D] text-[#8A93A3] hover:text-[#E7EAEE]"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <h1 className="font-serif-vajra text-lg font-bold text-[#E7EAEE]">
              Expanded Transaction Graph — {id}
            </h1>
            <p className="text-xs text-[#5A6373] font-mono-vajra">
              {graphData.nodes.length} nodes · {graphData.edges.length} hops · Termination: {graphData.termination_reason ?? "known_service_boundary"}
            </p>
          </div>
        </div>

        <div className="text-xs text-[#8A93A3] font-mono-vajra">
          Bounded priority BFS · Max depth 8
        </div>
      </div>

      <div className="flex-1 w-full min-h-0">
        <GraphView graphData={graphData} compact={false} />
      </div>
    </div>
  );
}
