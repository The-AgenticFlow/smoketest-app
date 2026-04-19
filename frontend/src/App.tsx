import { useEffect } from "react";
import { useTaskStore } from "./store";

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
      <ul className="task-list">
        {tasks.map((task) => (
          <li key={task.id} className={task.completed ? "completed" : ""}>
            <span onClick={() => toggleTask(task.id)}>{task.title}</span>
            <button onClick={() => deleteTask(task.id)}>x</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
