"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, ShieldCheck, FileSearch, GitCompareArrows } from "lucide-react";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/Button";
import { AnimatedBackground } from "@/components/landing/AnimatedBackground";
import { FlowDiagram } from "@/components/landing/FlowDiagram";
import { Reveal } from "@/components/Reveal";
import { useTheme } from "@/lib/theme";
import { Sun, Moon } from "lucide-react";

const FEATURES = [
  {
    icon: FileSearch,
    title: "Reads your real profile",
    desc: "Education, research, projects and experience extracted directly from your CV — nothing invented.",
  },
  {
    icon: GitCompareArrows,
    title: "Compares against the program",
    desc: "Retrieves current official program information and evaluates your fit against it.",
  },
  {
    icon: ShieldCheck,
    title: "Evidence, not guesses",
    desc: "Every conclusion links back to your profile or the program source. No fabricated odds.",
  },
];

export default function Landing() {
  const { theme, toggle } = useTheme();

  return (
    <main className="relative min-h-screen overflow-hidden">
      <AnimatedBackground />

      <header className="relative z-10 max-w-6xl mx-auto flex items-center justify-between px-6 py-6">
        <Logo />
        <div className="flex items-center gap-2">
          <button
            onClick={toggle}
            className="w-9 h-9 flex items-center justify-center rounded-lg text-ink-muted hover:bg-surface-2 transition-colors"
            aria-label="Toggle theme"
          >
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          <Link href="/app/documents">
            <Button variant="secondary" size="sm">
              Open app
            </Button>
          </Link>
        </div>
      </header>

      <section className="relative z-10 max-w-4xl mx-auto px-6 pt-16 pb-20 text-center flex flex-col items-center">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-accent bg-accent-soft border border-accent/20 rounded-full px-3 py-1 mb-6"
        >
          Evidence-based admissions analysis
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.05 }}
          className="text-4xl sm:text-5xl font-semibold tracking-tight text-ink leading-[1.1]"
        >
          Your graduate application,
          <br />
          understood.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.15 }}
          className="mt-5 text-lg text-ink-muted max-w-xl"
        >
          GradPilot reads your profile, understands your target programs, and shows you where you
          stand — with evidence.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.25 }}
          className="mt-8"
        >
          <Link href="/app/documents">
            <Button size="lg" className="group">
              Analyze my profile
              <ArrowRight size={16} className="transition-transform group-hover:translate-x-0.5" />
            </Button>
          </Link>
        </motion.div>

        <div className="mt-20 w-full">
          <FlowDiagram />
        </div>
      </section>

      <section className="relative z-10 max-w-5xl mx-auto px-6 pb-28">
        <div className="grid sm:grid-cols-3 gap-5">
          {FEATURES.map((f, i) => {
            const Icon = f.icon;
            return (
              <Reveal key={f.title} delay={i * 0.08} className="rounded-2xl border border-border bg-surface p-6">
                <div className="w-9 h-9 rounded-lg bg-accent-soft flex items-center justify-center mb-4">
                  <Icon size={17} className="text-accent" strokeWidth={1.8} />
                </div>
                <h3 className="font-medium text-ink mb-1.5">{f.title}</h3>
                <p className="text-sm text-ink-muted leading-relaxed">{f.desc}</p>
              </Reveal>
            );
          })}
        </div>
      </section>
    </main>
  );
}
