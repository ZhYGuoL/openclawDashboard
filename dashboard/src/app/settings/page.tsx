"use client";

import { useState, useEffect } from "react";
import { Smartphone, Check, Loader2 } from "lucide-react";
import Card, { CardHeader } from "@/components/Card";
import { useProject } from "@/lib/hooks";
import { api, PROJECT_ID } from "@/lib/api";

export default function SettingsPage() {
  const { data: project, mutate } = useProject();
  const [phone, setPhone] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (project?.notify_phone) setPhone(project.notify_phone);
  }, [project?.notify_phone]);

  async function handleSave() {
    setSaving(true);
    setSaved(false);
    try {
      await api.updateProject(PROJECT_ID, {
        notify_phone: phone.trim() || null,
      });
      await mutate();
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  const dirty = phone.trim() !== (project?.notify_phone ?? "");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
          Settings
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
          Configure notifications and project preferences.
        </p>
      </div>

      <Card>
        <CardHeader title="iMessage Notifications" />
        <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>
          Get a recap of the most important points from each investor memo sent straight to your
          phone via iMessage when a meeting finishes.
        </p>

        <div className="flex items-center gap-3">
          <div
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
            style={{ background: "var(--accent-dim)" }}
          >
            <Smartphone size={18} style={{ color: "var(--accent)" }} />
          </div>

          <input
            type="tel"
            placeholder="+1 (555) 123-4567"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && dirty) handleSave();
            }}
            className="flex-1 rounded-lg border px-3 py-2 text-sm outline-none transition-colors focus:ring-1"
            style={{
              background: "var(--bg-root)",
              borderColor: "var(--border)",
              color: "var(--text-primary)",
              // @ts-expect-error CSS custom property for ring color
              "--tw-ring-color": "var(--accent)",
            }}
          />

          <button
            onClick={handleSave}
            disabled={!dirty || saving}
            className="flex items-center gap-1.5 rounded-lg px-4 py-2 text-sm font-medium transition-opacity disabled:opacity-40"
            style={{
              background: saved ? "var(--success)" : "var(--accent)",
              color: "#fff",
            }}
          >
            {saving ? (
              <Loader2 size={14} className="animate-spin" />
            ) : saved ? (
              <Check size={14} />
            ) : null}
            {saving ? "Saving…" : saved ? "Saved" : "Save"}
          </button>
        </div>

        {project?.notify_phone && (
          <p className="text-xs mt-3" style={{ color: "var(--text-muted)" }}>
            Currently sending recaps to <span className="font-mono">{project.notify_phone}</span>
          </p>
        )}
      </Card>
    </div>
  );
}
