import { redirect } from "next/navigation";
import { mockApiClient } from "@/lib/api/client";

/**
 * Top-level report redirect: sends visitor to the first active case report,
 * or back to the queue if no case exists.
 */
export default async function ReportRootPage() {
  const cases = await mockApiClient.listCases();
  const targetId = cases[0]?.case_id || "case_s1";
  redirect(`/cases/${targetId}/report`);
}
