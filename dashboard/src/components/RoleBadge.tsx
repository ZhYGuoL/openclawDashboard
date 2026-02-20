"use client";

import type { AgentRole } from "@/lib/types";

const ROLE_COLORS: Record<AgentRole, string> = {
  ceo: "var(--role-ceo)",
  pm: "var(--role-pm)",
  engineer: "var(--role-engineer)",
  designer: "var(--role-designer)",
  analyst: "var(--role-analyst)",
  memo_writer: "var(--role-memo)",
};

const ROLE_LABELS: Record<AgentRole, string> = {
  ceo: "CEO",
  pm: "PM",
  engineer: "Engineer",
  designer: "Designer",
  analyst: "Analyst",
  memo_writer: "Memo Writer",
};

export default function RoleBadge({ role }: { role: AgentRole }) {
  const color = ROLE_COLORS[role] || "var(--text-muted)";

  return (
    <span
      className="inline-flex items-center gap-1.5 rounded px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wider"
      style={{
        background: `color-mix(in srgb, ${color} 12%, transparent)`,
        color,
        fontFamily: "var(--font-mono)",
      }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />
      {ROLE_LABELS[role] || role}
    </span>
  );
}
