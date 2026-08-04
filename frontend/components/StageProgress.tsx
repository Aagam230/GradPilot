"use client";
import { motion } from "framer-motion";
import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export type Stage = { label: string };

export function StageProgress({
  stages,
  currentIndex,
  failed,
}: {
  stages: Stage[];
  /** index of the stage currently in progress; stages before it are complete */
  currentIndex: number;
  failed?: boolean;
}) {
  return (
    <div className="flex flex-col gap-1">
      {stages.map((stage, i) => {
        const isDone = i < currentIndex || (failed === false && currentIndex >= stages.length);
        const isCurrent = i === currentIndex && !isDone;
        const isFailed = failed && i === currentIndex;
        return (
          <motion.div
            key={stage.label}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: i <= currentIndex ? 1 : 0.4, x: 0 }}
            transition={{ duration: 0.25, delay: i * 0.03 }}
            className="flex items-center gap-3 py-2"
          >
            <span
              className={cn(
                "flex items-center justify-center w-6 h-6 rounded-full border shrink-0 transition-colors",
                isDone && "bg-likely/15 border-likely/40 text-likely",
                isCurrent && !isFailed && "bg-accent-soft border-accent/40 text-accent",
                isFailed && "bg-reach/15 border-reach/40 text-reach",
                !isDone && !isCurrent && !isFailed && "border-border text-ink-faint"
              )}
            >
              {isDone ? (
                <Check size={13} strokeWidth={3} />
              ) : isCurrent && !isFailed ? (
                <Loader2 size={13} className="animate-spin" />
              ) : (
                <span className="w-1.5 h-1.5 rounded-full bg-current" />
              )}
            </span>
            <span
              className={cn(
                "text-sm transition-colors",
                isDone && "text-ink-muted",
                isCurrent && "text-ink font-medium",
                isFailed && "text-reach font-medium",
                !isDone && !isCurrent && !isFailed && "text-ink-faint"
              )}
            >
              {stage.label}
            </span>
          </motion.div>
        );
      })}
    </div>
  );
}
