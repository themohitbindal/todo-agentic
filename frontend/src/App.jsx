import { useEffect, useState } from "react";
import { createTodo, deleteTodo, listTodos, updateTodo } from "./api.js";

export default function App() {
  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // READ: load all todos once on page load -> GET /todos
  useEffect(() => {
    listTodos()
      .then(setTodos)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  // Small wrapper so every action shows backend errors the same way.
  async function run(action) {
    setError("");
    try {
      await action();
    } catch (e) {
      setError(e.message);
    }
  }

  // CREATE -> POST /todos
  const handleAdd = (e) => {
    e.preventDefault();
    run(async () => {
      const todo = await createTodo({ title, description: description || null });
      setTodos((prev) => [...prev, todo]);
      setTitle("");
      setDescription("");
    });
  };

  // UPDATE -> PATCH /todos/{id}
  const handleUpdate = (id, changes) =>
    run(async () => {
      const updated = await updateTodo(id, changes);
      setTodos((prev) => prev.map((t) => (t.id === id ? updated : t)));
    });

  // DELETE -> DELETE /todos/{id}
  const handleDelete = (id) =>
    run(async () => {
      await deleteTodo(id);
      setTodos((prev) => prev.filter((t) => t.id !== id));
    });

  const doneCount = todos.filter((t) => t.completed).length;

  return (
    <main className="app">
      <header>
        <h1>Todos</h1>
        <p className="muted">
          React + Vite → FastAPI → Postgres · {doneCount}/{todos.length} done
        </p>
      </header>

      <form className="add-form" onSubmit={handleAdd}>
        <input
          placeholder="What needs doing?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <input
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button type="submit">Add</button>
      </form>

      {error && <p className="error">⚠ {error}</p>}

      {loading ? (
        <p className="muted">Loading…</p>
      ) : todos.length === 0 ? (
        <p className="muted">No todos yet. Add one above.</p>
      ) : (
        <ul className="list">
          {todos.map((todo) => (
            <TodoItem
              key={todo.id}
              todo={todo}
              onUpdate={handleUpdate}
              onDelete={handleDelete}
            />
          ))}
        </ul>
      )}
    </main>
  );
}

function TodoItem({ todo, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(todo.title);

  const save = () => {
    setEditing(false);
    if (draft.trim() && draft !== todo.title) onUpdate(todo.id, { title: draft.trim() });
    else setDraft(todo.title);
  };

  return (
    <li className={todo.completed ? "item done" : "item"}>
      <input
        type="checkbox"
        checked={todo.completed}
        onChange={() => onUpdate(todo.id, { completed: !todo.completed })}
      />
      <div className="body">
        {editing ? (
          <input
            autoFocus
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onBlur={save}
            onKeyDown={(e) => e.key === "Enter" && save()}
          />
        ) : (
          <span className="title" onDoubleClick={() => setEditing(true)} title="Double-click to edit">
            {todo.title}
          </span>
        )}
        {todo.description && <small className="muted">{todo.description}</small>}
      </div>
      <button className="danger" onClick={() => onDelete(todo.id)}>
        Delete
      </button>
    </li>
  );
}
