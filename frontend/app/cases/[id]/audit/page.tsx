import { mockApiClient } from "@/lib/api/client";
import AuditView from "./AuditView";

interface AuditPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function AuditPage({ params }: AuditPageProps) {
  const { id } = await params;
  const auditEvents = await mockApiClient.getAuditTrail(id);

  return <AuditView initialEvents={auditEvents} caseId={id} />;
}
