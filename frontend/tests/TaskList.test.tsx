import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TaskList from "../src/components/TaskList";
import { Task } from "../src/store";

describe("TaskList", () => {
  it("renders empty list when no tasks provided", () => {
    render(<TaskList tasks={[]} onToggle={vi.fn()} onDelete={vi.fn()} />);
    const list = document.querySelector("ul.task-list");
    expect(list).toBeInTheDocument();
    expect(list?.children.length).toBe(0);
  });

  it("renders multiple tasks", () => {
    const mockTasks: Task[] = [
      {
        id: 1,
        title: "Task 1",
        description: null,
        completed: false,
        priority: "medium",
      },
      {
        id: 2,
        title: "Task 2",
        description: null,
        completed: true,
        priority: "high",
      },
      {
        id: 3,
        title: "Task 3",
        description: null,
        completed: false,
        priority: "low",
      },
    ];

    render(<TaskList tasks={mockTasks} onToggle={vi.fn()} onDelete={vi.fn()} />);
    expect(screen.getByText("Task 1")).toBeInTheDocument();
    expect(screen.getByText("Task 2")).toBeInTheDocument();
    expect(screen.getByText("Task 3")).toBeInTheDocument();
  });

  it("renders ul with task-list class", () => {
    const { container } = render(
      <TaskList tasks={[]} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    const list = container.querySelector("ul.task-list");
    expect(list).toBeInTheDocument();
  });

  it("passes correct props to TaskItem children", () => {
    const mockTask: Task = {
      id: 1,
      title: "Test Task",
      description: null,
      completed: false,
      priority: "medium",
    };
    const onToggle = vi.fn();
    const onDelete = vi.fn();

    render(<TaskList tasks={[mockTask]} onToggle={onToggle} onDelete={onDelete} />);

    // Task should render with the correct title
    expect(screen.getByText("Test Task")).toBeInTheDocument();

    // Click on the task to verify onToggle is passed
    screen.getByText("Test Task").click();
    expect(onToggle).toHaveBeenCalledWith(1);

    // Click on delete button to verify onDelete is passed
    screen.getByText("x").click();
    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it("renders correct number of TaskItem children", () => {
    const mockTasks: Task[] = [
      { id: 1, title: "Task 1", description: null, completed: false, priority: "medium" },
      { id: 2, title: "Task 2", description: null, completed: false, priority: "medium" },
      { id: 3, title: "Task 3", description: null, completed: false, priority: "medium" },
    ];

    const { container } = render(
      <TaskList tasks={mockTasks} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    const listItems = container.querySelectorAll("li");
    expect(listItems.length).toBe(3);
  });
});
