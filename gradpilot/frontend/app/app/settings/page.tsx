"use client";
import { Settings as SettingsIcon, Sun, Moon, Trash2 } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { useTheme } from "@/lib/theme";
import { useAppState } from "@/lib/store";

export default function SettingsPage() {
  const { theme, toggle } = useTheme();
  const { clearProfile } = useAppState();

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight mb-1">Settings</h1>
      <p className="text-ink-muted mb-8">Local preferences for this device.</p>

      <div className="space-y-4 max-w-lg">
        <Card className="p-5 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-ink flex items-center gap-2">
              <SettingsIcon size={14} /> Appearance
            </p>
            <p className="text-xs text-ink-faint mt-0.5">Switch between light and dark mode.</p>
          </div>
          <Button size="sm" variant="secondary" onClick={toggle}>
            {theme === "dark" ? <Sun size={14} /> : <Moon size={14} />}
            {theme === "dark" ? "Light" : "Dark"}
          </Button>
        </Card>

        <Card className="p-5 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-ink flex items-center gap-2">
              <Trash2 size={14} /> Clear local profile
            </p>
            <p className="text-xs text-ink-faint mt-0.5">Removes your uploaded profile from this browser.</p>
          </div>
          <Button size="sm" variant="secondary" onClick={clearProfile}>
            Clear
          </Button>
        </Card>
      </div>
    </div>
  );
}
