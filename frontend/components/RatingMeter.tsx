"use client";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

// Qualitative levels only — derived from the rating text the backend returns.
// This never invents a numeric score; it just gives the existing category a visual position.
const LEVELS = ["Insufficient evidence", "Weak", "Moderate", "Strong"];

function levelIndex(rating: string): number {
  const r = (rating || "").toLowerCase();
  if (r.includes("insufficient")) return 0;
  if (r.includes("weak") || r.includes("limited") || r.includes("poor")) return 1;
  if (r.includes("moderate") || r.includes("fair") || r.includes("partial")) return 2;
  if (r.includes("strong") || r.includes("excellent") || r.includes("good")) return 3;
  return 2;
}

export function RatingMeter({ label, rating }: { label: string; rating: string }) {
  const idx = levelIndex(rating);
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-sm font-medium text-ink">{label}</span>
        <span className="text-xs text-ink-muted">{rating}</span>
      </div>
      <div className="flex gap-1">
        {LEVELS.map((_, i) => (
          <div key={i} className="h-1.5 flex-1 rounded-full bg-surface-2 overflow-hidden">
            <motion.div
              initial={{ scaleX: 0 }}
              animate={{ scaleX: i <= idx ? 1 : 0 }}
              transition={{ duration: 0.5, delay: 0.1 + i * 0.06, ease: "easeOut" }}
              style={{ originX: 0 }}
              className={cn(
                "h-full rounded-full",
                idx === 0 && "bg-ink-faint",
                idx === 1 && "bg-reach",
                idx === 2 && "bg-target",
                idx === 3 && "bg-likely"
              )}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
