"use client";
import { motion } from "framer-motion";
import { UserCircle, Building2, GitCompareArrows, Compass } from "lucide-react";

const STEPS = [
  { label: "Student Profile", icon: UserCircle },
  { label: "Program Intelligence", icon: Building2 },
  { label: "Profile Match", icon: GitCompareArrows },
  { label: "Application Strategy", icon: Compass },
];

export function FlowDiagram() {
  return (
    <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-0 w-full max-w-3xl mx-auto">
      {STEPS.map((step, i) => {
        const Icon = step.icon;
        return (
          <div key={step.label} className="flex items-center sm:flex-1 w-full">
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.15 * i }}
              className="flex flex-1 flex-col items-center gap-2.5 rounded-2xl border border-border bg-surface/80 backdrop-blur-sm px-4 py-5 shadow-soft"
            >
              <motion.div
                animate={{ y: [0, -3, 0] }}
                transition={{ duration: 3, repeat: Infinity, delay: i * 0.3, ease: "easeInOut" }}
                className="w-9 h-9 rounded-xl bg-accent-soft flex items-center justify-center"
              >
                <Icon size={17} className="text-accent" strokeWidth={1.8} />
              </motion.div>
              <span className="text-xs font-medium text-ink-muted text-center">{step.label}</span>
            </motion.div>
            {i < STEPS.length - 1 && (
              <motion.div
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ duration: 0.4, delay: 0.15 * i + 0.25 }}
                style={{ originX: 0 }}
                className="hidden sm:block h-px w-6 bg-border shrink-0"
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
