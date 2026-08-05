"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import { Check, UserCircle, Building2, Sparkles, PenLine, ClipboardList } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Reveal } from "@/components/Reveal";
import { useAppState } from "@/lib/store";

export default function OverviewPage() {
  const { profile, lastJob } = useAppState();

  const steps = [
    { label: "Profile", icon: UserCircle, done: !!profile, href: "/app/documents" },
    { label: "Shortlist", icon: Building2, done: !!lastJob, href: "/app/universities" },
    { label: "Analyze", icon: Sparkles, done: !!lastJob?.analysisId, href: "/app/analysis" },
    { label: "SOP", icon: PenLine, done: false, href: "/app/sop" },
    { label: "Apply", icon: ClipboardList, done: false, href: "/app/applications" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight mb-1">Overview</h1>
      <p className="text-ink-muted mb-8">Your graduate application journey.</p>

      <Card className="p-6 mb-8 overflow-x-auto">
        <div className="flex items-center min-w-[560px]">
          {steps.map((step, i) => {
            const Icon = step.icon;
            return (
              <div key={step.label} className="flex items-center flex-1">
                <Link href={step.href} className="flex flex-col items-center gap-2 group">
                  <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: i * 0.08 }}
                    className={`w-10 h-10 rounded-full flex items-center justify-center border transition-colors ${
                      step.done
                        ? "bg-likely/15 border-likely/40 text-likely"
                        : "bg-surface-2 border-border text-ink-faint group-hover:border-accent/40 group-hover:text-accent"
                    }`}
                  >
                    {step.done ? <Check size={16} /> : <Icon size={16} />}
                  </motion.div>
                  <span className="text-xs text-ink-muted">{step.label}</span>
                </Link>
                {i < steps.length - 1 && (
                  <motion.div
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: 1 }}
                    transition={{ delay: i * 0.08 + 0.1 }}
                    style={{ originX: 0 }}
                    className={`h-px flex-1 mx-2 ${step.done ? "bg-likely/40" : "bg-border"}`}
                  />
                )}
              </div>
            );
          })}
        </div>
      </Card>

      <div className="grid sm:grid-cols-2 gap-5">
        <Reveal>
          <Card className="p-6">
            <h3 className="text-sm font-medium text-ink mb-2">Profile</h3>
            {profile ? (
              <p className="text-sm text-ink-muted leading-relaxed">{profile.summary}</p>
            ) : (
              <p className="text-sm text-ink-faint italic">Upload your CV to build your profile.</p>
            )}
            <Link href="/app/profile">
              <Button size="sm" variant="secondary" className="mt-4">
                View profile
              </Button>
            </Link>
          </Card>
        </Reveal>

        <Reveal delay={0.06}>
          <Card className="p-6">
            <h3 className="text-sm font-medium text-ink mb-2">Latest analysis</h3>
            {lastJob ? (
              <p className="text-sm text-ink-muted leading-relaxed">
                {lastJob.universityName} — {lastJob.programName}
              </p>
            ) : (
              <p className="text-sm text-ink-faint italic">No universities yet.</p>
            )}
            <Link href={lastJob ? `/app/analysis/${lastJob.jobId}` : "/app/universities"}>
              <Button size="sm" variant="secondary" className="mt-4">
                {lastJob ? "View analysis" : "Choose a program"}
              </Button>
            </Link>
          </Card>
        </Reveal>
      </div>
    </div>
  );
}
