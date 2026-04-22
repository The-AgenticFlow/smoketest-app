import { describe, it, expect, vi, beforeEach, MockedFunction } from "vitest";
import { useTaskStore, Task } from "../src/store";
import { updateTask } from "../src/api";

vi.mock("../src/api", () => ({
  fetchTasks: vi.fn().mockResolvedValue([]),
  createTask: vi.fn().mockResolvedValue({
    id: 1,
    title: "Test",
    description: null,
    completed: false,
    priority: "medium",
  }),
  updateTask: vi.fn().mockResolvedValue({
    id: 1,
    title: "Test Task",
    description: null,
    completed: true,
    priority: "medium",
  }),
  deleteTask: vi.fn().mockResolvedValue(undefined),
}));

const mockedUpdateTask = updateTask as MockedFunction<typeof updateTask>;

describe("toggleTask", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset store to initial state
    useTaskStore.setState({
      tasks: [],
      loading: false,
      error: null,
    });
  });

  it("flips completed status from false to true", async () => {
    const store = useTaskStore;

    // Set up a task with completed: false
    const initialTask: Task = {
      id: 1,
      title: "Test Task",
      description: null,
      completed: false,
      priority: "medium",
    };

    store.setState({ tasks: [initialTask] });

    // Call toggleTask
    await store.getState().toggleTask(1);

    // Verify updateTask was called with the correct parameters
    expect(mockedUpdateTask).toHaveBeenCalledWith(1, { completed: true });

    // Verify the task's completed status is now true
    const tasks = store.getState().tasks;
    expect(tasks[0].completed).toBe(true);
  });

  it("flips completed status from true to false", async () => {
    const store = useTaskStore;

    // Mock the response for toggling back to false
    mockedUpdateTask.mockResolvedValueOnce({
      id: 2,
      title: "Test Task 2",
      description: null,
      completed: false,
      priority: "high",
    });

    // Set up a task with completed: true
    const initialTask: Task = {
      id: 2,
      title: "Test Task 2",
      description: null,
      completed: true,
      priority: "high",
    };

    store.setState({ tasks: [initialTask] });

    // Call toggleTask
    await store.getState().toggleTask(2);

    // Verify updateTask was called with the correct parameters
    expect(mockedUpdateTask).toHaveBeenCalledWith(2, { completed: false });

    // Verify the task's completed status is now false
    const tasks = store.getState().tasks;
    expect(tasks[0].completed).toBe(false);
  });

  it("handles task not found", async () => {
    const store = useTaskStore;

    store.setState({ tasks: [] });

    // Call toggleTask with non-existent ID
    await store.getState().toggleTask(999);

    // Verify updateTask was not called
    expect(mockedUpdateTask).not.toHaveBeenCalled();
  });

  it("handles API error", async () => {
    const store = useTaskStore;

    // Mock updateTask to throw an error
    mockedUpdateTask.mockRejectedValueOnce(new Error("API error"));

    const initialTask: Task = {
      id: 3,
      title: "Test Task",
      description: null,
      completed: false,
      priority: "medium",
    };

    store.setState({ tasks: [initialTask] });

    // Call toggleTask
    await store.getState().toggleTask(3);

    // Verify error is set in store
    expect(store.getState().error).toBe("Error: API error");
  });
});
