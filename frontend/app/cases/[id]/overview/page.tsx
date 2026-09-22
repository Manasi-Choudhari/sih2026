import { mockApiClient } from "@/lib/api/client";
import OverviewContent from "./OverviewContent";

interface CaseOverviewPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function CaseOverviewPage({ params }: CaseOverviewPageProps) {
  const { id } = await params;

  const [
    summary,
    graph,
    attribution,
    atlas,
    evidence,
    recommendation,
    auditTrail,
  ] = await Promise.all([
    mockApiClient.getCaseOverview(id),
    mockApiClient.getGraph(id),
    mockApiClient.getAttribution(id),
    mockApiClient.getAtlas(id),
    mockApiClient.getEvidenceLedger(id),
    mockApiClient.getRecommendation(id),
    mockApiClient.getAuditTrail(id),
  ]);

  return (
    <OverviewContent
      summary={summary}
      graph={graph}
      attribution={attribution}
      atlas={atlas}
      evidence={evidence}
      recommendation={recommendation}
      auditTrail={auditTrail}
    />
  );
}
