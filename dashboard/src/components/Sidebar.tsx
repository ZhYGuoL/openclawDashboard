"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  MessagesSquare,
  ListTodo,
  Activity,
  Settings,
  Zap,
} from "lucide-react";

const NAV = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/memos", label: "Memos", icon: FileText },
  { href: "/meetings", label: "Meetings", icon: MessagesSquare },
  { href: "/tasks", label: "Tasks", icon: ListTodo },
  { href: "/events", label: "Events", icon: Activity },
  { href: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-56 flex-col border-r"
      style={{ background: "var(--bg-surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center gap-2.5 px-5 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg"
          style={{ background: "var(--accent-dim)" }}
        >
          <Zap size={16} style={{ color: "var(--accent)" }} />
        </div>
        <div>
          <div className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>
            OpenClaw
          </div>
          <div className="text-[10px] font-medium tracking-wider uppercase"
            style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
          >
            Dashboard
          </div>
        </div>
      </div>

      <div className="mt-1 px-3">
        <div className="text-[10px] font-semibold tracking-wider uppercase px-2 mb-2"
          style={{ color: "var(--text-muted)" }}
        >
          Navigation
        </div>
        <nav className="flex flex-col gap-0.5">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium transition-colors"
                style={{
                  color: active ? "var(--text-primary)" : "var(--text-secondary)",
                  background: active ? "var(--bg-surface-raised)" : "transparent",
                }}
              >
                <Icon size={16} style={{ color: active ? "var(--accent)" : "var(--text-muted)" }} />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="mt-auto px-5 pb-5">
        <div className="rounded-lg p-3 text-xs"
          style={{ background: "var(--bg-surface-raised)", border: "1px solid var(--border-subtle)" }}
        >
          <div className="font-mono text-[10px] mb-1" style={{ color: "var(--text-muted)" }}>
            PROJECT ID
          </div>
          <div className="font-mono truncate" style={{ color: "var(--text-secondary)", fontSize: "10px" }}>
            9b7d36e6-b590-...
          </div>
        </div>
      </div>
    </aside>
  );
}
