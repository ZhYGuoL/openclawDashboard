import useSWR from "swr";
import { fetcher, PROJECT_ID } from "./api";
import type { Agent, Event, Memo, Task, Project } from "./types";

const projectId = PROJECT_ID;

export function useProject() {
  return useSWR<Project>(`/projects/${projectId}`, fetcher);
}

export function useAgents() {
  return useSWR<Agent[]>(`/projects/${projectId}/agents`, fetcher);
}

export function useMemos() {
  return useSWR<Memo[]>(`/projects/${projectId}/memos`, fetcher);
}

export function useMemo(id: string) {
  return useSWR<Memo>(id ? `/memos/${id}` : null, fetcher);
}

export function useEvents(limit = 100) {
  return useSWR<Event[]>(`/projects/${projectId}/events?limit=${limit}`, fetcher, {
    refreshInterval: 5000,
  });
}

export function useTasks() {
  return useSWR<Task[]>(`/projects/${projectId}/tasks`, fetcher);
}
