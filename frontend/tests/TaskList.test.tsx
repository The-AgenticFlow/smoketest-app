import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TaskList from "../src/components/TaskList";
import { Task } from "../src/store";

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
];

describe("TaskList", () => {
  it("renders empty state when no tasks", () => {
    render(
      <TaskList tasks={[]} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    expect(screen.getByText("No tasks yet")).toBeInTheDocument();
  });

  it("renders list of tasks", () => {
    render(
      <TaskList tasks={mockTasks} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    expect(screen.getByText("Task 1")).toBeInTheDocument();
    expect(screen.getByText("Task 2")).toBeInTheDocument();
  });

  it("renders correct number of TaskItem children", () => {
    const threeTasks: Task[] = [
      { id: 1, title: "Task 1", description: null, completed: false, priority: "medium" },
      { id: 2, title: "Task 2", description: null, completed: false, priority: "medium" },
      { id: 3, title: "Task 3", description: null, completed: false, priority: "medium" },
    ];

    const { container } = render(
      <TaskList tasks={threeTasks} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    const listItems = container.querySelectorAll("li");
    expect(listItems.length).toBe(3);
  });

  it("propagates onToggle callback from task item", () => {
    const onToggle = vi.fn();
    render(
      <TaskList tasks={mockTasks} onToggle={onToggle} onDelete={vi.fn()} />
    );
    fireEvent.click(screen.getByText("Task 1"));
    expect(onToggle).toHaveBeenCalledWith(1);
  });

  it("propagates onDelete callback from task item", () => {
    const onDelete = vi.fn();
    render(
      <TaskList tasks={mockTasks} onToggle={vi.fn()} onDelete={onDelete} />
    );
    const deleteButtons = screen.getAllByText("x");
    fireEvent.click(deleteButtons[0]);
    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it("has correct CSS class for styling", () => {
    render(
      <TaskList tasks={mockTasks} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    expect(screen.getByRole("list")).toHaveClass("task-list");
  });

  it("renders ul with task-list class", () => {
    const { container } = render(
      <TaskList tasks={[]} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    const list = container.querySelector("ul.task-list");
    expect(list).toBeInTheDocument();
  });
});
