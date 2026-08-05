"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutGrid,
  UserCircle,
  FileStack,
  Building2,
  Sparkles,
  PenLine,
  ClipboardList,
  Settings,
  Sun,
  Moon,
} from "lucide-react";
import { Logo } from "./Logo";
import { useTheme } from "@/lib/theme";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/app/overview", label: "Overview", icon: LayoutGrid },
  { href: "/app/profile", label: "Profile", icon: UserCircle },
  { href: "/app/documents", label: "Documents", icon: FileStack },
  { href: "/app/universities", label: "Universities", icon: Building2 },
  { href: "/app/analysis", label: "Analysis", icon: Sparkles },
  { href: "/app/sop", label: "SOP", icon: PenLine },
  { href: "/app/applications", label: "Applications", icon: ClipboardList },
  { href: "/app/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { theme, toggle } = useTheme();

  return (
    <aside className="hidden md:flex flex-col w-60 shrink-0 border-r border-border bg-surface h-screen sticky top-0 px-3 py-4">
      <Link href="/" className="px-2 py-2 mb-2">
        <Logo size={22} />
      </Link>

      <nav className="flex flex-col gap-0.5 mt-2">
        {NAV.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className="relative flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors"
            >
              {active && (
                <motion.div
                  layoutId="sidebar-active"
                  transition={{ type: "spring", stiffness: 400, damping: 32 }}
                  className="absolute inset-0 bg-accent-soft rounded-lg"
                />
              )}
              <Icon
                size={16}
                strokeWidth={1.9}
                className={cn("relative z-10 shrink-0", active ? "text-accent" : "text-ink-faint")}
              />
              <span className={cn("relative z-10", active ? "text-accent font-medium" : "text-ink-muted")}>
                {item.label}
              </span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto">
        <button
          onClick={toggle}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-ink-muted hover:bg-surface-2 transition-colors"
        >
          {theme === "dark" ? <Sun size={16} strokeWidth={1.9} /> : <Moon size={16} strokeWidth={1.9} />}
          {theme === "dark" ? "Light mode" : "Dark mode"}
        </button>
      </div>
    </aside>
  );
}
