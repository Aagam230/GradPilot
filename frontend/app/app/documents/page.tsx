"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { FileText, GraduationCap, FlaskConical, Languages, Presentation, CheckCircle2 } from "lucide-react";
import { Dropzone } from "@/components/Dropzone";
import { StageProgress } from "@/components/StageProgress";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { uploadCV } from "@/lib/api";
import { useAppState } from "@/lib/store";

const EXTRACTION_STAGES = [
  { label: "Reading document" },
  { label: "Extracting academics" },
  { label: "Finding research" },
  { label: "Understanding projects" },
  { label: "Building profile" },
];

const PLACEHOLDER_DOCS = [
  { icon: FileText, label: "CV", available: true },
  { icon: GraduationCap, label: "Transcript", available: false },
  { icon: FlaskConical, label: "GRE score report", available: false },
  { icon: Languages, label: "TOEFL / IELTS", available: false },
  { icon: Presentation, label: "Research papers", available: false },
  { icon: FileText, label: "Statement of Purpose", available: false },
];

export default function DocumentsPage() {
  const router = useRouter();
  const { profileId, fileName, setProfile } = useAppState();
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">(
    profileId ? "success" : "idle"
  );
  const [error, setError] = useState<string | null>(null);
  const [stageIndex, setStageIndex] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => () => {
    if (timerRef.current) clearInterval(timerRef.current);
  }, []);

  async function handleFile(file: File) {
    setStatus("uploading");
    setError(null);
    setStageIndex(0);

    timerRef.current = setInterval(() => {
      setStageIndex((i) => (i < EXTRACTION_STAGES.length - 1 ? i + 1 : i));
    }, 700);

    try {
      const data = await uploadCV(file);
      if (timerRef.current) clearInterval(timerRef.current);
      setStageIndex(EXTRACTION_STAGES.length);
      setProfile(data.profile_id, data.profile, file.name);
      setStatus("success");
    } catch (e: any) {
      if (timerRef.current) clearInterval(timerRef.current);
      setError(e.message || "Upload failed");
      setStatus("error");
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight mb-1">Documents</h1>
      <p className="text-ink-muted mb-8">Upload your CV to build your structured profile.</p>

      <div className="grid lg:grid-cols-[1.1fr_0.9fr] gap-6">
        <Card className="p-6">
          <Dropzone onFile={handleFile} status={status} fileName={fileName} errorMessage={error} />

          {status === "uploading" && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="mt-6"
            >
              <StageProgress stages={EXTRACTION_STAGES} currentIndex={stageIndex} />
            </motion.div>
          )}

          {status === "success" && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 flex items-center justify-between gap-4 rounded-xl bg-likely/10 border border-likely/25 px-4 py-3"
            >
              <div className="flex items-center gap-2 text-sm text-likely">
                <CheckCircle2 size={16} />
                Profile extracted successfully
              </div>
              <Button size="sm" onClick={() => router.push("/app/profile")}>
                Review profile
              </Button>
            </motion.div>
          )}
        </Card>

        <Card className="p-6">
          <h2 className="text-sm font-medium text-ink mb-1">Document types</h2>
          <p className="text-xs text-ink-faint mb-5">More document types are coming soon.</p>
          <div className="grid grid-cols-2 gap-3">
            {PLACEHOLDER_DOCS.map((doc) => {
              const Icon = doc.icon;
              return (
                <div
                  key={doc.label}
                  className={`rounded-xl border px-3 py-4 flex flex-col items-center gap-2 text-center ${
                    doc.available
                      ? "border-accent/30 bg-accent-soft/40"
                      : "border-border bg-surface-2/40 opacity-60"
                  }`}
                >
                  <Icon size={18} className={doc.available ? "text-accent" : "text-ink-faint"} strokeWidth={1.7} />
                  <span className="text-xs font-medium text-ink-muted">{doc.label}</span>
                  {!doc.available && <span className="text-[10px] text-ink-faint">Coming soon</span>}
                </div>
              );
            })}
          </div>
        </Card>
      </div>
    </div>
  );
}
