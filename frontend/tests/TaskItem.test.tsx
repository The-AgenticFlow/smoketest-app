import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TaskItem from "../src/components/TaskItem";
import { Task } from "../src/store";

describe("TaskItem", () => {
  const mockTask: Task = {
    id: 1,
    title: "Test Task",
    description: null,
    completed: false,
    priority: "medium",
  };

  it("renders the task title", () => {
    const onToggle = vi.fn();
    const onDelete = vi.fn();

    render(<TaskItem task={mockTask} onToggle={onToggle} onDelete={onDelete} />);
    expect(screen.getByText("Test Task")).toBeInTheDocument();
  });

  it("calls onToggle when task title is clicked", () => {
    const onToggle = vi.fn();
    const onDelete = vi.fn();

    render(<TaskItem task={mockTask} onToggle={onToggle} onDelete={onDelete} />);
    fireEvent.click(screen.getByText("Test Task"));
    expect(onToggle).toHaveBeenCalledWith(1);
  });

  it("calls onDelete when delete button is clicked", () => {
    const onToggle = vi.fn();
    const onDelete = vi.fn();

    render(<TaskItem task={mockTask} onToggle={onToggle} onDelete={onDelete} />);
    fireEvent.click(screen.getByText("x"));
    expect(onDelete).toHaveBeenCalledWith(1);
  });

  it("has completed CSS class when task is completed", () => {
    const onToggle = vi.fn();
    const onDelete = vi.fn();
    const completedTask: Task = { ...mockTask, completed: true };

    const { container } = render(
      <TaskItem task={completedTask} onToggle={onToggle} onDelete={onDelete} />
    );
    expect(container.querySelector("li")?.classList.contains("completed")).toBe(true);
  });

  it("does not have completed CSS class when task is not completed", () => {
    const onToggle = vi.fn();
    const onDelete = vi.fn();

    const { container } = render(
      <TaskItem task={mockTask} onToggle={onToggle} onDelete={onDelete} />
    );
    expect(container.querySelector("li")?.classList.contains("completed")).toBe(false);
  });
});
