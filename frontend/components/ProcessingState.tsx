"use client";

import { motion } from "motion/react";
import { motionTokens } from "@/lib/motionTokens";

const PIPELINE_STAGES = [
  "Clasificando reclamo…",
  "Recuperando evidencia…",
  "Analizando cláusulas…",
  "Emitiendo veredicto…",
  "Auditando resultado…",
];

function PulsingDot({ delay }: { delay: number }) {
  return (
    <motion.span
      className="inline-block w-1.5 h-1.5 rounded-full bg-primary"
      animate={{ opacity: [0.3, 1, 0.3], scaleY: [0.6, 1, 0.6] }}
      transition={{
        duration: 1.2,
        repeat: Infinity,
        ease: "easeInOut",
        delay,
      }}
      style={{ display: "inline-block" }}
    />
  );
}

export function ProcessingState() {
  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center gap-3">
        <span className="font-mono text-sm text-primary">Auditando</span>
        <span className="flex items-center gap-1">
          <PulsingDot delay={0} />
          <PulsingDot delay={0.2} />
          <PulsingDot delay={0.4} />
        </span>
      </div>

      {/* Pipeline indicator */}
      <div className="flex flex-col gap-0 relative">
        {/* Animated vertical rail */}
        <motion.div
          className="absolute left-[7px] top-4 w-px bg-primary/30 origin-top"
          style={{ height: `calc(100% - 1rem)` }}
          initial={{ scaleY: 0 }}
          animate={{ scaleY: 1 }}
          transition={{
            duration: 1.8,
            ease: motionTokens.easing.smooth,
            repeat: Infinity,
            repeatDelay: 0.5,
          }}
        />

        {PIPELINE_STAGES.map((stage, i) => (
          <motion.div
            key={stage}
            className="flex items-center gap-4 py-2.5 relative"
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{
              duration: motionTokens.duration.normal,
              ease: motionTokens.easing.smooth,
              delay: i * 0.12,
            }}
          >
            {/* Node dot */}
            <motion.div
              className="w-3.5 h-3.5 rounded-full border border-primary/40 bg-card shrink-0 relative z-10"
              animate={{
                borderColor: [
                  "rgba(232,184,75,0.3)",
                  "rgba(232,184,75,0.9)",
                  "rgba(232,184,75,0.3)",
                ],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: "easeInOut",
                delay: i * 0.3,
              }}
            />
            <div className="flex flex-col gap-1 flex-1">
              <span className="font-mono text-xs text-muted-foreground">
                {stage}
              </span>
              <motion.div
                className="h-1 rounded-full bg-primary/20 origin-left"
                animate={{ scaleX: [0, 1] }}
                transition={{
                  duration: 1.4,
                  ease: motionTokens.easing.smooth,
                  delay: i * 0.18 + 0.1,
                  repeat: Infinity,
                  repeatDelay: 2,
                }}
                style={{ width: `${55 + i * 8}%` }}
              />
            </div>
          </motion.div>
        ))}
      </div>

      <div className="flex flex-col gap-3 mt-2">
        {[1, 2, 3].map((n) => (
          <motion.div
            key={n}
            className="h-3 rounded-full bg-muted/60"
            style={{ width: `${85 - n * 10}%` }}
            animate={{ opacity: [0.4, 0.8, 0.4] }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: n * 0.15,
            }}
          />
        ))}
      </div>
    </div>
  );
}
