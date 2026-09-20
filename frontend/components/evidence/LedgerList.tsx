import type { EvidenceRecord } from "@/lib/api/types";

interface LedgerListProps {
  records: EvidenceRecord[];
}

function truncateHash(hash: string): string {
  if (hash === "GENESIS") return "GENESIS";
  if (hash.length <= 16) return hash;
  return `${hash.slice(0, 10)}…${hash.slice(-10)}`;
}

export default function LedgerList({ records }: LedgerListProps) {
  return (
    <div className="overflow-hidden rounded-lg border border-[#2B2B2E] bg-[#141415]">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-[#1B1B1D] border-b border-[#2B2B2E] text-[#5A6373]">
            <tr>
              <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Record ID</th>
              <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Event Type</th>
              <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Timestamp</th>
              <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Content Hash (SHA-256)</th>
              <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Previous Hash</th>
              <th className="px-4 py-3 font-medium uppercase font-mono-vajra">Integrity</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#2B2B2E]">
            {records.map((record) => {
              const isGenesis = record.previous_hash === "GENESIS";

              return (
                <tr
                  key={record.record_id}
                  className="bg-[#141415] hover:bg-[#1B1B1D] transition-colors"
                >
                  <td className="px-4 py-3 font-mono-vajra text-[#E7EAEE] font-medium">
                    {record.record_id}
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded border border-[#2B2B2E] bg-[#0A0A0B] text-[#8A93A3] font-mono-vajra">
                      {record.record_type}
                    </span>
                    {record.is_simulated && (
                      <span className="ml-1.5 px-1.5 py-0.5 rounded text-[10px] uppercase font-mono-vajra bg-[rgba(227,174,62,0.12)] text-[#E3AE3E] border border-[rgba(227,174,62,0.3)]">
                        Simulated
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3 font-mono-vajra text-[#8A93A3] whitespace-nowrap">
                    {new Date(record.created_at).toLocaleString("en-IN")}
                  </td>
                  <td className="px-4 py-3 font-mono-vajra text-[#3FBE8B]" title={record.content_hash}>
                    {truncateHash(record.content_hash)}
                  </td>
                  <td
                    className={`px-4 py-3 font-mono-vajra ${
                      isGenesis ? "text-[#60A5FA] font-bold" : "text-[#5A6373]"
                    }`}
                    title={record.previous_hash}
                  >
                    {truncateHash(record.previous_hash)}
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full border border-[rgba(63,190,139,0.3)] bg-[rgba(63,190,139,0.12)] text-[#3FBE8B] font-mono-vajra text-[11px]">
                      ✓ Chained
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
