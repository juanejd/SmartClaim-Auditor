"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { submitClaim, getClaim } from "@/lib/api";
import { ClaimForm } from "@/components/ClaimForm";
import { ProcessingState } from "@/components/ProcessingState";
import { Card, CardContent } from "@/components/ui/card";
import { useConsole } from "@/lib/consoleContext";

type SubmitState = "idle" | "processing" | "error";

export default function NewClaimPage() {
  const router = useRouter();
  const { refreshHistory } = useConsole();
  const reduce = useReducedMotion();
  const [submitState, setSubmitState] = useState<SubmitState>("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");

  const motionProps = {
    initial: { opacity: 0, y: reduce ? 0 : 8 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: reduce ? 0 : -8 },
    transition: {
      duration: reduce ? 0.1 : 0.22,
      ease: [0.22, 1, 0.36, 1] as [number, number, number, number],
    },
  };

  async function handleSubmit(data: {
    complaint_text: string;
    contract_clauses: string;
  }) {
    setSubmitState("processing");
    setErrorMessage("");

    try {
      const accepted = await submitClaim(data);
      await getClaim(accepted.claim_id);
      await refreshHistory();
      router.push(`/auditorias/${accepted.claim_id}?nuevo=1`);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Error desconocido al procesar el reclamo.";
      setErrorMessage(message);
      setSubmitState("error");
      toast.error("Error al auditar", { description: message });
    }
  }

  return (
    <AnimatePresence mode="wait">
      {submitState === "idle" && (
        <motion.div key="form" {...motionProps}>
          <ClaimForm onSubmit={handleSubmit} isSubmitting={false} />
        </motion.div>
      )}

      {submitState === "processing" && (
        <motion.div key="processing" {...motionProps}>
          <Card className="border-border bg-card">
            <CardContent className="p-0">
              <ProcessingState />
            </CardContent>
          </Card>
        </motion.div>
      )}

      {submitState === "error" && (
        <motion.div key="error" {...motionProps}>
          <Card className="border-border bg-card">
            <CardContent className="py-10 text-center flex flex-col gap-2 items-center">
              <p className="text-sm text-destructive font-mono">
                Error al auditar
              </p>
              <p className="text-sm text-muted-foreground">{errorMessage}</p>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
