"use client";

import { useEffect, useState, useCallback } from "react";
import { toast } from "sonner";
import type { ClaimRead, ClaimSummary } from "@/lib/types";
import { submitClaim, getClaim, listClaims } from "@/lib/api";
import { HistorySidebar } from "@/components/HistorySidebar";
import { ClaimForm } from "@/components/ClaimForm";
import { ReasoningTrace } from "@/components/ReasoningTrace";
import { ProcessingState } from "@/components/ProcessingState";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";

type AppState =
  | { phase: "idle" }
  | { phase: "processing" }
  | { phase: "result"; claim: ClaimRead; isNew: boolean }
  | { phase: "error"; message: string };

export default function Home() {
  const [history, setHistory] = useState<ClaimSummary[]>([]);
  const [activeClaim, setActiveClaim] = useState<string | null>(null);
  const [appState, setAppState] = useState<AppState>({ phase: "idle" });

  // Load history on mount
  const refreshHistory = useCallback(async () => {
    try {
      const claims = await listClaims();
      setHistory(claims);
    } catch {
      // History load failure is non-fatal — sidebar shows empty
    }
  }, []);

  useEffect(() => {
    refreshHistory();
  }, [refreshHistory]);

  // Select a claim from history — instant render (no reveal choreography)
  async function handleHistorySelect(claimId: string) {
    setActiveClaim(claimId);
    setAppState({ phase: "processing" });
    try {
      const claim = await getClaim(claimId);
      setAppState({ phase: "result", claim, isNew: false });
    } catch {
      setAppState({
        phase: "error",
        message: "No se pudo cargar el reclamo seleccionado.",
      });
    }
  }

  // Submit a new claim — POST → GET, then staged reveal
  async function handleSubmit(data: {
    complaint_text: string;
    contract_clauses: string;
  }) {
    setActiveClaim(null);
    setAppState({ phase: "processing" });
    try {
      // POST /api/claims — returns ClaimAccepted quickly
      const accepted = await submitClaim(data);

      // GET /api/claims/{id} — may take several seconds while Groq audits
      const claim = await getClaim(accepted.claim_id);

      setActiveClaim(claim.claim_id);
      setAppState({ phase: "result", claim, isNew: true });
      await refreshHistory();
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Error desconocido al procesar el reclamo.";
      setAppState({ phase: "error", message });
      toast.error("Error al auditar", { description: message });
    }
  }

  const selectedClaim = appState.phase === "result" ? appState.claim : null;
  const isNew = appState.phase === "result" ? appState.isNew : false;

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <div className="w-64 shrink-0 flex flex-col h-full">
        <HistorySidebar
          claims={history}
          activeClaim={activeClaim}
          onSelect={handleHistorySelect}
        />
      </div>

      <main className="flex-1 flex flex-col h-full overflow-hidden">
        <header className="shrink-0 px-6 py-4 border-b border-border flex items-center gap-4">
          <div className="flex flex-col">
            <h1 className="font-display text-lg text-foreground leading-tight">
              SmartClaim Auditor
            </h1>
            <p className="font-mono text-xs text-muted-foreground">
              Consola de auditoría de seguros asistida por IA
            </p>
          </div>
        </header>

        <ScrollArea className="flex-1 min-h-0">
          <div className="p-6 flex flex-col gap-6 max-w-4xl mx-auto">
            <ClaimForm
              onSubmit={handleSubmit}
              isSubmitting={appState.phase === "processing"}
            />

            {appState.phase === "idle" && (
              <Card className="border-border bg-card">
                <CardContent className="py-16 text-center">
                  <p className="text-muted-foreground text-sm">
                    Envíe un reclamo para ver su traza de auditoría, o
                    seleccione uno del historial.
                  </p>
                </CardContent>
              </Card>
            )}

            {appState.phase === "processing" && (
              <Card className="border-border bg-card">
                <CardContent className="p-0">
                  <ProcessingState />
                </CardContent>
              </Card>
            )}

            {appState.phase === "error" && (
              <Card className="border-border bg-card">
                <CardContent className="py-10 text-center flex flex-col gap-2 items-center">
                  <p className="text-sm text-destructive font-mono">
                    Error al auditar
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {appState.message}
                  </p>
                </CardContent>
              </Card>
            )}

            {selectedClaim && (
              <Card className="border-border bg-card">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <CardTitle className="font-display text-lg text-foreground">
                      Traza de razonamiento de auditoría
                    </CardTitle>
                    <span className="font-mono text-xs text-muted-foreground">
                      {selectedClaim.claim_id}
                    </span>
                  </div>
                  <CardDescription className="text-muted-foreground text-sm">
                    Cadena de evidencia paso a paso desde la clasificación hasta
                    el veredicto final.
                  </CardDescription>
                </CardHeader>
                <Separator />
                <CardContent className="p-0">
                  <ReasoningTrace
                    key={selectedClaim.claim_id}
                    claim={selectedClaim}
                    playReveal={isNew}
                  />
                </CardContent>
              </Card>
            )}
          </div>
        </ScrollArea>
      </main>
    </div>
  );
}
