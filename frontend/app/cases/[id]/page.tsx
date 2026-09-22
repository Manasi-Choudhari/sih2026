import { redirect } from "next/navigation";

interface CaseParamProps {
  params: Promise<{ id: string }>;
}

export default async function CaseIndexPage({ params }: CaseParamProps) {
  const { id } = await params;
  redirect(`/cases/${encodeURIComponent(id)}/overview`);
}
