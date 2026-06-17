"use client";

import { Suspense, useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import type { ClaimRead } from "@/lib/types";
import { getClaim } from "@/lib/api";
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
import { navLabels } from "@/lib/labels";

function ClaimPageInner({ claimId }: { claimId: string }) {
  const searchParams = useSearchParams();
  const isNew = searchParams.get("nuevo") === "1";
  const reduce = useReducedMotion();

  const [claim, setClaim] = useState<ClaimRead | null>(null);
  const [status, setStatus] = useState<
    "loading" | "ready" | "notfound" | "error"
  >("loading");

  const motionProps = {
    initial: { opacity: 0, y: reduce ? 0 : 8 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: reduce ? 0 : -8 },
    transition: {
      duration: reduce ? 0.1 : 0.22,
      ease: [0.22, 1, 0.36, 1] as [number, number, number, number],
    },
  };

  useEffect(() => {
    let cancelled = false;
    setStatus("loading");
    setClaim(null);

    getClaim(claimId)
      .then((data) => {
        if (!cancelled) {
          setClaim(data);
          setStatus("ready");
        }
      })
      .catch((err) => {
        if (!cancelled) {
          const is404 = err instanceof Error && err.message.includes("404");
          setStatus(is404 ? "notfound" : "error");
        }
      });

    return () => {
      cancelled = true;
    };
  }, [claimId]);

  return (
    <AnimatePresence mode="wait">
      {status === "loading" && (
        <motion.div key="loading" {...motionProps}>
          <Card className="border-border bg-card">
            <CardContent className="p-0">
              <ProcessingState />
            </CardContent>
          </Card>
        </motion.div>
      )}

      {status === "notfound" && (
        <motion.div key="notfound" {...motionProps}>
          <Card className="border-border bg-card">
            <CardContent className="py-10 text-center flex flex-col gap-2 items-center">
              <p className="text-sm text-muted-foreground font-mono">
                Reclamo no encontrado
              </p>
              <p className="text-xs text-muted-foreground/70 font-mono">
                {claimId}
              </p>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {status === "error" && (
        <motion.div key="error" {...motionProps}>
          <Card className="border-border bg-card">
            <CardContent className="py-10 text-center flex flex-col gap-2 items-center">
              <p className="text-sm text-destructive font-mono">
                Error al auditar
              </p>
              <p className="text-sm text-muted-foreground">
                No se pudo cargar el reclamo seleccionado.
              </p>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {status === "ready" && claim && (
        <motion.div key={`claim-${claim.claim_id}`} {...motionProps}>
          <Card className="border-border bg-card">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <CardTitle className="font-display text-lg text-foreground">
                  {navLabels.auditTraceTitle}
                </CardTitle>
                <span className="font-mono text-xs text-muted-foreground">
                  {claim.claim_id}
                </span>
              </div>
              <CardDescription className="text-muted-foreground text-sm">
                {navLabels.auditTraceDescription}
              </CardDescription>
            </CardHeader>
            <Separator />
            <CardContent className="p-0">
              <ReasoningTrace
                key={claim.claim_id}
                claim={claim}
                playReveal={isNew}
              />
            </CardContent>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function ClaimPageFallback() {
  return (
    <Card className="border-border bg-card">
      <CardContent className="p-0">
        <ProcessingState />
      </CardContent>
    </Card>
  );
}

export default function ClaimPage() {
  const params = useParams<{ claimId: string }>();
  const claimId = params.claimId;

  return (
    <Suspense fallback={<ClaimPageFallback />}>
      <ClaimPageInner claimId={claimId} />
    </Suspense>
  );
}
