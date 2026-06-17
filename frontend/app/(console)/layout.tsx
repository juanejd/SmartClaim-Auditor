"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { toast } from "sonner";
import type { ClaimSummary } from "@/lib/types";
import { listClaims, deleteClaim } from "@/lib/api";
import { HistorySidebar } from "@/components/HistorySidebar";
import { ConsoleContext } from "@/lib/consoleContext";

export default function ConsoleLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [history, setHistory] = useState<ClaimSummary[]>([]);

  const refreshHistory = useCallback(async () => {
    try {
      const claims = await listClaims();
      setHistory(claims);
    } catch {}
  }, []);

  useEffect(() => {
    refreshHistory();
  }, [refreshHistory]);

  const activeClaimId = useMemo(() => {
    const match = pathname.match(/^\/auditorias\/([^/]+)$/);
    return match ? match[1] : null;
  }, [pathname]);

  function handleNewClaim() {
    router.push("/");
  }

  function handleSelect(claimId: string) {
    router.push(`/auditorias/${claimId}`);
  }

  async function handleDelete(claimId: string) {
    setHistory((prev) => prev.filter((c) => c.claim_id !== claimId));

    if (activeClaimId === claimId) {
      router.push("/");
    }

    try {
      await deleteClaim(claimId);
    } catch {
      toast.error("No se pudo eliminar el reclamo.");
      refreshHistory();
    }
  }

  const contextValue = useMemo(() => ({ refreshHistory }), [refreshHistory]);

  return (
    <ConsoleContext.Provider value={contextValue}>
      <div className="flex flex-1 min-h-0 overflow-hidden bg-background">
        {/* Left sidebar — persists across all console routes */}
        <div className="w-60 shrink-0 flex flex-col h-full">
          <HistorySidebar
            claims={history}
            activeClaim={activeClaimId}
            onSelect={handleSelect}
            onNewClaim={handleNewClaim}
            onDelete={handleDelete}
          />
        </div>

        {/* Main content — driven by child route */}
        <main className="flex-1 flex flex-col h-full overflow-hidden">
          <div className="flex-1 min-h-0 overflow-y-auto">
            <div className="p-6 flex flex-col gap-6 max-w-4xl mx-auto min-h-full">
              {children}
            </div>
          </div>
        </main>
      </div>
    </ConsoleContext.Provider>
  );
}
