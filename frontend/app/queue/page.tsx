import { mockApiClient } from "@/lib/api/client";
import QueueView from "./QueueView";

export default async function QueuePage() {
  const cases = await mockApiClient.listCases();

  return <QueueView initialCases={cases} />;
}
