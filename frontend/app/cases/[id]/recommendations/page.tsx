import { mockApiClient } from "@/lib/api/client";
import RecommendationsClient from "./RecommendationsClient";

interface RecommendationsPageProps {
  params: Promise<{
    id: string;
  }>;
}

export default async function RecommendationsPage({ params }: RecommendationsPageProps) {
  const { id } = await params;
  const recommendation = await mockApiClient.getRecommendation(id);

  return (
    <RecommendationsClient
      initialRecommendation={recommendation}
      caseId={id}
    />
  );
}
