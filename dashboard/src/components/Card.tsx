"use client";

import { ReactNode } from "react";

export default function Card({
  children,
  className = "",
  padding = true,
  style,
}: {
  children: ReactNode;
  className?: string;
  padding?: boolean;
  style?: React.CSSProperties;
}) {
  return (
    <div
      className={`rounded-xl ${padding ? "p-5" : ""} ${className}`}
      style={{
        background: "var(--bg-surface)",
        border: "1px solid var(--border)",
        ...style,
      }}
    >
      {children}
    </div>
  );
}

export function CardHeader({ title, action }: { title: string; action?: ReactNode }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
        {title}
      </h2>
      {action}
    </div>
  );
}
