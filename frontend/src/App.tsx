import { useEffect } from "react";
import { useTaskStore } from "./store";
import TaskList from "./components/TaskList";

export default function App() {
  const { tasks, loading, error, fetchTasks, addTask, toggleTask, deleteTask } =
    useTaskStore();

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  if (error) return <div className="error">{error}</div>;
  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="app">
      <h1>SmokeTest Tasks</h1>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const form = e.target as HTMLFormElement;
          const input = form.elements.namedItem("title") as HTMLInputElement;
          if (input.value.trim()) {
            addTask(input.value.trim());
            input.value = "";
          }
        }}
      >
        <input name="title" placeholder="New task..." />
        <button type="submit">Add</button>
      </form>
      <TaskList tasks={tasks} onToggle={toggleTask} onDelete={deleteTask} />
    </div>
  );
}
