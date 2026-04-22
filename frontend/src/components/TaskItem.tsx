import { Task } from "../store";

interface TaskItemProps {
  task: Task;
  onToggle: (id: number) => void;
  onDelete: (id: number) => void;
}

export default function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <li className={task.completed ? "completed" : ""}>
      <span onClick={() => onToggle(task.id)}>{task.title}</span>
      <button onClick={() => onDelete(task.id)}>x</button>
    </li>
  );
}
