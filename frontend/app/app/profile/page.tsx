"use client";
import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  GraduationCap,
  FlaskConical,
  Boxes,
  Briefcase,
  Award,
  BookOpen,
  PenLine,
  FileStack,
  UploadCloud,
  Pencil,
  Check,
  X,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/EmptyState";
import { Reveal } from "@/components/Reveal";
import { ListFieldEditor } from "@/components/editor/ListFieldEditor";
import { TagsEditor } from "@/components/editor/TagsEditor";
import { useAppState } from "@/lib/store";
import { updateProfile } from "@/lib/api";

const EDITABLE_ARRAY_FIELDS = {
  education: [
    { key: "degree", label: "Degree" },
    { key: "field", label: "Field" },
    { key: "institution", label: "Institution" },
    { key: "gpa", label: "GPA" },
    { key: "years", label: "Years" },
  ],
  research_experience: [
    { key: "title", label: "Title" },
    { key: "duration", label: "Duration" },
    { key: "description", label: "Description", textarea: true },
  ],
  projects: [
    { key: "title", label: "Title" },
    { key: "tech", label: "Tech (comma-separated)" },
    { key: "description", label: "Description", textarea: true },
  ],
  work_experience: [
    { key: "role", label: "Role" },
    { key: "organization", label: "Organization" },
    { key: "duration", label: "Duration" },
    { key: "description", label: "Description", textarea: true },
  ],
  publications: [
    { key: "title", label: "Title" },
    { key: "venue", label: "Venue" },
    { key: "year", label: "Year" },
  ],
  test_scores: [
    { key: "test", label: "Test" },
    { key: "score", label: "Score" },
  ],
} as const;

const EMPTY_ITEMS: Record<string, Record<string, any>> = {
  education: { degree: "", field: "", institution: "", gpa: "", years: "" },
  research_experience: { title: "", duration: "", description: "" },
  projects: { title: "", tech: "", description: "" },
  work_experience: { role: "", organization: "", duration: "", description: "" },
  publications: { title: "", venue: "", year: "" },
  test_scores: { test: "", score: "" },
};

function toDraft(profile: any) {
  return {
    name: profile.name || "",
    summary: profile.summary || "",
    goals_and_motivation: profile.goals_and_motivation || "",
    education: profile.education || [],
    research_experience: profile.research_experience || [],
    projects: (profile.projects || []).map((p: any) => ({ ...p, tech: (p.tech || []).join(", ") })),
    work_experience: profile.work_experience || [],
    publications: profile.publications || [],
    test_scores: profile.test_scores || [],
    skills: profile.skills || [],
    awards: profile.awards || [],
    coursework_highlights: profile.coursework_highlights || [],
  };
}

function fromDraft(draft: any) {
  return {
    ...draft,
    projects: draft.projects.map((p: any) => ({
      ...p,
      tech: typeof p.tech === "string" ? p.tech.split(",").map((t: string) => t.trim()).filter(Boolean) : p.tech,
    })),
  };
}

export default function ProfilePage() {
  const { profile, documents, setProfile, profileId } = useAppState();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  function startEditing() {
    setDraft(toDraft(profile));
    setEditing(true);
    setError(null);
  }

  function cancelEditing() {
    setEditing(false);
    setDraft(null);
    setError(null);
  }

  async function saveEditing() {
    if (!profileId || !draft) return;
    setSaving(true);
    setError(null);
    try {
      const payload = fromDraft(draft);
      const data = await updateProfile(profileId, payload);
      setProfile(data.profile_id, data.profile, data.documents);
      setEditing(false);
      setDraft(null);
    } catch (e: any) {
      setError(e.message || "Could not save changes");
    } finally {
      setSaving(false);
    }
  }

  const active = editing ? draft : profile;
  const education = active.education || [];
  const research = active.research_experience || [];
  const projects = active.projects || [];
  const work = active.work_experience || [];
  const publications = active.publications || [];
  const skills = active.skills || [];
  const testScores = active.test_scores || [];
  const awards = active.awards || [];
  const coursework = active.coursework_highlights || [];
  const goals = active.goals_and_motivation as string | null;

  return (
    <div>
      <div className="flex items-start justify-between mb-8 gap-4">
        <div className="flex-1">
          {editing ? (
            <input
              value={draft.name}
              onChange={(e) => setDraft({ ...draft, name: e.target.value })}
              placeholder="Your name"
              className="text-2xl font-semibold tracking-tight mb-1 bg-transparent border-b border-border focus:border-accent outline-none w-full"
            />
          ) : (
            <h1 className="text-2xl font-semibold tracking-tight mb-1">{profile.name || "Your profile"}</h1>
          )}
          {editing ? (
            <textarea
              value={draft.summary}
              onChange={(e) => setDraft({ ...draft, summary: e.target.value })}
              placeholder="Summary"
              rows={2}
              className="text-sm text-ink-muted bg-transparent border border-border rounded-lg px-2 py-1 outline-none focus:ring-2 focus:ring-accent/30 w-full mt-1"
            />
          ) : (
            <p className="text-ink-muted text-sm">
              Built from {documents.length} document{documents.length === 1 ? "" : "s"} · {profile.summary}
            </p>
          )}
        </div>

        {editing ? (
          <div className="flex items-center gap-2 shrink-0">
            <Button size="sm" variant="secondary" onClick={cancelEditing} disabled={saving}>
              <X size={14} /> Cancel
            </Button>
            <Button size="sm" onClick={saveEditing} disabled={saving}>
              <Check size={14} /> {saving ? "Saving…" : "Save"}
            </Button>
          </div>
        ) : (
          <Button size="sm" variant="secondary" onClick={startEditing} className="shrink-0">
            <Pencil size={13} /> Edit
          </Button>
        )}
      </div>

      {error && (
        <div className="mb-6 text-sm text-reach bg-reach/10 border border-reach/20 rounded-lg px-3 py-2">
          {error}
        </div>
      )}
      {editing && (
        <div className="mb-6 text-xs text-ink-faint bg-surface-2/60 border border-border rounded-lg px-3 py-2">
          Correct anything GradPilot got wrong — your edits are kept even if you upload more
          documents later.
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {(goals || editing) && (
            <Reveal delay={0.02}>
              <Card className="p-5 bg-accent-soft/30 border-accent/20">
                <h2 className="flex items-center gap-2 text-sm font-medium text-ink mb-2">
                  <PenLine size={15} className="text-accent" strokeWidth={1.8} />
                  Goals &amp; motivation
                </h2>
                {editing ? (
                  <textarea
                    value={draft.goals_and_motivation}
                    onChange={(e) => setDraft({ ...draft, goals_and_motivation: e.target.value })}
                    rows={3}
                    className="w-full text-sm border border-border bg-surface-2/40 rounded-lg px-2.5 py-1.5 outline-none focus:ring-2 focus:ring-accent/30"
                  />
                ) : (
                  <>
                    <p className="text-sm text-ink-muted leading-relaxed">{goals}</p>
                    <p className="text-[11px] text-ink-faint mt-2">From your Statement of Purpose.</p>
                  </>
                )}
              </Card>
            </Reveal>
          )}

          <Reveal>
            <Section icon={GraduationCap} title="Academics">
              {editing ? (
                <ListFieldEditor
                  items={education}
                  fields={EDITABLE_ARRAY_FIELDS.education as any}
                  emptyItem={EMPTY_ITEMS.education}
                  onChange={(items) => setDraft({ ...draft, education: items })}
                />
              ) : education.length === 0 ? (
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
              {(coursework.length > 0 || editing) && (
                <div className="mt-4 pt-4 border-t border-border">
                  <p className="text-xs font-medium text-ink-faint uppercase tracking-wide mb-2">
                    Coursework highlights
                  </p>
                  {editing ? (
                    <TagsEditor
                      value={coursework}
                      onChange={(v) => setDraft({ ...draft, coursework_highlights: v })}
                    />
                  ) : (
                    <>
                      <div className="flex flex-wrap gap-1.5">
                        {coursework.map((c: string) => (
                          <Tag key={c}>{c}</Tag>
                        ))}
                      </div>
                      <p className="text-[11px] text-ink-faint mt-2">From your transcript.</p>
                    </>
                  )}
                </div>
              )}
            </Section>
          </Reveal>

          <Reveal delay={0.05}>
            <Section icon={FlaskConical} title="Research">
              {editing ? (
                <ListFieldEditor
                  items={research}
                  fields={EDITABLE_ARRAY_FIELDS.research_experience as any}
                  emptyItem={EMPTY_ITEMS.research_experience}
                  onChange={(items) => setDraft({ ...draft, research_experience: items })}
                />
              ) : research.length === 0 ? (
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
              {editing ? (
                <ListFieldEditor
                  items={projects}
                  fields={EDITABLE_ARRAY_FIELDS.projects as any}
                  emptyItem={EMPTY_ITEMS.projects}
                  onChange={(items) => setDraft({ ...draft, projects: items })}
                />
              ) : projects.length === 0 ? (
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
              {editing ? (
                <ListFieldEditor
                  items={work}
                  fields={EDITABLE_ARRAY_FIELDS.work_experience as any}
                  emptyItem={EMPTY_ITEMS.work_experience}
                  onChange={(items) => setDraft({ ...draft, work_experience: items })}
                />
              ) : work.length === 0 ? (
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

          {(publications.length > 0 || editing) && (
            <Reveal delay={0.2}>
              <Section icon={BookOpen} title="Publications">
                {editing ? (
                  <ListFieldEditor
                    items={publications}
                    fields={EDITABLE_ARRAY_FIELDS.publications as any}
                    emptyItem={EMPTY_ITEMS.publications}
                    onChange={(items) => setDraft({ ...draft, publications: items })}
                  />
                ) : (
                  <Timeline
                    items={publications.map((p: any) => ({
                      title: p.title,
                      subtitle: p.venue,
                      meta: p.year,
                    }))}
                  />
                )}
              </Section>
            </Reveal>
          )}
        </div>

        <div className="space-y-6">
          <Reveal>
            <Card className="p-5">
              <h3 className="text-sm font-medium text-ink mb-3 flex items-center gap-1.5">
                <FileStack size={14} className="text-accent" /> Source documents
              </h3>
              {documents.length === 0 ? (
                <EmptyRow text="No documents uploaded." />
              ) : (
                <ul className="space-y-2">
                  {documents.map((d) => (
                    <li key={d.id} className="flex items-center justify-between text-sm">
                      <span className="text-ink-muted capitalize">{d.doc_type.replace("_", " / ")}</span>
                      <span className="text-xs text-ink-faint truncate max-w-[110px]">{d.filename}</span>
                    </li>
                  ))}
                </ul>
              )}
              <Link href="/app/documents">
                <Button size="sm" variant="secondary" className="mt-4 w-full">
                  Manage documents
                </Button>
              </Link>
            </Card>
          </Reveal>

          <Reveal delay={0.05}>
            <Card className="p-5">
              <h3 className="text-sm font-medium text-ink mb-3">Skills</h3>
              {editing ? (
                <TagsEditor value={skills} onChange={(v) => setDraft({ ...draft, skills: v })} />
              ) : skills.length === 0 ? (
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
              {editing ? (
                <ListFieldEditor
                  items={testScores}
                  fields={EDITABLE_ARRAY_FIELDS.test_scores as any}
                  emptyItem={EMPTY_ITEMS.test_scores}
                  onChange={(items) => setDraft({ ...draft, test_scores: items })}
                />
              ) : testScores.length === 0 ? (
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
              {editing ? (
                <TagsEditor value={awards} onChange={(v) => setDraft({ ...draft, awards: v })} />
              ) : awards.length === 0 ? (
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
