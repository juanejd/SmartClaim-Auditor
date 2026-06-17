"use client";

import { Trash2 } from "lucide-react";
import type { ClaimSummary } from "@/lib/types";
import { getStatusLabel, navLabels } from "@/lib/labels";
import { VerdictBadge } from "@/components/VerdictBadge";
import { cn } from "@/lib/utils";

interface HistoryItemProps {
  claim: ClaimSummary;
  isActive?: boolean;
  onClick?: () => void;
  onDelete?: (claimId: string) => void;
}

export function HistoryItem({
  claim,
  isActive,
  onClick,
  onDelete,
}: HistoryItemProps) {
  const preview = claim.complaint_text
    ? claim.complaint_text.slice(0, 72) +
      (claim.complaint_text.length > 72 ? "…" : "")
    : claim.claim_id;

  function handleDelete(e: React.MouseEvent) {
    e.stopPropagation();
    onDelete?.(claim.claim_id);
  }

  return (
    <div
      className={cn(
        "group relative w-full text-left px-3 py-3 rounded-md flex flex-col gap-1.5",
        "transition-colors cursor-pointer",
        "hover:bg-muted/50",
        isActive && "bg-muted/60 ring-1 ring-primary/30",
      )}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick?.();
        }
      }}
    >
      <p className="text-xs text-foreground/90 leading-relaxed line-clamp-2 pr-6">
        {preview}
      </p>

      {/* Status / verdict row */}
      <div className="flex items-center justify-between gap-2">
        {claim.final_verdict ? (
          <VerdictBadge verdict={claim.final_verdict} />
        ) : (
          <span className="font-mono text-xs text-muted-foreground">
            {getStatusLabel(claim.status)}
          </span>
        )}
        <span className="font-mono text-xs text-muted-foreground/95">
          {new Date(claim.received_at).toLocaleDateString("es")}
        </span>
      </div>

      <button
        type="button"
        aria-label={navLabels.deleteClaim}
        onClick={handleDelete}
        className={cn(
          "absolute top-2.5 right-2 size-6 flex items-center justify-center rounded",
          "text-muted-foreground/40 hover:text-destructive hover:bg-destructive/10",
          "transition-colors opacity-0 group-hover:opacity-100 focus-visible:opacity-100",
          "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
        )}
      >
        <Trash2 className="size-3.5" />
      </button>
    </div>
  );
}
