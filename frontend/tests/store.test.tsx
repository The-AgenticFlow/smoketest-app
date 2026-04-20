import { vi, describe, it, expect, beforeEach } from "vitest";
import { useTaskStore } from "../src/store";

vi.mock("../src/api", () => ({
  fetchTasks: vi.fn().mockResolvedValue([]),
  createTask: vi.fn().mockResolvedValue({
    id: 1,
    title: "Test",
    description: null,
    completed: false,
    priority: "medium",
  }),
  updateTask: vi.fn().mockImplementation((id, updates) => {
    return Promise.resolve({
      id,
      title: "Test",
      description: null,
      completed: updates.completed ?? false,
      priority: "medium",
    });
  }),
  deleteTask: vi.fn().mockResolvedValue(undefined),
}));

describe("useTaskStore", () => {
  beforeEach(() => {
    useTaskStore.setState({
      tasks: [],
      loading: false,
      error: null,
    });
    vi.clearAllMocks();
  });

  describe("toggleTask", () => {
    it("flips the completed status of a task", async () => {
      // Set up initial state with a task
      useTaskStore.setState({
        tasks: [
          {
            id: 1,
            title: "Test Task",
            description: null,
            completed: false,
            priority: "medium",
          },
        ],
      });

      const store = useTaskStore.getState();

      // Call toggleTask
      await store.toggleTask(1);

      // Verify the task was toggled
      const updatedState = useTaskStore.getState();
      expect(updatedState.tasks[0].completed).toBe(true);
    });

    it("does nothing when task is not found", async () => {
      // Set up initial state without the task
      useTaskStore.setState({
        tasks: [],
      });

      const store = useTaskStore.getState();

      // Call toggleTask with non-existent ID
      await store.toggleTask(999);

      // Verify state remains unchanged
      const updatedState = useTaskStore.getState();
      expect(updatedState.tasks).toEqual([]);
    });
  });
});
