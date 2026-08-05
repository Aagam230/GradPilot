"use client";
import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, Loader2, X, AlertCircle, LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { DocType, DocumentSummary } from "@/lib/api";

const STAGE_CYCLE = [
  "Reading document",
  "Extracting details",
  "Cross-checking profile",
  "Updating profile",
];

export function DocumentSlot({
  icon: Icon,
  label,
  docType,
  required,
  existing,
  onUpload,
  onRemove,
}: {
  icon: LucideIcon;
  label: string;
  docType: DocType;
  required?: boolean;
  existing?: DocumentSummary;
  onUpload: (file: File, docType: DocType) => Promise<void>;
  onRemove?: (docId: string) => Promise<void>;
}) {
  const [status, setStatus] = useState<"idle" | "uploading" | "error" | "removing">("idle");
  const [error, setError] = useState<string | null>(null);
  const [stageText, setStageText] = useState(STAGE_CYCLE[0]);
  const inputRef = useRef<HTMLInputElement>(null);
  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => () => {
    if (tickRef.current) clearInterval(tickRef.current);
  }, []);

  async function handleFile(file: File) {
    setStatus("uploading");
    setError(null);
    let i = 0;
    setStageText(STAGE_CYCLE[0]);
    tickRef.current = setInterval(() => {
      i = Math.min(i + 1, STAGE_CYCLE.length - 1);
      setStageText(STAGE_CYCLE[i]);
    }, 650);

    try {
      await onUpload(file, docType);
      setStatus("idle");
    } catch (e: any) {
      setError(e.message || "Upload failed");
      setStatus("error");
    } finally {
      if (tickRef.current) clearInterval(tickRef.current);
    }
  }

  async function handleRemove() {
    if (!existing || !onRemove) return;
    setStatus("removing");
    try {
      await onRemove(existing.id);
      setStatus("idle");
    } catch (e: any) {
      setError(e.message || "Could not remove");
      setStatus("error");
    }
  }

  const busy = status === "uploading" || status === "removing";

  return (
    <div
      className={cn(
        "relative rounded-xl border px-3 py-4 flex flex-col items-center gap-2 text-center transition-colors",
        existing ? "border-accent/30 bg-accent-soft/40" : "border-border bg-surface-2/40 hover:bg-surface-2/70",
        status === "error" && "border-reach/40 bg-reach/5"
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
          e.target.value = "";
        }}
      />

      {existing && !busy && (
        <button
          onClick={handleRemove}
          className="absolute top-1.5 right-1.5 w-5 h-5 rounded-full bg-surface border border-border flex items-center justify-center text-ink-faint hover:text-reach"
          aria-label="Remove document"
        >
          <X size={11} />
        </button>
      )}

      <button
        onClick={() => !busy && inputRef.current?.click()}
        disabled={busy}
        className="flex flex-col items-center gap-2 w-full"
      >
        <AnimatePresence mode="wait">
          {busy ? (
            <motion.div key="busy" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <Loader2 size={18} className="text-accent animate-spin" strokeWidth={1.8} />
            </motion.div>
          ) : existing ? (
            <motion.div key="done" initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}>
              <CheckCircle2 size={18} className="text-likely" strokeWidth={1.8} />
            </motion.div>
          ) : status === "error" ? (
            <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <AlertCircle size={18} className="text-reach" strokeWidth={1.8} />
            </motion.div>
          ) : (
            <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <Icon size={18} className="text-ink-faint" strokeWidth={1.7} />
            </motion.div>
          )}
        </AnimatePresence>

        <span className="text-xs font-medium text-ink-muted">
          {label}
          {required && !existing && <span className="text-accent"> *</span>}
        </span>

        <AnimatePresence mode="wait">
          {status === "uploading" ? (
            <motion.span
              key={stageText}
              initial={{ opacity: 0, y: 2 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="text-[10px] text-accent"
            >
              {stageText}
            </motion.span>
          ) : status === "removing" ? (
            <span className="text-[10px] text-ink-faint">Removing…</span>
          ) : status === "error" ? (
            <span className="text-[10px] text-reach">{error}</span>
          ) : existing ? (
            <span className="text-[10px] text-ink-faint truncate max-w-[100px]">{existing.filename}</span>
          ) : (
            <span className="text-[10px] text-ink-faint">Upload PDF</span>
          )}
        </AnimatePresence>
      </button>
    </div>
  );
}
