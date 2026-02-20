"use client";

type Variant = "idle" | "running" | "error" | "completed" | "pending" | "failed" | "success" | "default";

const COLORS: Record<Variant, { bg: string; text: string; dot?: string }> = {
  idle: { bg: "rgba(139,146,154,0.1)", text: "var(--text-muted)", dot: "var(--text-muted)" },
  running: { bg: "rgba(78,168,222,0.1)", text: "var(--info)", dot: "var(--info)" },
  error: { bg: "rgba(239,95,95,0.1)", text: "var(--error)", dot: "var(--error)" },
  failed: { bg: "rgba(239,95,95,0.1)", text: "var(--error)", dot: "var(--error)" },
  completed: { bg: "rgba(62,207,142,0.1)", text: "var(--success)", dot: "var(--success)" },
  success: { bg: "rgba(62,207,142,0.1)", text: "var(--success)", dot: "var(--success)" },
  pending: { bg: "rgba(245,166,35,0.1)", text: "var(--warning)", dot: "var(--warning)" },
  default: { bg: "rgba(139,146,154,0.1)", text: "var(--text-secondary)" },
};

export default function StatusBadge({ status, label }: { status: string; label?: string }) {
  const variant = (status in COLORS ? status : "default") as Variant;
  const color = COLORS[variant];

  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-medium"
      style={{ background: color.bg, color: color.text, fontFamily: "var(--font-mono)" }}
    >
      {color.dot && (
        <span
          className={`h-1.5 w-1.5 rounded-full ${variant === "running" ? "animate-pulse-dot" : ""}`}
          style={{ background: color.dot }}
        />
      )}
      {label || status}
    </span>
  );
}
