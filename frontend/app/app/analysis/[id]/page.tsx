"use client";
import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { AlertTriangle, ExternalLink } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { StageProgress } from "@/components/StageProgress";
import { ClassificationBadge } from "@/components/ClassificationBadge";
import { EvidenceAccordion } from "@/components/EvidenceAccordion";
import { Reveal } from "@/components/Reveal";
import { getJob, getAnalysis, JobStatus } from "@/lib/api";
import { useAppState } from "@/lib/store";

const STAGES = [
  { label: "Understanding your profile" },
  { label: "Reviewing program requirements" },
  { label: "Matching research" },
  { label: "Evaluating projects" },
  { label: "Finding gaps" },
  { label: "Building assessment" },
];

function studentItemsFor(dimension: string, profile: any): string[] {
  if (!profile) return [];
  const edu = (profile.education || []).map(
    (e: any) => `${e.degree || ""} ${e.field ? "in " + e.field : ""} — ${e.institution || ""}`.trim()
  );
  const research = (profile.research_experience || []).map((r: any) => `${r.title}${r.description ? " — " + r.description : ""}`);
  const projects = (profile.projects || []).map((p: any) => `${p.title}${p.description ? " — " + p.description : ""}`);
  const work = (profile.work_experience || []).map((w: any) => `${w.role || ""} at ${w.organization || ""}`.trim());

  switch (dimension) {
    case "Academic Fit":
      return edu;
    case "Research Fit":
      return research;
    case "Project Fit":
      return projects;
    case "Experience Fit":
      return work;
    case "Program Alignment":
      return [profile.summary].filter(Boolean);
    default:
      return [];
  }
}

export default function AnalysisJobPage() {
  const params = useParams();
  const jobId = params.id as string;
  const { profile, setLastJob, lastJob } = useAppState();

  const [status, setStatus] = useState<JobStatus | "loading">("loading");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [analyzingTick, setAnalyzingTick] = useState(0);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const tickRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const job = await getJob(jobId);
        if (cancelled) return;
        setStatus(job.status);

        if (job.status === "done" && job.analysis_id) {
          if (pollRef.current) clearInterval(pollRef.current);
          const analysis = await getAnalysis(job.analysis_id);
          if (cancelled) return;
          setResult(analysis.result);
          if (lastJob) setLastJob({ ...lastJob, analysisId: job.analysis_id });
        } else if (job.status === "error") {
          if (pollRef.current) clearInterval(pollRef.current);
          setError(job.error || "Analysis failed");
        }
      } catch (e: any) {
        if (pollRef.current) clearInterval(pollRef.current);
        setError(e.message || "Could not load job status");
      }
    }

    poll();
    pollRef.current = setInterval(poll, 1500);
    return () => {
      cancelled = true;
      if (pollRef.current) clearInterval(pollRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  useEffect(() => {
    if (status === "analyzing") {
      tickRef.current = setInterval(() => {
        setAnalyzingTick((t) => Math.min(t + 1, 3));
      }, 900);
    }
    return () => {
      if (tickRef.current) clearInterval(tickRef.current);
    };
  }, [status]);

  const stageIndex =
    status === "loading" || status === "pending"
      ? 0
      : status === "retrieving"
      ? 1
      : status === "analyzing"
      ? 2 + analyzingTick
      : status === "done"
      ? STAGES.length
      : 2 + analyzingTick;

  if (error) {
    return (
      <div>
        <h1 className="text-2xl font-semibold tracking-tight mb-6">Analysis</h1>
        <Card className="p-8 max-w-lg mx-auto text-center">
          <AlertTriangle size={28} className="text-reach mx-auto mb-3" />
          <p className="text-sm text-ink mb-1 font-medium">Analysis could not be completed</p>
          <p className="text-sm text-ink-muted mb-5">{error}</p>
          <Link href="/app/universities">
            <Button size="sm" variant="secondary">
              Try another program
            </Button>
          </Link>
        </Card>
      </div>
    );
  }

  if (!result) {
    return (
      <div>
        <h1 className="text-2xl font-semibold tracking-tight mb-2">Analyzing your fit</h1>
        <p className="text-ink-muted mb-8">This usually takes under a minute.</p>
        <Card className="p-8 max-w-lg">
          <StageProgress stages={STAGES} currentIndex={stageIndex} />
        </Card>
      </div>
    );
  }

  const sources = result._evidence_sources || [];
  const dimensions = [
    ["Applicant Strength", result.applicant_strength],
    ["Academic Fit", result.academic_fit],
    ["Research Fit", result.research_fit],
    ["Project Fit", result.project_fit],
    ["Experience Fit", result.experience_fit],
    ["Program Alignment", result.program_alignment],
    ["Program Competitiveness", result.program_competitiveness],
  ] as const;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight mb-1">
          {lastJob ? `${lastJob.universityName} — ${lastJob.programName}` : "Fit analysis"}
        </h1>
        <div className="flex items-center gap-3 mt-3">
          <ClassificationBadge classification={result.overall_classification} />
          {result.confidence && (
            <span className="text-xs text-ink-faint">Confidence: {result.confidence}</span>
          )}
        </div>
        <p className="mt-4 text-ink-muted max-w-2xl leading-relaxed">{result.overall_fit_summary}</p>
        <p className="mt-2 text-sm text-ink-faint max-w-2xl">{result.classification_reasoning}</p>
      </div>

      <div className="space-y-3 mb-8">
        {dimensions.map(([title, data], i) => (
          <Reveal key={title} delay={i * 0.06}>
            <EvidenceAccordion
              title={title}
              rating={data?.rating || "Insufficient evidence"}
              analysis={data?.analysis || ""}
              studentItems={studentItemsFor(title, profile)}
              sources={(data?.evidence || [])
                .map((idx: number) => sources.find((s: any) => s.index === idx))
                .filter(Boolean)}
            />
          </Reveal>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-8">
        <ListCard title="Strengths" items={result.strengths} tone="likely" />
        <ListCard title="Weaknesses" items={result.weaknesses} tone="reach" />
        <ListCard title="Profile gaps" items={result.profile_gaps} tone="target" />
        <ListCard title="Recommended improvements" items={result.recommended_improvements} tone="accent" />
      </div>

      {result.community_outcome_evidence?.length > 0 && (
        <Card className="p-5 mb-8 border-target/25 bg-target/5">
          <h2 className="text-sm font-medium text-ink mb-1">Community-reported outcomes</h2>
          <p className="text-xs text-ink-faint mb-3">
            Self-reported by applicants on public forums — unverified, not official data. Used only
            as a secondary signal.
          </p>
          <ul className="space-y-1.5">
            {result.community_outcome_evidence.map((o: any, i: number) => (
              <li key={i} className="text-sm text-ink-muted flex items-start gap-2">
                <span className="text-ink-faint">·</span>
                {o.summary}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {sources.length > 0 && (
        <Card className="p-5">
          <h2 className="text-sm font-medium text-ink mb-3">Evidence sources</h2>
          <ol className="space-y-1.5">
            {sources.map((s: any) => (
              <li key={s.index} className="text-sm flex items-start gap-2">
                <span className="text-ink-faint">[{s.index}]</span>
                {s.url && s.url !== "user-provided" ? (
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-accent hover:underline inline-flex items-center gap-1"
                  >
                    {s.title || s.url} <ExternalLink size={11} />
                  </a>
                ) : (
                  <span className="text-ink-muted">{s.title || "Manually provided text"}</span>
                )}
              </li>
            ))}
          </ol>
        </Card>
      )}
    </div>
  );
}

const TONE_CLASSES: Record<string, string> = {
  likely: "text-likely",
  reach: "text-reach",
  target: "text-target",
  accent: "text-accent",
};

function ListCard({ title, items, tone }: { title: string; items: string[]; tone: string }) {
  return (
    <Card className="p-5">
      <h3 className={`text-sm font-medium mb-2.5 ${TONE_CLASSES[tone]}`}>{title}</h3>
      {items && items.length > 0 ? (
        <ul className="space-y-1.5">
          {items.map((it, i) => (
            <motion.li
              key={i}
              initial={{ opacity: 0, x: -4 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04 }}
              className="text-sm text-ink-muted leading-relaxed"
            >
              · {it}
            </motion.li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-ink-faint italic">None noted.</p>
      )}
    </Card>
  );
}
