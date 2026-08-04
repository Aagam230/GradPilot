type EvidenceSource = { index: number; url: string; title: string; excerpt: string };

export function SectionCard({
  title,
  rating,
  analysis,
  evidence,
  sources,
}: {
  title: string;
  rating: string;
  analysis: string;
  evidence: number[];
  sources: EvidenceSource[];
}) {
  return (
    <div className="border border-slate-200 rounded-lg p-4 bg-white">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-slate-800">{title}</h3>
        <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600">{rating}</span>
      </div>
      <p className="text-sm text-slate-600 mb-2">{analysis}</p>
      {evidence?.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {evidence.map((i) => {
            const src = sources.find((s) => s.index === i);
            return (
              <a
                key={i}
                href={src?.url}
                target="_blank"
                rel="noreferrer"
                title={src?.excerpt}
                className="text-xs px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100"
              >
                [{i}]
              </a>
            );
          })}
        </div>
      )}
    </div>
  );
}
