import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TaskItem from "../src/components/TaskItem";
import { Task } from "../src/store";

const mockTask: Task = {
  id: 1,
  title: "Test Task",
  description: null,
  completed: false,
  priority: "medium",
};

describe("TaskItem", () => {
  it("renders task title", () => {
    render(
      <TaskItem task={mockTask} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    expect(screen.getByText("Test Task")).toBeInTheDocument();
  });

  it("calls onToggle when task is clicked", () => {
    const onToggle = vi.fn();
    render(
      <TaskItem task={mockTask} onToggle={onToggle} onDelete={vi.fn()} />
    );
    fireEvent.click(screen.getByText("Test Task"));
    expect(onToggle).toHaveBeenCalledWith(1);
  });

  it("calls onDelete when delete button is clicked", () => {
    const onDelete = vi.fn();
    render(
      <TaskItem task={mockTask} onToggle={vi.fn()} onDelete={onDelete} />
    );
    fireEvent.click(screen.getByText("x"));
    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it("shows completed styling when task is completed", () => {
    const completedTask = { ...mockTask, completed: true };
    render(
      <TaskItem task={completedTask} onToggle={vi.fn()} onDelete={vi.fn()} />
    );
    expect(screen.getByText("Test Task").parentElement).toHaveClass("completed");
  });
});
