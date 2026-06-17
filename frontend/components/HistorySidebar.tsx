"use client";

import type { ClaimSummary } from "@/lib/types";
import { HistoryItem } from "@/components/HistoryItem";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";

interface HistorySidebarProps {
  claims: ClaimSummary[];
  activeClaim: string | null;
  onSelect: (claimId: string) => void;
}

export function HistorySidebar({
  claims,
  activeClaim,
  onSelect,
}: HistorySidebarProps) {
  return (
    <aside className="flex flex-col h-full overflow-hidden border-r border-border bg-card">
      <div className="px-4 py-4 shrink-0">
        <h2 className="font-mono text-xs text-muted-foreground uppercase tracking-widest">
          Historial de reclamos
        </h2>
      </div>
      <Separator />
      <ScrollArea className="flex-1 min-h-0">
        <div className="px-2 py-2 flex flex-col gap-1">
          {claims.length === 0 ? (
            <p className="px-3 py-4 text-sm text-muted-foreground italic text-center">
              Aún no hay reclamos.
            </p>
          ) : (
            claims.map((claim) => (
              <HistoryItem
                key={claim.claim_id}
                claim={claim}
                isActive={activeClaim === claim.claim_id}
                onClick={() => onSelect(claim.claim_id)}
              />
            ))
          )}
        </div>
      </ScrollArea>
    </aside>
  );
}
