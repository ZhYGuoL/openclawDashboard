"use client";

import { ReactNode } from "react";

export default function EmptyState({ icon, message }: { icon: ReactNode; message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3">
      <div style={{ color: "var(--text-muted)" }}>{icon}</div>
      <p className="text-sm" style={{ color: "var(--text-muted)" }}>
        {message}
      </p>
    </div>
  );
}
