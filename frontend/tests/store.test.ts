import { describe, it, expect, vi, beforeEach } from "vitest";
import { useTaskStore, Task } from "../src/store";
import * as api from "../src/api";

// Mock the API module
vi.mock("../src/api", () => ({
  fetchTasks: vi.fn(),
  createTask: vi.fn(),
  updateTask: vi.fn(),
  deleteTask: vi.fn(),
}));

describe("useTaskStore", () => {
  beforeEach(() => {
    // Reset store to initial state before each test
    useTaskStore.setState({
      tasks: [],
      loading: false,
      error: null,
    });
    // Clear all mocks
    vi.clearAllMocks();
  });

  describe("toggleTask", () => {
    it("should toggle task completed status from false to true", async () => {
      // Create a test task matching the Task interface
      const testTask: Task = {
        id: 1,
        title: "Test Task",
        description: "Test Description",
        completed: false,
        priority: "medium",
      };

      // Setup mocked API responses
      const mockUpdateTask = vi.mocked(api.updateTask);

      // Mock the update to return task with completed: true
      mockUpdateTask.mockResolvedValueOnce({
        ...testTask,
        completed: true,
      });

      // Set initial task in store
      useTaskStore.setState({
        tasks: [testTask],
      });

      // Verify initial state
      const initialState = useTaskStore.getState();
      expect(initialState.tasks).toHaveLength(1);
      expect(initialState.tasks[0].completed).toBe(false);

      // Call toggleTask
      await useTaskStore.getState().toggleTask(1);

      // Verify updateTask API was called with correct params
      expect(mockUpdateTask).toHaveBeenCalledWith(1, { completed: true });

      // Verify state was updated
      const newState = useTaskStore.getState();
      expect(newState.tasks).toHaveLength(1);
      expect(newState.tasks[0].completed).toBe(true);
    });

    it("should toggle task completed status from true to false", async () => {
      const testTask: Task = {
        id: 2,
        title: "Completed Task",
        description: "Already done",
        completed: true,
        priority: "high",
      };

      const mockUpdateTask = vi.mocked(api.updateTask);
      mockUpdateTask.mockResolvedValueOnce({
        ...testTask,
        completed: false,
      });

      useTaskStore.setState({
        tasks: [testTask],
      });

      const initialState = useTaskStore.getState();
      expect(initialState.tasks[0].completed).toBe(true);

      await useTaskStore.getState().toggleTask(2);

      expect(mockUpdateTask).toHaveBeenCalledWith(2, { completed: false });

      const newState = useTaskStore.getState();
      expect(newState.tasks[0].completed).toBe(false);
    });

    it("should not call API if task not found", async () => {
      const mockUpdateTask = vi.mocked(api.updateTask);

      useTaskStore.setState({
        tasks: [],
      });

      await useTaskStore.getState().toggleTask(999);

      expect(mockUpdateTask).not.toHaveBeenCalled();
    });

    it("should handle API errors gracefully", async () => {
      const testTask: Task = {
        id: 3,
        title: "Error Task",
        description: null,
        completed: false,
        priority: "low",
      };

      const mockUpdateTask = vi.mocked(api.updateTask);
      mockUpdateTask.mockRejectedValueOnce(new Error("API Error"));

      useTaskStore.setState({
        tasks: [testTask],
      });

      await useTaskStore.getState().toggleTask(3);

      const state = useTaskStore.getState();
      expect(state.error).toBe("Error: API Error");
      // Task should remain unchanged
      expect(state.tasks[0].completed).toBe(false);
    });
  });
});
