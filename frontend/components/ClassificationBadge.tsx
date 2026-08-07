"use client";
import { motion } from "framer-motion";
import { TrendingUp, TrendingUpDown, Target, ShieldCheck, HelpCircle } from "lucide-react";
import { cn } from "@/lib/utils";

const CONFIG: Record<string, { icon: any; color: string; bg: string; label: string }> = {
  "Very High Reach": { icon: TrendingUpDown, color: "text-reach", bg: "bg-reach/10 border-reach/30", label: "Very High Reach" },
  Reach: { icon: TrendingUp, color: "text-reach", bg: "bg-reach/10 border-reach/30", label: "Reach" },
  Target: { icon: Target, color: "text-target", bg: "bg-target/10 border-target/30", label: "Target" },
  Likely: { icon: ShieldCheck, color: "text-likely", bg: "bg-likely/10 border-likely/30", label: "Likely" },
  "Insufficient Evidence": { icon: HelpCircle, color: "text-ink-faint", bg: "bg-surface-2 border-border", label: "Insufficient Evidence" },
};

export function ClassificationBadge({ classification }: { classification: string }) {
  const cfg = CONFIG[classification] || {
    icon: HelpCircle,
    color: "text-ink-faint",
    bg: "bg-surface-2 border-border",
    label: classification || "Insufficient Evidence",
  };
  const Icon = cfg.icon;
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.92 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 20 }}
      className={cn("inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-sm font-medium", cfg.bg, cfg.color)}
    >
      <Icon size={15} strokeWidth={2} />
      {cfg.label}
    </motion.div>
  );
}
