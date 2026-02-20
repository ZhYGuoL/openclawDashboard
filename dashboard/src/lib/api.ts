const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const PROJECT_ID = process.env.NEXT_PUBLIC_PROJECT_ID || "9b7d36e6-b590-49f6-8439-2d702ac5a9f6";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

export const api = {
  getProject: (id: string) => request<import("./types").Project>(`/projects/${id}`),
  getAgents: (projectId: string) => request<import("./types").Agent[]>(`/projects/${projectId}/agents`),
  getMemos: (projectId: string) => request<import("./types").Memo[]>(`/projects/${projectId}/memos`),
  getMemo: (id: string) => request<import("./types").Memo>(`/memos/${id}`),
  getEvents: (projectId: string, limit = 50) => request<import("./types").Event[]>(`/projects/${projectId}/events?limit=${limit}`),
  getTasks: (projectId: string) => request<import("./types").Task[]>(`/projects/${projectId}/tasks`),
  getMessages: (threadId: string) => request<import("./types").Message[]>(`/threads/${threadId}/messages`),
  getArtifacts: (projectId: string) => request<import("./types").Artifact[]>(`/projects/${projectId}/artifacts`),
  startSession: (projectId: string, body: import("./types").SessionCreate) =>
    request<import("./types").SessionRead>(`/projects/${projectId}/sessions`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  updateProject: (id: string, body: Partial<Pick<import("./types").Project, "name" | "notify_phone">>) =>
    request<import("./types").Project>(`/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  executeTask: (taskId: string) =>
    request<{ task_id: string; celery_task_id: string; status: string }>(`/tasks/${taskId}/execute`, {
      method: "POST",
    }),
  health: () => request<{ status: string }>("/health"),
};

export function fetcher<T>(path: string): Promise<T> {
  return request<T>(path);
}
