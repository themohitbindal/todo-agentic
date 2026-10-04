// Every call to the FastAPI backend lives here, so components never build URLs themselves.

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    // FastAPI errors look like {"detail": "..."} or {"detail": [ {msg, loc, ...} ]}
    const body = await res.json().catch(() => ({}));
    const detail = Array.isArray(body.detail)
      ? body.detail.map((d) => d.msg).join(", ")
      : body.detail;
    throw new Error(detail || `HTTP ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

export const listTodos = () => request("/todos");

export const createTodo = (data) =>
  request("/todos", { method: "POST", body: JSON.stringify(data) });

export const updateTodo = (id, data) =>
  request(`/todos/${id}`, { method: "PATCH", body: JSON.stringify(data) });

export const deleteTodo = (id) => request(`/todos/${id}`, { method: "DELETE" });
