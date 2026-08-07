"use client";
import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";

export type FieldConfig = { key: string; label: string; placeholder?: string; textarea?: boolean };

export function ListFieldEditor({
  items,
  fields,
  onChange,
  emptyItem,
}: {
  items: Record<string, any>[];
  fields: FieldConfig[];
  onChange: (items: Record<string, any>[]) => void;
  emptyItem: Record<string, any>;
}) {
  function updateItem(i: number, key: string, value: string) {
    const next = items.map((it, idx) => (idx === i ? { ...it, [key]: value } : it));
    onChange(next);
  }

  function removeItem(i: number) {
    onChange(items.filter((_, idx) => idx !== i));
  }

  function addItem() {
    onChange([...items, { ...emptyItem }]);
  }

  return (
    <div className="space-y-3">
      {items.map((item, i) => (
        <div key={i} className="rounded-xl border border-border p-3 relative">
          <button
            onClick={() => removeItem(i)}
            className="absolute top-2 right-2 text-ink-faint hover:text-reach"
            aria-label="Remove"
          >
            <Trash2 size={13} />
          </button>
          <div className="grid sm:grid-cols-2 gap-2 pr-6">
            {fields.map((f) =>
              f.textarea ? (
                <textarea
                  key={f.key}
                  value={item[f.key] ?? ""}
                  placeholder={f.placeholder || f.label}
                  onChange={(e) => updateItem(i, f.key, e.target.value)}
                  rows={2}
                  className="sm:col-span-2 text-sm border border-border bg-surface-2/40 rounded-lg px-2.5 py-1.5 outline-none focus:ring-2 focus:ring-accent/30"
                />
              ) : (
                <input
                  key={f.key}
                  value={item[f.key] ?? ""}
                  placeholder={f.placeholder || f.label}
                  onChange={(e) => updateItem(i, f.key, e.target.value)}
                  className="text-sm border border-border bg-surface-2/40 rounded-lg px-2.5 py-1.5 outline-none focus:ring-2 focus:ring-accent/30"
                />
              )
            )}
          </div>
        </div>
      ))}
      <Button size="sm" variant="secondary" onClick={addItem}>
        <Plus size={13} /> Add
      </Button>
    </div>
  );
}
