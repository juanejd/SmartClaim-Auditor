"use client";

import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import { VerdictBadge } from "@/components/VerdictBadge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { motionTokens } from "@/lib/motionTokens";

interface AuditCorrectionProps {
  draftVerdict: string | null;
  finalVerdict: string | null;
  correctionsApplied: boolean | null;
  draftJustification: string | null;
  animate?: boolean;
}

export function AuditCorrection({
  draftVerdict,
  finalVerdict,
  correctionsApplied,
  draftJustification,
  animate: runAnimation = true,
}: AuditCorrectionProps) {
  const reduce = useReducedMotion();

  if (!correctionsApplied) {
    return (
      <motion.div
        initial={{ opacity: 0, y: reduce ? 0 : motionTokens.distance.sm }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: motionTokens.duration.normal,
          ease: motionTokens.easing.smooth,
        }}
      >
        <Alert className="border-verdict-approved/30 bg-verdict-approved/5">
          <AlertDescription className="flex items-center gap-2 text-sm text-muted-foreground">
            <motion.span
              className="text-verdict-approved text-base leading-none select-none"
              initial={{ scale: reduce ? 1 : 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{
                duration: 0.3,
                ease: motionTokens.easing.smooth,
                delay: 0.15,
              }}
            >
              ✓
            </motion.span>
            El auditor confirmó el borrador — no se realizaron correcciones.
          </AlertDescription>
        </Alert>
      </motion.div>
    );
  }

  const strikeDuration = reduce ? 0 : 0.35;
  const flashDelay = reduce ? 0 : 0.5;
  const labelDelay = reduce ? 0.05 : 0.55;

  return (
    <div className="flex flex-col gap-3">
      {/* Draft verdict with strike-through animation */}
      <motion.div
        className="relative rounded-md border border-verdict-rejected/30 bg-verdict-rejected/5 px-4 py-3 overflow-hidden"
        initial={{ opacity: 0, y: reduce ? 0 : motionTokens.distance.sm }}
        animate={{ opacity: 1, y: 0 }}
        transition={{
          duration: motionTokens.duration.normal,
          ease: motionTokens.easing.smooth,
        }}
      >
        {/* Amber flash overlay */}
        <motion.div
          className="absolute inset-0 bg-primary/10 pointer-events-none"
          initial={{ opacity: 0 }}
          animate={runAnimation ? { opacity: [0, 0, 0.55, 0] } : { opacity: 0 }}
          transition={{
            duration: reduce ? 0 : 0.7,
            ease: "easeOut",
            delay: flashDelay,
            times: [0, 0.45, 0.55, 1],
          }}
        />

        <div className="flex flex-col gap-2 relative">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground font-mono">
              BORRADOR
            </span>
            <div className="relative">
              <VerdictBadge verdict={draftVerdict} />
              {/* Strike-through line that sweeps across the badge */}
              {runAnimation && (
                <motion.div
                  className="absolute top-1/2 left-0 h-px bg-verdict-rejected origin-left pointer-events-none"
                  style={{ width: "100%", translateY: "-50%" }}
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: reduce ? 0 : 1 }}
                  transition={{
                    duration: strikeDuration,
                    ease: motionTokens.easing.sharp,
                    delay: 0.3,
                  }}
                />
              )}
            </div>
          </div>
          {draftJustification && (
            <p className="text-sm text-muted-foreground leading-relaxed">
              {draftJustification}
            </p>
          )}
        </div>
      </motion.div>

      {/* Detector label — slides in after the flash */}
      <AnimatePresence mode="wait">
        {runAnimation && (
          <motion.div
            key="detector-label"
            className="flex items-center gap-2 px-1"
            initial={{ opacity: 0, y: reduce ? 0 : 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: motionTokens.duration.normal,
              ease: motionTokens.easing.smooth,
              delay: labelDelay,
            }}
          >
            <div className="flex-1 h-px bg-border" />
            <span className="text-xs font-mono text-primary px-2 whitespace-nowrap">
              El auditor detectó una afirmación sin respaldo
            </span>
            <div className="flex-1 h-px bg-border" />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
