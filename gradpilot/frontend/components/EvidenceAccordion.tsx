"use client";
import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, User, GraduationCap, ExternalLink } from "lucide-react";
import { RatingMeter } from "./RatingMeter";

type SourceRef = { index: number; url: string; title?: string; excerpt: string };

export function EvidenceAccordion({
  title,
  rating,
  analysis,
  studentItems,
  sources,
}: {
  title: string;
  rating: string;
  analysis: string;
  studentItems: string[];
  sources: SourceRef[];
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-2xl border border-border bg-surface overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full text-left px-5 py-4 flex flex-col gap-3"
      >
        <RatingMeter label={title} rating={rating} />
        <div className="flex items-start justify-between gap-4">
          <p className="text-sm text-ink-muted leading-relaxed">{analysis}</p>
          <motion.span animate={{ rotate: open ? 180 : 0 }} transition={{ duration: 0.2 }} className="shrink-0 mt-0.5">
            <ChevronDown size={16} className="text-ink-faint" />
          </motion.span>
        </div>
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.28, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 pt-1 border-t border-border">
              <div className="relative grid md:grid-cols-2 gap-4 mt-4">
                {/* connecting line */}
                <div className="hidden md:block absolute left-1/2 top-6 bottom-6 w-px bg-border" />

                <div className="rounded-xl bg-surface-2/60 border border-border p-4">
                  <div className="flex items-center gap-2 mb-2.5 text-xs font-medium text-ink-faint uppercase tracking-wide">
                    <User size={13} /> Student evidence
                  </div>
                  {studentItems.length > 0 ? (
                    <ul className="space-y-1.5">
                      {studentItems.map((it, i) => (
                        <li key={i} className="text-sm text-ink-muted leading-snug">
                          {it}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-ink-faint italic">No related items found in profile.</p>
                  )}
                </div>

                <div className="rounded-xl bg-surface-2/60 border border-border p-4">
                  <div className="flex items-center gap-2 mb-2.5 text-xs font-medium text-ink-faint uppercase tracking-wide">
                    <GraduationCap size={13} /> University evidence
                  </div>
                  {sources.length > 0 ? (
                    <ul className="space-y-2.5">
                      {sources.map((s) => (
                        <li key={s.index} className="text-sm text-ink-muted leading-snug">
                          <span className="text-ink-faint">[{s.index}]</span> {s.excerpt}
                          {s.url && s.url !== "user-provided" && (
                            <a
                              href={s.url}
                              target="_blank"
                              rel="noreferrer"
                              className="ml-1.5 inline-flex items-center gap-0.5 text-accent hover:underline"
                            >
                              source <ExternalLink size={11} />
                            </a>
                          )}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-ink-faint italic">Insufficient evidence retrieved.</p>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
