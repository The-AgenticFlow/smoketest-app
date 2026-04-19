import { create } from "zustand";
import { fetchTasks as apiFetch, createTask, updateTask, deleteTask } from "./api";

export interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  priority: string;
}

interface TaskState {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  fetchTasks: () => Promise<void>;
  addTask: (title: string) => Promise<void>;
  toggleTask: (id: number) => Promise<void>;
  deleteTask: (id: number) => Promise<void>;
}

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  loading: false,
  error: null,

  fetchTasks: async () => {
    set({ loading: true, error: null });
    try {
      const tasks = await apiFetch();
      set({ tasks, loading: false });
    } catch (err) {
      set({ error: String(err), loading: false });
    }
  },

  addTask: async (title) => {
    try {
      const task = await createTask({ title });
      set((s) => ({ tasks: [...s.tasks, task] }));
    } catch (err) {
      set({ error: String(err) });
    }
  },

  toggleTask: async (id) => {
    try {
      const task = get().tasks.find((t) => t.id === id);
      if (!task) return;
      const updated = await updateTask(id, { completed: !task.completed });
      set((s) => ({ tasks: s.tasks.map((t) => (t.id === id ? updated : t)) }));
    } catch (err) {
      set({ error: String(err) });
    }
  },

  deleteTask: async (id) => {
    try {
      await deleteTask(id);
      set((s) => ({ tasks: s.tasks.filter((t) => t.id !== id) }));
    } catch (err) {
      set({ error: String(err) });
    }
  },
}));
