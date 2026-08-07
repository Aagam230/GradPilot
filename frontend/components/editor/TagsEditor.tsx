"use client";

export function TagsEditor({
  value,
  onChange,
  placeholder,
}: {
  value: string[];
  onChange: (v: string[]) => void;
  placeholder?: string;
}) {
  return (
    <textarea
      value={value.join(", ")}
      placeholder={placeholder || "Comma-separated"}
      onChange={(e) =>
        onChange(
          e.target.value
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean)
        )
      }
      rows={2}
      className="w-full text-sm border border-border bg-surface-2/40 rounded-lg px-2.5 py-1.5 outline-none focus:ring-2 focus:ring-accent/30"
    />
  );
}
