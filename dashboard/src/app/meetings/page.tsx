"use client";

import { useState } from "react";
import { useAgents } from "@/lib/hooks";
import { api, PROJECT_ID } from "@/lib/api";
import Card, { CardHeader } from "@/components/Card";
import StatusBadge from "@/components/StatusBadge";
import RoleBadge from "@/components/RoleBadge";
import { MessagesSquare, Send, Loader2, Zap, CheckCircle2, AlertCircle } from "lucide-react";

type SessionState = "idle" | "submitting" | "success" | "error";

export default function MeetingsPage() {
  const { data: agents } = useAgents();
  const [prompt, setPrompt] = useState("");
  const [title, setTitle] = useState("");
  const [autoExecute, setAutoExecute] = useState(false);
  const [state, setState] = useState<SessionState>("idle");
  const [result, setResult] = useState<{ threadId: string; taskId: string } | null>(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setState("submitting");
    setError("");

    try {
      const res = await api.startSession(PROJECT_ID, {
        prompt: prompt.trim(),
        thread_title: title.trim() || "Work Session",
        auto_execute: autoExecute,
      });
      setResult({ threadId: res.thread_id, taskId: res.task_id });
      setState("success");
      setPrompt("");
      setTitle("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start session");
      setState("error");
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8 animate-fade-in">
        <h1 className="text-xl font-bold" style={{ color: "var(--text-primary)" }}>
          Meetings
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>
          Start a new meeting session with your AI product team
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2">
          <Card>
            <CardHeader title="New Meeting Session" />
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div>
                <label className="block text-[11px] font-semibold uppercase tracking-wider mb-1.5"
                  style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
                >
                  Meeting Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Sprint Planning — Notifications"
                  className="w-full rounded-lg px-3.5 py-2.5 text-sm outline-none transition-colors placeholder:opacity-40"
                  style={{
                    background: "var(--bg-surface-raised)",
                    border: "1px solid var(--border)",
                    color: "var(--text-primary)",
                  }}
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold uppercase tracking-wider mb-1.5"
                  style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}
                >
                  Prompt / Topic
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe what the team should discuss or work on..."
                  rows={5}
                  className="w-full rounded-lg px-3.5 py-2.5 text-sm outline-none transition-colors resize-none placeholder:opacity-40"
                  style={{
                    background: "var(--bg-surface-raised)",
                    border: "1px solid var(--border)",
                    color: "var(--text-primary)",
                  }}
                />
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setAutoExecute(!autoExecute)}
                  className="relative h-5 w-9 rounded-full transition-colors cursor-pointer"
                  style={{
                    background: autoExecute ? "var(--accent)" : "var(--border)",
                  }}
                >
                  <span
                    className="absolute top-0.5 h-4 w-4 rounded-full transition-transform"
                    style={{
                      background: "var(--text-primary)",
                      left: autoExecute ? "18px" : "2px",
                    }}
                  />
                </button>
                <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
                  Auto-execute action items after meeting
                </span>
              </div>

              <button
                type="submit"
                disabled={!prompt.trim() || state === "submitting"}
                className="flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-semibold transition-opacity cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                style={{
                  background: "var(--accent)",
                  color: "var(--bg-root)",
                }}
              >
                {state === "submitting" ? (
                  <>
                    <Loader2 size={14} className="animate-spin" />
                    Starting session...
                  </>
                ) : (
                  <>
                    <Send size={14} />
                    Start Meeting
                  </>
                )}
              </button>
            </form>

            {state === "success" && result && (
              <div className="mt-4 rounded-lg p-3 flex items-start gap-2"
                style={{ background: "rgba(62,207,142,0.08)", border: "1px solid rgba(62,207,142,0.2)" }}
              >
                <CheckCircle2 size={16} style={{ color: "var(--success)" }} className="shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium" style={{ color: "var(--success)" }}>
                    Meeting session started
                  </p>
                  <p className="text-xs mt-0.5 font-mono" style={{ color: "var(--text-muted)" }}>
                    Thread: {result.threadId.slice(0, 8)}... &middot; Task: {result.taskId.slice(0, 8)}...
                  </p>
                </div>
              </div>
            )}

            {state === "error" && (
              <div className="mt-4 rounded-lg p-3 flex items-start gap-2"
                style={{ background: "rgba(239,95,95,0.08)", border: "1px solid rgba(239,95,95,0.2)" }}
              >
                <AlertCircle size={16} style={{ color: "var(--error)" }} className="shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium" style={{ color: "var(--error)" }}>
                    Failed to start session
                  </p>
                  <p className="text-xs mt-0.5 font-mono" style={{ color: "var(--text-muted)" }}>
                    {error}
                  </p>
                </div>
              </div>
            )}
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader title="Team Roster" />
            <div className="flex flex-col gap-2">
              {agents?.map((agent) => (
                <div
                  key={agent.id}
                  className="flex items-center gap-3 rounded-lg p-2.5"
                  style={{ background: "var(--bg-surface-raised)" }}
                >
                  <div
                    className="flex h-7 w-7 items-center justify-center rounded-full text-[10px] font-bold"
                    style={{
                      background: `var(--role-${agent.role})`,
                      color: "var(--bg-root)",
                    }}
                  >
                    {agent.name.charAt(0)}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-xs font-medium truncate" style={{ color: "var(--text-primary)" }}>
                      {agent.name}
                    </div>
                    <RoleBadge role={agent.role} />
                  </div>
                  <StatusBadge status={agent.status} />
                </div>
              ))}
              {(!agents || agents.length === 0) && (
                <p className="text-xs text-center py-4" style={{ color: "var(--text-muted)" }}>
                  No agents configured
                </p>
              )}
            </div>
          </Card>

          <Card className="mt-4">
            <div className="flex items-start gap-2.5">
              <Zap size={14} style={{ color: "var(--accent)" }} className="shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-medium mb-1" style={{ color: "var(--text-primary)" }}>
                  How meetings work
                </p>
                <p className="text-[11px] leading-relaxed" style={{ color: "var(--text-muted)" }}>
                  Each meeting runs multiple rounds where agents discuss and collaborate on your prompt. 
                  The Memo Writer then produces a structured summary. Results appear in the Memos tab.
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
