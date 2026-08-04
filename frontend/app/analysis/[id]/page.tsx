"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getAnalysis } from "@/lib/api";
import { FitBadge } from "@/components/FitBadge";
import { SectionCard } from "@/components/SectionCard";

export default function AnalysisPage() {
  const params = useParams();
  const id = params.id as string;
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAnalysis(id)
      .then((d) => setResult(d.result))
      .catch((e) => setError(e.message));
  }, [id]);

  if (error) return <main className="max-w-3xl mx-auto py-12 px-4 text-rose-600">{error}</main>;
  if (!result) return <main className="max-w-3xl mx-auto py-12 px-4 text-slate-500">Loading...</main>;

  const sources = result._evidence_sources || [];
  const sections = [
    ["Academic Fit", result.academic_fit],
    ["Research Fit", result.research_fit],
    ["Project Fit", result.project_fit],
    ["Experience Fit", result.experience_fit],
    ["Program Alignment", result.program_alignment],
  ] as const;

  return (
    <main className="max-w-3xl mx-auto py-12 px-4 space-y-6">
      <Link href="/" className="text-sm text-indigo-600">&larr; New analysis</Link>
      <div>
        <h1 className="text-2xl font-bold mb-2">Profile Fit Analysis</h1>
        <FitBadge rating={result.overall_classification} />
        <p className="mt-3 text-slate-700">{result.overall_fit_summary}</p>
        <p className="mt-2 text-sm text-slate-500">{result.classification_reasoning}</p>
      </div>

      <div className="grid gap-4">
        {sections.map(([title, data]: any) => (
          <SectionCard
            key={title}
            title={title}
            rating={data?.rating}
            analysis={data?.analysis}
            evidence={data?.evidence || []}
            sources={sources}
          />
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <ListCard title="Strengths" items={result.strengths} color="emerald" />
        <ListCard title="Weaknesses" items={result.weaknesses} color="rose" />
        <ListCard title="Profile Gaps" items={result.profile_gaps} color="amber" />
        <ListCard title="Recommended Improvements" items={result.recommended_improvements} color="indigo" />
      </div>

      {sources.length > 0 && (
        <div>
          <h2 className="font-semibold mb-2">Evidence Sources</h2>
          <ol className="text-sm space-y-1 list-decimal list-inside">
            {sources.map((s: any) => (
              <li key={s.index}>
                <a href={s.url} target="_blank" rel="noreferrer" className="text-indigo-600 hover:underline">
                  {s.title || s.url}
                </a>
              </li>
            ))}
          </ol>
        </div>
      )}
    </main>
  );
}

const COLOR_CLASSES: Record<string, string> = {
  emerald: "text-emerald-700",
  rose: "text-rose-700",
  amber: "text-amber-700",
  indigo: "text-indigo-700",
};

function ListCard({ title, items, color }: { title: string; items: string[]; color: string }) {
  return (
    <div className="border border-slate-200 rounded-lg p-4 bg-white">
      <h3 className={`font-semibold mb-2 ${COLOR_CLASSES[color] || "text-slate-700"}`}>{title}</h3>
      <ul className="text-sm text-slate-600 list-disc list-inside space-y-1">
        {(items || []).map((it, i) => (
          <li key={i}>{it}</li>
        ))}
      </ul>
    </div>
  );
}
