"use client";

import { useMemos } from "@/lib/hooks";
import Card from "@/components/Card";
import TimeAgo from "@/components/TimeAgo";
import EmptyState from "@/components/EmptyState";
import { FileText, Loader2, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function MemosPage() {
  const { data: memos, isLoading } = useMemos();

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8 animate-fade-in">
        <h1 className="text-xl font-bold" style={{ color: "var(--text-primary)" }}>
          Memos
        </h1>
        <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>
          AI-generated meeting summaries and product memos
        </p>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center h-[40vh]">
          <Loader2 className="animate-spin" size={24} style={{ color: "var(--text-muted)" }} />
        </div>
      )}

      {!isLoading && (!memos || memos.length === 0) && (
        <Card>
          <EmptyState icon={<FileText size={32} />} message="No memos generated yet. Start a meeting session to create one." />
        </Card>
      )}

      <div className="flex flex-col gap-3">
        {memos?.map((memo, i) => (
          <Link key={memo.id} href={`/memos/${memo.id}`}>
            <Card className="group cursor-pointer transition-all animate-fade-in"
              style={{ animationDelay: `${i * 40}ms` } as React.CSSProperties}
            >
              <div className="flex items-center justify-between">
                <div className="min-w-0 flex-1">
                  <h2 className="text-sm font-semibold truncate mb-1" style={{ color: "var(--text-primary)" }}>
                    {memo.title}
                  </h2>
                  <p className="text-xs line-clamp-2" style={{ color: "var(--text-secondary)" }}>
                    {memo.content_markdown.slice(0, 200).replace(/[#*_\-|]/g, "").trim()}...
                  </p>
                  <div className="mt-2">
                    <TimeAgo date={memo.created_at} />
                  </div>
                </div>
                <ArrowRight size={16} style={{ color: "var(--text-muted)" }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0 ml-4" />
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
