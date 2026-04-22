import { create } from "zustand";
import {
  fetchTasks as apiFetch,
  createTask,
  updateTask,
  deleteTask,
  TaskFilterParams
} from "./api";

export interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  priority: string;
}

interface TaskState {
  tasks: Task[];
  total: number;  // Track total count for pagination UI
  loading: boolean;
  error: string | null;
  fetchTasks: (filters?: TaskFilterParams) => Promise<void>;
  addTask: (title: string) => Promise<void>;
  toggleTask: (id: number) => Promise<void>;
  deleteTask: (id: number) => Promise<void>;
}

export const useTaskStore = create<TaskState>((set, get) => ({
  tasks: [],
  total: 0,
  loading: false,
  error: null,

  fetchTasks: async (filters?: TaskFilterParams) => {
    set({ loading: true, error: null });
    try {
      const response = await apiFetch(filters);
      set({
        tasks: response.items,  // Extract items from paginated response
        total: response.total,  // Store total count
        loading: false
      });
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
