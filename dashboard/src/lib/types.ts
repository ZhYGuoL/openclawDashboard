export interface Project {
  id: string;
  name: string;
  notify_phone: string | null;
  created_at: string;
}

export interface Agent {
  id: string;
  project_id: string;
  role: AgentRole;
  name: string;
  status: "idle" | "running" | "error";
  config_json: Record<string, unknown>;
  created_at: string;
}

export type AgentRole = "ceo" | "pm" | "engineer" | "designer" | "analyst" | "memo_writer";

export interface Thread {
  id: string;
  project_id: string;
  title: string;
  created_at: string;
}

export interface Message {
  id: string;
  thread_id: string;
  author_type: "user" | "agent" | "system";
  author_agent_id: string | null;
  content: string;
  created_at: string;
}

export interface Memo {
  id: string;
  project_id: string;
  title: string;
  content_markdown: string;
  created_at: string;
}

export interface Event {
  id: string;
  project_id: string;
  type: string;
  payload_json: Record<string, unknown>;
  created_at: string;
}

export interface Task {
  id: string;
  project_id: string;
  agent_role: AgentRole;
  title: string;
  description: string;
  task_type: "code" | "design" | "research" | "review" | "analysis" | "document";
  status: "pending" | "running" | "completed" | "failed";
  source: "meeting" | "direct";
  action_item_id: string | null;
  result_summary: string | null;
  workspace_dir: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface Artifact {
  id: string;
  project_id: string;
  task_id: string;
  artifact_type: "file" | "commit" | "url" | "document" | "image";
  path_or_url: string;
  description: string;
  metadata_json: Record<string, unknown>;
  created_at: string;
}

export interface SessionCreate {
  prompt: string;
  thread_title: string;
  auto_execute?: boolean;
}

export interface SessionRead {
  task_id: string;
  project_id: string;
  thread_id: string;
  status: string;
}
