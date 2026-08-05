"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Search, UploadCloud, ArrowRight } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/EmptyState";
import { createJob } from "@/lib/api";
import { useAppState } from "@/lib/store";

export default function UniversitiesPage() {
  const router = useRouter();
  const { profileId, setLastJob } = useAppState();
  const [university, setUniversity] = useState("");
  const [programName, setProgramName] = useState("");
  const [seedUrl, setSeedUrl] = useState("");
  const [manualText, setManualText] = useState("");
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!profileId) {
    return (
      <div>
        <h1 className="text-2xl font-semibold tracking-tight mb-1">Universities</h1>
        <p className="text-ink-muted mb-8">Choose a program to begin analysis.</p>
        <EmptyState
          icon={UploadCloud}
          title="Upload your CV first"
          description="GradPilot needs your profile before it can compare you against a program."
          action={
            <Link href="/app/documents">
              <Button size="sm">Upload CV</Button>
            </Link>
          }
        />
      </div>
    );
  }

  async function handleSubmit() {
    setSubmitting(true);
    setError(null);
    try {
      const job = await createJob({
        profile_id: profileId!,
        university_name: university,
        program_name: programName,
        seed_url: seedUrl || undefined,
        manual_text: manualText || undefined,
      });
      setLastJob({ jobId: job.job_id, universityName: university, programName });
      router.push(`/app/analysis/${job.job_id}`);
    } catch (e: any) {
      setError(e.message || "Could not start analysis");
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight mb-1">Universities</h1>
      <p className="text-ink-muted mb-8">
        Tell us your target program. We&apos;ll retrieve official program information and compare it
        against your profile.
      </p>

      <Card className="p-6 max-w-2xl">
        {error && (
          <div className="mb-4 text-sm text-reach bg-reach/10 border border-reach/20 rounded-lg px-3 py-2">
            {error}
          </div>
        )}

        <div className="relative mb-4">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-faint" />
          <input
            placeholder="University name (e.g. Stanford University)"
            value={university}
            onChange={(e) => setUniversity(e.target.value)}
            className="w-full border border-border bg-surface-2/40 focus:bg-surface rounded-xl pl-10 pr-4 py-3 text-sm outline-none focus:ring-2 focus:ring-accent/30 transition-shadow"
          />
        </div>

        <div className="relative mb-4">
          <Search size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ink-faint" />
          <input
            placeholder="Program name (e.g. MS in Computer Science)"
            value={programName}
            onChange={(e) => setProgramName(e.target.value)}
            className="w-full border border-border bg-surface-2/40 focus:bg-surface rounded-xl pl-10 pr-4 py-3 text-sm outline-none focus:ring-2 focus:ring-accent/30 transition-shadow"
          />
        </div>

        <button
          onClick={() => setAdvancedOpen((o) => !o)}
          className="flex items-center gap-1.5 text-xs text-ink-muted hover:text-ink mb-2"
        >
          <motion.span animate={{ rotate: advancedOpen ? 180 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronDown size={13} />
          </motion.span>
          Advanced (optional source overrides)
        </button>

        <AnimatePresence initial={false}>
          {advancedOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.25 }}
              className="overflow-hidden"
            >
              <div className="pt-2 pb-1 space-y-3">
                <input
                  placeholder="Official program page URL"
                  value={seedUrl}
                  onChange={(e) => setSeedUrl(e.target.value)}
                  className="w-full border border-border bg-surface-2/40 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-accent/30"
                />
                <textarea
                  placeholder="Paste official program page text (used if live web search isn't configured)"
                  value={manualText}
                  onChange={(e) => setManualText(e.target.value)}
                  rows={4}
                  className="w-full border border-border bg-surface-2/40 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-accent/30"
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <Button
          onClick={handleSubmit}
          disabled={!university || !programName || submitting}
          className="mt-4 group"
        >
          {submitting ? "Starting…" : "Run fit analysis"}
          {!submitting && <ArrowRight size={15} className="transition-transform group-hover:translate-x-0.5" />}
        </Button>
      </Card>
    </div>
  );
}
