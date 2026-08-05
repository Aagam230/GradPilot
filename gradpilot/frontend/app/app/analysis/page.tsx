"use client";
import Link from "next/link";
import { UploadCloud, Building2 } from "lucide-react";
import { EmptyState } from "@/components/EmptyState";
import { Button } from "@/components/ui/Button";
import { useAppState } from "@/lib/store";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AnalysisIndexPage() {
  const { profileId, lastJob } = useAppState();
  const router = useRouter();

  useEffect(() => {
    if (lastJob?.jobId) {
      router.replace(`/app/analysis/${lastJob.jobId}`);
    }
  }, [lastJob, router]);

  if (lastJob?.jobId) return null;

  if (!profileId) {
    return (
      <div>
        <h1 className="text-2xl font-semibold tracking-tight mb-1">Analysis</h1>
        <p className="text-ink-muted mb-8">Your fit analysis will appear here.</p>
        <EmptyState
          icon={UploadCloud}
          title="Upload your CV to build your profile"
          description="Analysis compares your extracted profile against a target program."
          action={
            <Link href="/app/documents">
              <Button size="sm">Upload CV</Button>
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight mb-1">Analysis</h1>
      <p className="text-ink-muted mb-8">Choose a program to begin analysis.</p>
      <EmptyState
        icon={Building2}
        title="Choose a program to begin analysis"
        description="Select a university and program, and GradPilot will compare it against your profile."
        action={
          <Link href="/app/universities">
            <Button size="sm">Select a program</Button>
          </Link>
        }
      />
    </div>
  );
}
