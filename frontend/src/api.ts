const BASE_URL = "http://localhost:8000/api/v1";

export interface TaskPayload {
  title: string;
  description?: string;
  priority?: string;
}

export interface TaskUpdatePayload {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: string;
}

export interface TaskResponse {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  priority: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!resp.ok) {
    throw new Error(`API error: ${resp.status}`);
  }
  if (resp.status === 204) return undefined as T;
  return resp.json();
}

export async function fetchTasks(): Promise<TaskResponse[]> {
  return request<TaskResponse[]>("/tasks");
}

export async function createTask(payload: TaskPayload): Promise<TaskResponse> {
  return request<TaskResponse>("/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateTask(
  id: number,
  payload: TaskUpdatePayload,
): Promise<TaskResponse> {
  return request<TaskResponse>(`/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function deleteTask(id: number): Promise<void> {
  return request<void>(`/tasks/${id}`, { method: "DELETE" });
}
