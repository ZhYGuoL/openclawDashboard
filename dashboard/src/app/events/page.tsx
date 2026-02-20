"use client";

import { useEvents } from "@/lib/hooks";
import Card from "@/components/Card";
import EmptyState from "@/components/EmptyState";
import { Activity, Loader2, Radio } from "lucide-react";

const EVENT_COLORS: Record<string, string> = {
  "meeting.started": "var(--info)",
  "meeting.round_start": "var(--info)",
  "meeting.round_end": "var(--info)",
  "meeting.completed": "var(--success)",
  "meeting.failed": "var(--error)",
  "agent.started": "var(--role-engineer)",
  "agent.completed": "var(--success)",
  "agent.error": "var(--error)",
  "memo.created": "var(--accent)",
  "task.created": "var(--warning)",
  "task.started": "var(--info)",
  "task.completed": "var(--success)",
  "task.failed": "var(--error)",
};

function getEventColor(type: string): string {
  return EVENT_COLORS[type] || "var(--text-muted)";
}

function formatPayload(payload: Record<string, unknown>): string[] {
  return Object.entries(payload)
    .filter(([, v]) => v !== null && v !== undefined && v !== "")
    .slice(0, 4)
    .map(([k, v]) => {
      const val = typeof v === "object" ? JSON.stringify(v).slice(0, 60) : String(v).slice(0, 60);
      return `${k}: ${val}`;
    });
}

export default function EventsPage() {
  const { data: events, isLoading } = useEvents(200);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8 animate-fade-in">
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold" style={{ color: "var(--text-primary)" }}>
            Events
          </h1>
          <span className="flex items-center gap-1.5 text-[11px] font-mono rounded-full px-2.5 py-0.5"
            style={{ background: "rgba(78,168,222,0.1)", color: "var(--info)" }}
          >
            <Radio size={10} className="animate-pulse-dot" />
            Live
          </span>
        </div>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>
          Real-time event stream from your project &middot; auto-refreshes every 5s
        </p>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center h-[40vh]">
          <Loader2 className="animate-spin" size={24} style={{ color: "var(--text-muted)" }} />
        </div>
      )}

      {!isLoading && (!events || events.length === 0) && (
        <Card>
          <EmptyState icon={<Activity size={32} />} message="No events yet. Events appear here in real-time as meetings run." />
        </Card>
      )}

      <div className="relative">
        {/* Timeline line */}
        <div
          className="absolute left-[19px] top-4 bottom-4 w-px"
          style={{ background: "var(--border)" }}
        />

        <div className="flex flex-col gap-1">
          {events?.map((event, i) => {
            const color = getEventColor(event.type);
            const payloadLines = formatPayload(event.payload_json);
            const time = new Date(event.created_at);

            return (
              <div
                key={event.id}
                className="relative flex gap-4 py-2.5 pl-0 animate-fade-in"
                style={{ animationDelay: `${Math.min(i * 15, 300)}ms` }}
              >
                {/* Dot */}
                <div className="relative z-10 flex h-10 w-10 items-center justify-center shrink-0">
                  <div className="h-2.5 w-2.5 rounded-full" style={{ background: color }} />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 rounded-lg p-3 -mt-0.5"
                  style={{ background: "var(--bg-surface)", border: "1px solid var(--border-subtle)" }}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-xs font-semibold font-mono" style={{ color }}>
                      {event.type}
                    </span>
                    <span className="text-[10px] font-mono shrink-0" style={{ color: "var(--text-muted)" }}>
                      {time.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
                      {" "}
                      {time.toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                    </span>
                  </div>

                  {payloadLines.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
                      {payloadLines.map((line, j) => (
                        <span key={j} className="text-[11px] font-mono" style={{ color: "var(--text-muted)" }}>
                          {line}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
