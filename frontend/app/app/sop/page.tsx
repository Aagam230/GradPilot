"use client";
import { PenLine } from "lucide-react";
import { EmptyState } from "@/components/EmptyState";

export default function SopPage() {
  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight mb-1">Statement of Purpose</h1>
      <p className="text-ink-muted mb-8">Coming soon.</p>
      <EmptyState
        icon={PenLine}
        title="SOP generator is coming soon"
        description="GradPilot will help you draft a statement of purpose grounded in your real profile and target program."
      />
    </div>
  );
}
