export function FitBadge({ rating }: { rating: string }) {
  const map: Record<string, string> = {
    Reach: "bg-rose-100 text-rose-700 border-rose-300",
    Target: "bg-amber-100 text-amber-700 border-amber-300",
    Likely: "bg-emerald-100 text-emerald-700 border-emerald-300",
    "Insufficient evidence": "bg-slate-100 text-slate-600 border-slate-300",
  };
  const cls = map[rating] || "bg-slate-100 text-slate-600 border-slate-300";
  return (
    <span className={`inline-block px-3 py-1 rounded-full border text-sm font-medium ${cls}`}>
      {rating}
    </span>
  );
}
