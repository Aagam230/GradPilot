"use client";
import { Sidebar } from "@/components/Sidebar";
import { MobileNav } from "@/components/MobileNav";
import { PageTransition } from "@/components/PageTransition";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 min-w-0">
        <MobileNav />
        <div className="max-w-5xl mx-auto px-5 sm:px-8 py-8 sm:py-12">
          <PageTransition>{children}</PageTransition>
        </div>
      </div>
    </div>
  );
}
