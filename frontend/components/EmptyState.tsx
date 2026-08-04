"use client";
import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { ReactNode } from "react";

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="flex flex-col items-center justify-center text-center py-20 px-6 rounded-2xl border border-dashed border-border bg-surface-2/50"
    >
      <div className="w-12 h-12 rounded-xl bg-accent-soft flex items-center justify-center mb-4">
        <Icon size={22} className="text-accent" strokeWidth={1.75} />
      </div>
      <h3 className="font-medium text-ink mb-1">{title}</h3>
      <p className="text-sm text-ink-muted max-w-sm">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </motion.div>
  );
}
