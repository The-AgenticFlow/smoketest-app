import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TaskList from "../TaskList";
import { Task } from "../../store";

describe("TaskList", () => {
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

  it("renders empty state when no tasks", () => {
    render(
      <TaskList
        tasks={[]}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
      />
    );
    expect(screen.getByText("No tasks yet")).toBeInTheDocument();
  });

  it("renders correct number of tasks", () => {
    render(
      <TaskList
        tasks={mockTasks}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
      />
    );
    expect(screen.getByText("Task 1")).toBeInTheDocument();
    expect(screen.getByText("Task 2")).toBeInTheDocument();
  });

  it("calls onToggle when task is clicked", () => {
    const onToggle = vi.fn();
    render(
      <TaskList
        tasks={mockTasks}
        onToggle={onToggle}
        onDelete={vi.fn()}
      />
    );
    fireEvent.click(screen.getByText("Task 1"));
    expect(onToggle).toHaveBeenCalledWith(1);
  });

  it("calls onDelete when delete button is clicked", () => {
    const onDelete = vi.fn();
    render(
      <TaskList
        tasks={mockTasks}
        onToggle={vi.fn()}
        onDelete={onDelete}
      />
    );
    const deleteButtons = screen.getAllByText("x");
    fireEvent.click(deleteButtons[0]);
    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it("renders task-list container", () => {
    const { container } = render(
      <TaskList
        tasks={mockTasks}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
      />
    );
    expect(container.querySelector(".task-list")).toBeInTheDocument();
  });
});
