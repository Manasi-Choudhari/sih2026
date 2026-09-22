import { mockApiClient } from "@/lib/api/client";
import ReportView from "./ReportView";

interface ReportPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function ReportPage({ params }: ReportPageProps) {
  const { id } = await params;

  const [summary, evidence, reportMeta] = await Promise.all([
    mockApiClient.getCaseOverview(id),
    mockApiClient.getEvidenceLedger(id),
    mockApiClient.getReport(id),
  ]);

  return (
    <ReportView
      summary={summary}
      evidence={evidence}
      reportMeta={reportMeta}
    />
  );
}
