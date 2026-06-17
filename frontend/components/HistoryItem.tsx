import type { ClaimSummary } from "@/lib/types";
import { getIntentLabel, getStatusLabel } from "@/lib/labels";
import { VerdictBadge } from "@/components/VerdictBadge";
import { cn } from "@/lib/utils";

interface HistoryItemProps {
  claim: ClaimSummary;
  isActive?: boolean;
  onClick?: () => void;
}

export function HistoryItem({ claim, isActive, onClick }: HistoryItemProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full text-left px-3 py-3 rounded-md flex flex-col gap-1.5 transition-colors",
        "hover:bg-muted/50 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
        isActive && "bg-muted/60 ring-1 ring-primary/30",
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-xs text-primary truncate">
          {claim.claim_id}
        </span>
        {claim.final_verdict ? (
          <VerdictBadge verdict={claim.final_verdict} />
        ) : (
          <span className="font-mono text-xs text-muted-foreground">
            {getStatusLabel(claim.status)}
          </span>
        )}
      </div>
      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground truncate">
          {getIntentLabel(claim.intent_label)}
        </span>
      </div>
      <span className="font-mono text-xs text-muted-foreground/60">
        {new Date(claim.received_at).toLocaleDateString("es")}
      </span>
    </button>
  );
}
