import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "../src/App";

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
    title: "Test",
    description: null,
    completed: true,
    priority: "medium",
  }),
  deleteTask: vi.fn().mockResolvedValue(undefined),
}));

describe("App", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the heading", async () => {
    render(<App />);
    expect(await screen.findByText("SmokeTest Tasks")).toBeInTheDocument();
  });

  it("shows the add task form", async () => {
    render(<App />);
    expect(await screen.findByPlaceholderText("New task...")).toBeInTheDocument();
  });
});
