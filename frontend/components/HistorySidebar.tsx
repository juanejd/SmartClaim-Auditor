"use client";

import { Plus } from "lucide-react";
import type { ClaimSummary } from "@/lib/types";
import { HistoryItem } from "@/components/HistoryItem";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { navLabels } from "@/lib/labels";

interface HistorySidebarProps {
  claims: ClaimSummary[];
  activeClaim: string | null;
  onSelect: (claimId: string) => void;
  onNewClaim: () => void;
  onDelete: (claimId: string) => void;
}

export function HistorySidebar({
  claims,
  activeClaim,
  onSelect,
  onNewClaim,
  onDelete,
}: HistorySidebarProps) {
  return (
    <aside className="flex flex-col h-full overflow-hidden border-r border-border bg-card">
      {/* Header + new claim button */}
      <div className="px-3 py-3 shrink-0 flex items-center justify-between gap-2">
        <h2 className="font-mono text-xs text-muted-foreground uppercase tracking-widest">
          {navLabels.historyHeading}
        </h2>
        <button
          type="button"
          onClick={onNewClaim}
          className="flex items-center gap-1 font-mono text-xs text-primary hover:text-primary/80 transition-colors px-2 py-1 rounded-md hover:bg-primary/10 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring cursor-pointer"
          aria-label={navLabels.newClaim}
        >
          <Plus className="size-3" />
          {navLabels.newClaim}
        </button>
      </div>
      <Separator />
      <ScrollArea className="flex-1 min-h-0">
        <div className="px-2 py-2 flex flex-col gap-1">
          {claims.length === 0 ? (
            <p className="px-3 py-4 text-sm text-muted-foreground italic text-center">
              {navLabels.noHistory}
            </p>
          ) : (
            claims.map((claim) => (
              <HistoryItem
                key={claim.claim_id}
                claim={claim}
                isActive={activeClaim === claim.claim_id}
                onClick={() => onSelect(claim.claim_id)}
                onDelete={onDelete}
              />
            ))
          )}
        </div>
      </ScrollArea>
    </aside>
  );
}
