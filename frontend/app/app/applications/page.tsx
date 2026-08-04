"use client";
import { ClipboardList } from "lucide-react";
import { EmptyState } from "@/components/EmptyState";

export default function ApplicationsPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight mb-1">Applications</h1>
      <p className="text-ink-muted mb-8">Coming soon.</p>
      <EmptyState
        icon={ClipboardList}
        title="Application tracker is coming soon"
        description="Track deadlines, statuses and materials across every program you apply to."
      />
    </div>
  );
}
