"use client";

import { useProject, useAgents, useEvents, useMemos, useTasks } from "@/lib/hooks";
import Card, { CardHeader } from "@/components/Card";
import StatusBadge from "@/components/StatusBadge";
import RoleBadge from "@/components/RoleBadge";
import TimeAgo from "@/components/TimeAgo";
import {
  Users,
  FileText,
  Activity,
  ListTodo,
  ArrowRight,
  Loader2,
} from "lucide-react";
import Link from "next/link";

function StatCard({
  label,
  value,
  icon: Icon,
  href,
  delay,
}: {
  label: string;
  value: number | string;
  icon: React.ElementType;
  href: string;
  delay: number;
}) {
  return (
    <Link href={href}>
      <Card className="group cursor-pointer transition-colors hover:!border-[var(--border)]"
        padding={true}
      >
        <div className="animate-fade-in" style={{ animationDelay: `${delay}ms` }}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg"
              style={{ background: "var(--accent-dim)" }}
            >
              <Icon size={16} style={{ color: "var(--accent)" }} />
            </div>
            <ArrowRight size={14} style={{ color: "var(--text-muted)" }}
              className="opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <div className="text-2xl font-bold font-mono" style={{ color: "var(--text-primary)" }}>
            {value}
          </div>
          <div className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
            {label}
          </div>
        </div>
      </Card>
    </Link>
  );
}

export default function OverviewPage() {
  const { data: project } = useProject();
  const { data: agents } = useAgents();
  const { data: events } = useEvents(10);
  const { data: memos } = useMemos();
  const { data: tasks } = useTasks();

  const loading = !project;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="animate-spin" size={24} style={{ color: "var(--text-muted)" }} />
      </div>
    );
  }

  const runningAgents = agents?.filter((a) => a.status === "running").length ?? 0;
  const completedTasks = tasks?.filter((t) => t.status === "completed").length ?? 0;

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8 animate-fade-in">
        <h1 className="text-xl font-bold" style={{ color: "var(--text-primary)" }}>
          {project.name}
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>
          Created {new Date(project.created_at).toLocaleDateString("en-US", {
            month: "long",
            day: "numeric",
            year: "numeric",
          })}
        </p>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard label="Agents" value={agents?.length ?? 0} icon={Users} href="/meetings" delay={0} />
        <StatCard label="Memos" value={memos?.length ?? 0} icon={FileText} href="/memos" delay={50} />
        <StatCard label="Tasks" value={tasks?.length ?? 0} icon={ListTodo} href="/tasks" delay={100} />
        <StatCard label="Events" value={events?.length ?? 0} icon={Activity} href="/events" delay={150} />
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* Agents Panel */}
        <Card>
          <CardHeader
            title="Agent Roster"
            action={
              runningAgents > 0 ? (
                <StatusBadge status="running" label={`${runningAgents} active`} />
              ) : null
            }
          />
          <div className="flex flex-col gap-2.5">
            {agents?.map((agent) => (
              <div
                key={agent.id}
                className="flex items-center justify-between rounded-lg p-2.5"
                style={{ background: "var(--bg-surface-raised)" }}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold"
                    style={{
                      background: `var(--role-${agent.role})`,
                      color: "var(--bg-root)",
                    }}
                  >
                    {agent.name.charAt(0)}
                  </div>
                  <div>
                    <div className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
                      {agent.name}
                    </div>
                    <RoleBadge role={agent.role} />
                  </div>
                </div>
                <StatusBadge status={agent.status} />
              </div>
            ))}
            {(!agents || agents.length === 0) && (
              <p className="text-xs text-center py-6" style={{ color: "var(--text-muted)" }}>
                No agents configured
              </p>
            )}
          </div>
        </Card>

        {/* Recent Memos */}
        <Card>
          <CardHeader
            title="Recent Memos"
            action={
              <Link href="/memos" className="text-[11px] font-medium"
                style={{ color: "var(--accent)" }}
              >
                View all
              </Link>
            }
          />
          <div className="flex flex-col gap-2">
            {memos?.slice(0, 4).map((memo) => (
              <Link
                key={memo.id}
                href={`/memos/${memo.id}`}
                className="block rounded-lg p-3 transition-colors"
                style={{ background: "var(--bg-surface-raised)" }}
              >
                <div className="text-sm font-medium mb-1 truncate" style={{ color: "var(--text-primary)" }}>
                  {memo.title}
                </div>
                <TimeAgo date={memo.created_at} />
              </Link>
            ))}
            {(!memos || memos.length === 0) && (
              <p className="text-xs text-center py-6" style={{ color: "var(--text-muted)" }}>
                No memos yet
              </p>
            )}
          </div>
        </Card>

        {/* Recent Events */}
        <Card>
          <CardHeader
            title="Latest Events"
            action={
              <Link href="/events" className="text-[11px] font-medium"
                style={{ color: "var(--accent)" }}
              >
                View all
              </Link>
            }
          />
          <div className="flex flex-col gap-1.5">
            {events?.slice(0, 6).map((event) => (
              <div
                key={event.id}
                className="flex items-center justify-between rounded-lg px-3 py-2"
                style={{ background: "var(--bg-surface-raised)" }}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className="h-1.5 w-1.5 rounded-full shrink-0"
                    style={{ background: "var(--accent)" }}
                  />
                  <span className="text-xs font-mono truncate" style={{ color: "var(--text-secondary)" }}>
                    {event.type}
                  </span>
                </div>
                <TimeAgo date={event.created_at} />
              </div>
            ))}
            {(!events || events.length === 0) && (
              <p className="text-xs text-center py-6" style={{ color: "var(--text-muted)" }}>
                No events yet
              </p>
            )}
          </div>
        </Card>

        {/* Recent Tasks - full width */}
        {tasks && tasks.length > 0 && (
          <div className="col-span-3">
            <Card>
              <CardHeader
                title="Recent Tasks"
                action={
                  <Link href="/tasks" className="text-[11px] font-medium" style={{ color: "var(--accent)" }}>
                    View all
                  </Link>
                }
              />
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                      <th className="text-left py-2 px-3 text-[11px] font-semibold uppercase tracking-wider"
                        style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
                      >
                        Task
                      </th>
                      <th className="text-left py-2 px-3 text-[11px] font-semibold uppercase tracking-wider"
                        style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
                      >
                        Agent
                      </th>
                      <th className="text-left py-2 px-3 text-[11px] font-semibold uppercase tracking-wider"
                        style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
                      >
                        Type
                      </th>
                      <th className="text-left py-2 px-3 text-[11px] font-semibold uppercase tracking-wider"
                        style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
                      >
                        Status
                      </th>
                      <th className="text-right py-2 px-3 text-[11px] font-semibold uppercase tracking-wider"
                        style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
                      >
                        Time
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.slice(0, 5).map((task) => (
                      <tr key={task.id} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                        <td className="py-2.5 px-3">
                          <span className="font-medium" style={{ color: "var(--text-primary)" }}>
                            {task.title}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <RoleBadge role={task.agent_role} />
                        </td>
                        <td className="py-2.5 px-3">
                          <span className="text-xs font-mono" style={{ color: "var(--text-muted)" }}>
                            {task.task_type}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <StatusBadge status={task.status} />
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          <TimeAgo date={task.created_at} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
