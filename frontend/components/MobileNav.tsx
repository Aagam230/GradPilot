"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutGrid,
  UserCircle,
  FileStack,
  Building2,
  Sparkles,
} from "lucide-react";
import { Logo } from "./Logo";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/app/overview", label: "Overview", icon: LayoutGrid },
  { href: "/app/profile", label: "Profile", icon: UserCircle },
  { href: "/app/documents", label: "Documents", icon: FileStack },
  { href: "/app/universities", label: "Universities", icon: Building2 },
  { href: "/app/analysis", label: "Analysis", icon: Sparkles },
];

export function MobileNav() {
  const pathname = usePathname();
  return (
    <div className="md:hidden sticky top-0 z-20 bg-surface/90 backdrop-blur-sm border-b border-border">
      <div className="flex items-center justify-between px-5 py-3">
        <Link href="/">
          <Logo size={20} />
        </Link>
      </div>
      <nav className="flex gap-1 px-3 pb-2 overflow-x-auto">
        {NAV.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs whitespace-nowrap shrink-0",
                active ? "bg-accent-soft text-accent font-medium" : "text-ink-muted"
              )}
            >
              <Icon size={13} />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
