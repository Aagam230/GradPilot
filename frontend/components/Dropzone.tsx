"use client";
import { useCallback, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, FileText, CheckCircle2, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

type Status = "idle" | "dragging" | "selected" | "uploading" | "success" | "error";

export function Dropzone({
  onFile,
  status,
  fileName,
  errorMessage,
}: {
  onFile: (file: File) => void;
  status: Status;
  fileName?: string | null;
  errorMessage?: string | null;
}) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files?.[0];
      if (file) onFile(file);
    },
    [onFile]
  );

  const visualState: Status = dragging ? "dragging" : status;

  return (
    <div>
      <motion.div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => status !== "uploading" && inputRef.current?.click()}
        animate={{
          borderColor:
            visualState === "dragging"
              ? "rgb(var(--accent))"
              : visualState === "error"
              ? "rgb(var(--reach))"
              : "rgb(var(--border))",
          scale: visualState === "dragging" ? 1.01 : 1,
        }}
        transition={{ duration: 0.18 }}
        className={cn(
          "relative rounded-2xl border-2 border-dashed p-10 flex flex-col items-center justify-center text-center cursor-pointer select-none",
          "bg-surface-2/40 hover:bg-surface-2/70 transition-colors"
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onFile(file);
          }}
        />

        <AnimatePresence mode="wait">
          {status === "success" ? (
            <motion.div
              key="success"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-3"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 300, damping: 18 }}
              >
                <CheckCircle2 size={40} className="text-likely" strokeWidth={1.6} />
              </motion.div>
              <p className="text-sm font-medium text-ink">{fileName}</p>
              <p className="text-xs text-ink-faint">Uploaded — click to replace</p>
            </motion.div>
          ) : status === "error" ? (
            <motion.div
              key="error"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-3"
            >
              <XCircle size={36} className="text-reach" strokeWidth={1.6} />
              <p className="text-sm text-reach">{errorMessage || "Upload failed"}</p>
              <p className="text-xs text-ink-faint">Click to try again</p>
            </motion.div>
          ) : status === "uploading" ? (
            <motion.div
              key="uploading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-3"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              >
                <FileText size={34} className="text-accent" strokeWidth={1.6} />
              </motion.div>
              <p className="text-sm text-ink-muted">Reading document…</p>
            </motion.div>
          ) : (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center gap-3"
            >
              <motion.div
                animate={{ y: visualState === "dragging" ? -4 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <UploadCloud size={34} className="text-accent" strokeWidth={1.6} />
              </motion.div>
              <p className="text-sm font-medium text-ink">
                Drag and drop your CV, or click to browse
              </p>
              <p className="text-xs text-ink-faint">PDF only, up to 10MB</p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
