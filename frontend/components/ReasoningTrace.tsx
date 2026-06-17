"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import type { ClaimRead } from "@/lib/types";
import { getVerdictLabel, getIntentLabel } from "@/lib/labels";
import { VerdictBadge } from "@/components/VerdictBadge";
import { ConfidenceMeter } from "@/components/ConfidenceMeter";
import { EvidencePanel } from "@/components/EvidencePanel";
import { AuditCorrection } from "@/components/AuditCorrection";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { motionTokens } from "@/lib/motionTokens";

interface StageProps {
  number: string;
  label: string;
  children: React.ReactNode;
  visible: boolean;
  delay: number;
  isLast?: boolean;
}

function StageSkeleton() {
  return (
    <div className="pl-8 flex flex-col gap-2">
      {[80, 60, 72].map((w, i) => (
        <motion.div
          key={i}
          className="h-3 rounded-full bg-muted/50"
          style={{ width: `${w}%` }}
          animate={{ opacity: [0.35, 0.65, 0.35] }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            ease: "easeInOut",
            delay: i * 0.15,
          }}
        />
      ))}
    </div>
  );
}

function Stage({
  number,
  label,
  children,
  visible,
  delay,
  isLast,
}: StageProps) {
  const reduce = useReducedMotion();
  const [showSkeleton, setShowSkeleton] = useState(false);
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    if (!visible) {
      setShowSkeleton(false);
      setShowContent(false);
      return;
    }
    if (reduce) {
      setShowContent(true);
      return;
    }
    const skeletonTimer = setTimeout(() => setShowSkeleton(true), delay * 1000);
    const contentTimer = setTimeout(
      () => {
        setShowSkeleton(false);
        setShowContent(true);
      },
      (delay + 0.35) * 1000,
    );

    return () => {
      clearTimeout(skeletonTimer);
      clearTimeout(contentTimer);
    };
  }, [visible, delay, reduce]);

  return (
    <motion.section
      className="flex flex-col gap-3"
      initial={{ opacity: 0, y: reduce ? 0 : motionTokens.distance.sm }}
      animate={
        visible
          ? { opacity: 1, y: 0 }
          : { opacity: 0, y: reduce ? 0 : motionTokens.distance.sm }
      }
      transition={{
        duration: motionTokens.duration.normal,
        ease: motionTokens.easing.smooth,
        delay: reduce ? 0 : delay,
      }}
    >
      <div className="flex items-center gap-3">
        <span className="font-mono text-xs text-primary bg-primary/10 border border-primary/30 rounded px-2 py-0.5 shrink-0">
          {number}
        </span>
        <span className="text-xs font-mono text-muted-foreground uppercase tracking-widest">
          {label}
        </span>
      </div>
      <AnimatePresence mode="wait">
        {showSkeleton && !showContent && (
          <motion.div
            key="skeleton"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
          >
            <StageSkeleton />
          </motion.div>
        )}
        {showContent && (
          <motion.div
            key="content"
            className="pl-8"
            initial={{ opacity: 0, y: reduce ? 0 : 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: motionTokens.duration.fast,
              ease: motionTokens.easing.smooth,
            }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.section>
  );
}

function ConnectingRail({ visible }: { visible: boolean }) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className="w-px bg-border/60 origin-top mx-[calc(0.5rem+1.5px)]"
      style={{ height: "1.5rem" }}
      initial={{ scaleY: 0, opacity: 0 }}
      animate={
        visible
          ? { scaleY: reduce ? 0 : 1, opacity: reduce ? 0 : 0.6 }
          : { scaleY: 0, opacity: 0 }
      }
      transition={{ duration: 0.2, ease: motionTokens.easing.sharp }}
    />
  );
}

interface ReasoningTraceProps {
  claim: ClaimRead;
  playReveal?: boolean;
}

const STAGE_DELAYS = [0, 0.45, 0.9, 1.4, 1.95, 2.55];

export function ReasoningTrace({
  claim,
  playReveal = true,
}: ReasoningTraceProps) {
  const reduce = useReducedMotion();
  const isAudited = claim.status === "AUDITED";
  const isUnavailable =
    isAudited && (claim.final_verdict === null || claim.draft_verdict === null);

  const [visibleStages, setVisibleStages] = useState<boolean[]>(
    playReveal && !reduce ? Array(6).fill(false) : Array(6).fill(true),
  );

  useEffect(() => {
    if (!playReveal || reduce) {
      setVisibleStages(Array(6).fill(true));
      return;
    }

    setVisibleStages(Array(6).fill(false));

    const timers: ReturnType<typeof setTimeout>[] = [];

    STAGE_DELAYS.forEach((delay, i) => {
      const t = setTimeout(() => {
        setVisibleStages((prev) => {
          const next = [...prev];
          next[i] = true;
          return next;
        });
      }, delay * 1000);
      timers.push(t);
    });

    return () => timers.forEach(clearTimeout);
  }, [claim.claim_id, playReveal, reduce]);

  return (
    <div className="flex flex-col p-6">
      {/* Stage 1: Claim received */}
      <Stage
        number="01"
        label="Reclamo recibido"
        visible={visibleStages[0]}
        delay={STAGE_DELAYS[0]}
      >
        <div className="flex flex-col gap-2">
          <p className="text-sm text-foreground leading-relaxed">
            {claim.complaint_text}
          </p>
          <div className="font-mono text-xs text-muted-foreground">
            ID: {claim.claim_id} ·{" "}
            {new Date(claim.received_at).toLocaleString("es")}
          </div>
        </div>
      </Stage>

      <ConnectingRail visible={visibleStages[0]} />
      <Separator />
      <ConnectingRail visible={visibleStages[1]} />

      {/* Stage 2: Classification */}
      <Stage
        number="02"
        label="Clasificación"
        visible={visibleStages[1]}
        delay={STAGE_DELAYS[1]}
      >
        {claim.intent_label ? (
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="font-mono text-sm text-foreground">
                {getIntentLabel(claim.intent_label)}
              </span>
              {claim.confidence !== null && (
                <span className="font-mono text-xs text-muted-foreground">
                  confianza
                </span>
              )}
            </div>
            <ConfidenceMeter confidence={claim.confidence} />
          </div>
        ) : (
          <p className="text-sm text-muted-foreground italic">
            Clasificación pendiente.
          </p>
        )}
      </Stage>

      <ConnectingRail visible={visibleStages[1]} />
      <Separator />
      <ConnectingRail visible={visibleStages[2]} />

      {/* Stage 3: Evidence */}
      <Stage
        number="03"
        label="Evidencia"
        visible={visibleStages[2]}
        delay={STAGE_DELAYS[2]}
      >
        <EvidencePanel
          chunks={claim.rag_chunks ?? []}
          citation={claim.rag_citation}
          contractClauses={claim.contract_clauses}
        />
      </Stage>

      <ConnectingRail visible={visibleStages[2]} />
      <Separator />
      <ConnectingRail visible={visibleStages[3]} />

      {/* Stage 4: Draft verdict */}
      <Stage
        number="04"
        label="Veredicto borrador"
        visible={visibleStages[3]}
        delay={STAGE_DELAYS[3]}
      >
        {claim.draft_verdict ? (
          <div className="flex flex-col gap-2">
            <VerdictBadge verdict={claim.draft_verdict} />
            {claim.draft_justification && (
              <p className="text-sm text-muted-foreground leading-relaxed">
                {claim.draft_justification}
              </p>
            )}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground italic">
            Veredicto borrador no disponible.
          </p>
        )}
      </Stage>

      <ConnectingRail visible={visibleStages[3]} />
      <Separator />
      <ConnectingRail visible={visibleStages[4]} />

      {/* Stage 5: Auditor review — the wow moment lives here */}
      <Stage
        number="05"
        label="Revisión del auditor"
        visible={visibleStages[4]}
        delay={STAGE_DELAYS[4]}
      >
        {isAudited ? (
          <AuditCorrection
            draftVerdict={claim.draft_verdict}
            finalVerdict={claim.final_verdict}
            correctionsApplied={claim.corrections_applied}
            draftJustification={
              claim.corrections_applied ? claim.draft_justification : null
            }
            animate={playReveal}
          />
        ) : (
          <Alert className="border-border bg-muted/20">
            <AlertDescription className="text-sm text-muted-foreground">
              En espera de revisión del auditor.
            </AlertDescription>
          </Alert>
        )}
      </Stage>

      <ConnectingRail visible={visibleStages[4]} />
      <Separator />
      <ConnectingRail visible={visibleStages[5]} />

      {/* Stage 6: Final verdict */}
      <Stage
        number="06"
        label="Veredicto final"
        visible={visibleStages[5]}
        delay={STAGE_DELAYS[5]}
      >
        {isUnavailable ? (
          <Alert className="border-border bg-muted/20">
            <AlertDescription className="text-sm text-muted-foreground">
              Derivado a revisión manual — no se emitió veredicto automatizado.
            </AlertDescription>
          </Alert>
        ) : isAudited && claim.final_verdict ? (
          <div className="flex flex-col gap-3">
            <motion.div
              className="flex items-center gap-3"
              initial={{ opacity: 0, y: reduce ? 0 : motionTokens.distance.sm }}
              animate={
                visibleStages[5]
                  ? { opacity: 1, y: 0 }
                  : { opacity: 0, y: reduce ? 0 : motionTokens.distance.sm }
              }
              transition={{
                duration: motionTokens.duration.slow,
                ease: motionTokens.easing.smooth,
                delay: reduce ? 0 : 0.1,
              }}
            >
              <span className="font-display text-2xl text-foreground leading-tight">
                {getVerdictLabel(claim.final_verdict)}
              </span>
              <VerdictBadge verdict={claim.final_verdict} />
            </motion.div>
            {claim.final_justification && (
              <motion.p
                className="text-sm text-foreground/80 leading-relaxed"
                initial={{ opacity: 0 }}
                animate={visibleStages[5] ? { opacity: 1 } : { opacity: 0 }}
                transition={{
                  duration: motionTokens.duration.normal,
                  delay: reduce ? 0 : 0.25,
                }}
              >
                {claim.final_justification}
              </motion.p>
            )}
          </div>
        ) : (
          <Alert className="border-border bg-muted/20">
            <AlertDescription className="text-sm text-muted-foreground">
              {claim.rag_chunks === null || claim.rag_chunks.length === 0
                ? "Evidencia insuficiente — derivado a revisión manual. No se emitió veredicto automatizado."
                : "Veredicto final pendiente."}
            </AlertDescription>
          </Alert>
        )}
      </Stage>
    </div>
  );
}
