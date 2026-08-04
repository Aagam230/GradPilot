"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  GraduationCap,
  FlaskConical,
  Boxes,
  Briefcase,
  Award,
  BookOpen,
  UploadCloud,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/EmptyState";
import { Reveal } from "@/components/Reveal";
import { useAppState } from "@/lib/store";

export default function ProfilePage() {
  const { profile, fileName } = useAppState();

  if (!profile) {
    return (
      <div>
        <h1 className="text-2xl font-semibold tracking-tight mb-1">Profile</h1>
        <p className="text-ink-muted mb-8">Your extracted profile will appear here.</p>
        <EmptyState
          icon={UploadCloud}
          title="Upload your CV to build your profile"
          description="GradPilot extracts your education, research, projects and experience directly from your CV."
          action={
            <Link href="/app/documents">
              <Button size="sm">Upload CV</Button>
            </Link>
          }
        />
      </div>
    );
  }

  const education = profile.education || [];
  const research = profile.research_experience || [];
  const projects = profile.projects || [];
  const work = profile.work_experience || [];
  const publications = profile.publications || [];
  const skills = profile.skills || [];
  const testScores = profile.test_scores || [];
  const awards = profile.awards || [];

  return (
    <div>
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight mb-1">
            {profile.name || "Your profile"}
          </h1>
          <p className="text-ink-muted text-sm">
            Extracted from {fileName || "your CV"} · {profile.summary}
          </p>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Reveal>
            <Section icon={GraduationCap} title="Academics">
              {education.length === 0 ? (
                <EmptyRow text="No education entries found." />
              ) : (
                <Timeline
                  items={education.map((e: any) => ({
                    title: `${e.degree || ""} ${e.field ? "in " + e.field : ""}`.trim(),
                    subtitle: e.institution,
                    meta: [e.years, e.gpa ? `GPA ${e.gpa}` : null].filter(Boolean).join(" · "),
                  }))}
                />
              )}
            </Section>
          </Reveal>

          <Reveal delay={0.05}>
            <Section icon={FlaskConical} title="Research">
              {research.length === 0 ? (
                <EmptyRow text="No research experience found." />
              ) : (
                <Timeline
                  items={research.map((r: any) => ({
                    title: r.title,
                    subtitle: r.description,
                    meta: r.duration,
                  }))}
                />
              )}
            </Section>
          </Reveal>

          <Reveal delay={0.1}>
            <Section icon={Boxes} title="Projects">
              {projects.length === 0 ? (
                <EmptyRow text="No projects found." />
              ) : (
                <div className="grid sm:grid-cols-2 gap-3">
                  {projects.map((p: any, i: number) => (
                    <div key={i} className="rounded-xl border border-border p-4">
                      <p className="text-sm font-medium text-ink mb-1">{p.title}</p>
                      <p className="text-xs text-ink-muted leading-relaxed mb-2">{p.description}</p>
                      <div className="flex flex-wrap gap-1">
                        {(p.tech || []).map((t: string) => (
                          <Tag key={t}>{t}</Tag>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Section>
          </Reveal>

          <Reveal delay={0.15}>
            <Section icon={Briefcase} title="Experience">
              {work.length === 0 ? (
                <EmptyRow text="No work experience found." />
              ) : (
                <Timeline
                  items={work.map((w: any) => ({
                    title: `${w.role || ""}${w.organization ? " · " + w.organization : ""}`,
                    subtitle: w.description,
                    meta: w.duration,
                  }))}
                />
              )}
            </Section>
          </Reveal>

          {publications.length > 0 && (
            <Reveal delay={0.2}>
              <Section icon={BookOpen} title="Publications">
                <Timeline
                  items={publications.map((p: any) => ({
                    title: p.title,
                    subtitle: p.venue,
                    meta: p.year,
                  }))}
                />
              </Section>
            </Reveal>
          )}
        </div>

        <div className="space-y-6">
          <Reveal delay={0.05}>
            <Card className="p-5">
              <h3 className="text-sm font-medium text-ink mb-3">Skills</h3>
              {skills.length === 0 ? (
                <EmptyRow text="No skills listed." />
              ) : (
                <div className="flex flex-wrap gap-1.5">
                  {skills.map((s: string) => (
                    <Tag key={s}>{s}</Tag>
                  ))}
                </div>
              )}
            </Card>
          </Reveal>

          <Reveal delay={0.1}>
            <Card className="p-5">
              <h3 className="text-sm font-medium text-ink mb-3 flex items-center gap-1.5">
                <Award size={14} className="text-accent" /> Test scores
              </h3>
              {testScores.length === 0 ? (
                <EmptyRow text="No test scores listed." />
              ) : (
                <div className="space-y-2">
                  {testScores.map((t: any, i: number) => (
                    <div key={i} className="flex justify-between text-sm">
                      <span className="text-ink-muted">{t.test}</span>
                      <span className="font-medium text-ink">{t.score}</span>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </Reveal>

          <Reveal delay={0.15}>
            <Card className="p-5">
              <h3 className="text-sm font-medium text-ink mb-3">Awards</h3>
              {awards.length === 0 ? (
                <EmptyRow text="No awards listed." />
              ) : (
                <ul className="space-y-1.5">
                  {awards.map((a: string, i: number) => (
                    <li key={i} className="text-sm text-ink-muted">
                      · {a}
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </Reveal>
        </div>
      </div>
    </div>
  );
}

function Section({ icon: Icon, title, children }: { icon: any; title: string; children: React.ReactNode }) {
  return (
    <Card className="p-5">
      <h2 className="flex items-center gap-2 text-sm font-medium text-ink mb-4">
        <Icon size={15} className="text-accent" strokeWidth={1.8} />
        {title}
      </h2>
      {children}
    </Card>
  );
}

function Timeline({ items }: { items: { title: string; subtitle?: string; meta?: string }[] }) {
  return (
    <div className="relative pl-4 space-y-5 before:absolute before:left-[3px] before:top-1 before:bottom-1 before:w-px before:bg-border">
      {items.map((item, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, x: -6 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: i * 0.05, duration: 0.3 }}
          className="relative"
        >
          <span className="absolute -left-4 top-1.5 w-1.5 h-1.5 rounded-full bg-accent" />
          <p className="text-sm font-medium text-ink">{item.title}</p>
          {item.subtitle && <p className="text-xs text-ink-muted mt-0.5">{item.subtitle}</p>}
          {item.meta && <p className="text-[11px] text-ink-faint mt-1">{item.meta}</p>}
        </motion.div>
      ))}
    </div>
  );
}

function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="text-xs px-2 py-1 rounded-full bg-surface-2 border border-border text-ink-muted">
      {children}
    </span>
  );
}

function EmptyRow({ text }: { text: string }) {
  return <p className="text-sm text-ink-faint italic">{text}</p>;
}
