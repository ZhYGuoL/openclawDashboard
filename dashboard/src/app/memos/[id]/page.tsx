"use client";

import { useMemo } from "@/lib/hooks";
import Card from "@/components/Card";
import { ArrowLeft, Loader2, Calendar, Copy, Check } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useState } from "react";
import { use } from "react";

export default function MemoDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: memo, isLoading } = useMemo(id);
  const [copied, setCopied] = useState(false);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Loader2 className="animate-spin" size={24} style={{ color: "var(--text-muted)" }} />
      </div>
    );
  }

  if (!memo) {
    return (
      <div className="max-w-4xl mx-auto">
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>Memo not found.</p>
      </div>
    );
  }

  const handleCopy = async () => {
    await navigator.clipboard.writeText(memo.content_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <Link href="/memos" className="inline-flex items-center gap-1.5 text-sm mb-6 transition-colors"
        style={{ color: "var(--text-muted)" }}
      >
        <ArrowLeft size={14} />
        Back to memos
      </Link>

      <div className="mb-6">
        <h1 className="text-xl font-bold mb-2" style={{ color: "var(--text-primary)" }}>
          {memo.title}
        </h1>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5 text-xs" style={{ color: "var(--text-muted)" }}>
            <Calendar size={12} />
            {new Date(memo.created_at).toLocaleDateString("en-US", {
              weekday: "long",
              month: "long",
              day: "numeric",
              year: "numeric",
            })}
          </span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 text-xs transition-colors cursor-pointer"
            style={{ color: copied ? "var(--success)" : "var(--text-muted)" }}
          >
            {copied ? <Check size={12} /> : <Copy size={12} />}
            {copied ? "Copied!" : "Copy markdown"}
          </button>
        </div>
      </div>

      <Card>
        <div className="markdown-body">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {memo.content_markdown}
          </ReactMarkdown>
        </div>
      </Card>
    </div>
  );
}
