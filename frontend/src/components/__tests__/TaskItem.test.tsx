import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TaskItem from "../TaskItem";
import { Task } from "../../store";

describe("TaskItem", () => {
  const mockTask: Task = {
    id: 1,
    title: "Test Task",
    description: null,
    completed: false,
    priority: "medium",
  };

  it("renders task title", () => {
    render(
      <TaskItem
        task={mockTask}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
      />
    );
    expect(screen.getByText("Test Task")).toBeInTheDocument();
  });

  it("applies completed class when task.completed is true", () => {
    const completedTask = { ...mockTask, completed: true };
    const { container } = render(
      <TaskItem
        task={completedTask}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
      />
    );
    expect(container.querySelector("li")).toHaveClass("completed");
  });

  it("does not apply completed class when task.completed is false", () => {
    const { container } = render(
      <TaskItem
        task={mockTask}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
      />
    );
    expect(container.querySelector("li")).not.toHaveClass("completed");
  });

  it("calls onToggle with task.id when title span clicked", () => {
    const onToggle = vi.fn();
    render(
      <TaskItem
        task={mockTask}
        onToggle={onToggle}
        onDelete={vi.fn()}
      />
    );
    fireEvent.click(screen.getByText("Test Task"));
    expect(onToggle).toHaveBeenCalledWith(1);
  });

  it("calls onDelete with task.id when delete button clicked", () => {
    const onDelete = vi.fn();
    render(
      <TaskItem
        task={mockTask}
        onToggle={vi.fn()}
        onDelete={onDelete}
      />
    );
    fireEvent.click(screen.getByText("x"));
    expect(onDelete).toHaveBeenCalledWith(1);
  });
});
