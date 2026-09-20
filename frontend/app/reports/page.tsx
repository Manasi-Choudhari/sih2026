import { redirect } from "next/navigation";
import { mockApiClient } from "@/lib/api/client";

/**
 * Top-level reports redirect: sends visitor to the first active case report.
 */
export default async function ReportsRootPage() {
  const cases = await mockApiClient.listCases();
  const targetId = cases[0]?.case_id || "case_s1";
  redirect(`/cases/${targetId}/report`);
}
