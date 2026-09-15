import { ShieldCheck, ShieldHalf, ShieldAlert, HelpCircle } from "lucide-react";
import type { EvidenceTier } from "@/lib/api/types";

interface EvidenceTierBadgeProps {
  tier: EvidenceTier;
  className?: string;
}

const TIER_CONFIG: Record<
  EvidenceTier,
  { icon: typeof ShieldCheck; classes: string; label: string }
> = {
  Strong: {
    icon: ShieldCheck,
    classes: "border-[rgba(63,190,139,0.3)] bg-[rgba(63,190,139,0.12)] text-[#3FBE8B]",
    label: "Strong",
  },
  Medium: {
    icon: ShieldHalf,
    classes: "border-[rgba(227,174,62,0.3)] bg-[rgba(227,174,62,0.12)] text-[#E3AE3E]",
    label: "Medium",
  },
  Weak: {
    icon: ShieldAlert,
    classes: "border-[rgba(197,106,75,0.3)] bg-[rgba(197,106,75,0.12)] text-[#C56A4B]",
    label: "Weak",
  },
  Unknown: {
    icon: HelpCircle,
    classes: "border-[rgba(92,102,117,0.3)] bg-[rgba(92,102,117,0.15)] text-[#5C6675]",
    label: "Unknown",
  },
};

export default function EvidenceTierBadge({ tier, className = "" }: EvidenceTierBadgeProps) {
  const config = TIER_CONFIG[tier] ?? TIER_CONFIG.Unknown;
  const Icon = config.icon;

  return (
    <span
      className={[
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium font-mono-vajra",
        config.classes,
        className,
      ].join(" ")}
    >
      <Icon className="h-3 w-3 shrink-0" strokeWidth={2.2} />
      <span>{config.label} tier</span>
    </span>
  );
}
