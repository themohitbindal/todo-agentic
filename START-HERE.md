# Start here: beginner checklist

Read this before RUN.md. These are the things that trip up beginners on this stack, most of them seen while testing this project.

## Test results (2026-10-01, real Uvicorn + Postgres 16)

All Phase 1 behaviour works:

| Check | Result |
|-------|--------|
| `GET /health` | ✅ 200 |
| `POST /todos` | ✅ 201, Postgres generates `id` + timestamps |
| `GET /todos`, `GET /todos/{id}` | ✅ 200 |
| `PATCH` with only `completed` | ✅ other fields untouched, `updated_at` changes |
| Empty or missing title | ✅ 422 with `loc: ["body","title"]` |
| `GET /todos/abc` | ✅ 422 (id must be int) |
| Unknown id | ✅ 404 `{"detail":"Todo not found"}` |
| `DELETE` | ✅ 204, then 404 |
| CORS from `localhost:5173` | ✅ allowed; other origins blocked |
| `/docs`, `/openapi.json` | ✅ |
| Table schema in Postgres | ✅ matches the model (NOT NULL, defaults, `timestamptz`) |
| `PATCH {"title": null}` | ⚠️ **500**, a known bug (DB rejects NULL). The server recovers fine. Fixed in Phase 2. |

## 1. Opening Docker Desktop does not start the DB

Docker Desktop is just the engine. Your DB exists only after you run:

```powershell
docker compose up -d      # from the todo-fastapi folder
docker compose ps         # must show todo-postgres ... (healthy)
```

An empty `docker compose ps` means no DB.

## 2. Port 5432 is shared with your other project

The `ai-and-learning-db-1` container also uses port 5432. Only one can run at a time. If you get `port is already allocated`:

```powershell
docker stop ai-and-learning-db-1
docker compose up -d
```

## 3. Start order matters: DB → backend → frontend

The backend connects to Postgres **at startup** (to create tables). If the DB is down, Uvicorn crashes immediately with `OperationalError` / `connection refused`. The frontend then shows `Failed to fetch`.

## 4. The venv: the #1 Python beginner trap

- Create it **once**, inside `backend/`: `python -m venv .venv`
- **Activate it in every new terminal**: `.\.venv\Scripts\Activate.ps1`
- Check your prompt starts with `(.venv)`. If it doesn't, you're using global Python, and `uvicorn` will be "not recognized", or `pip install` will put packages in the wrong place.
- Never commit `.venv/` (it's in `.gitignore`). It's like `node_modules`: rebuild it from `requirements.txt`.
- First time only, PowerShell may block activation: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
- In VS Code: `Ctrl+Shift+P` → "Python: Select Interpreter" → pick `backend\.venv`.

## 5. Run Uvicorn from the `backend/` folder

`uvicorn app.main:app --reload` means "import the package `app` from the **current folder**". From anywhere else, you get `ModuleNotFoundError: No module named 'app'`.

## 6. Adding a Python package

```powershell
pip install some-package
```

Then **add it to `requirements.txt` by hand** (pip doesn't do that automatically, unlike `npm install`). `--reload` restarts on `.py` changes, but restart Uvicorn yourself after installing packages.

## 7. Changing a model doesn't change the table (yet)

`create_all()` only creates **missing** tables. It never adds or alters columns. If you add a field to `models/todo.py`, Postgres won't get it. For now, reset the DB:

```powershell
docker compose down -v    # ⚠ deletes ALL todo data
docker compose up -d
```

Phase 3 fixes this properly with Alembic migrations.

## 8. Reading errors

| You see | Means | Look at |
|---------|-------|---------|
| **422** | your **input** is wrong | the `loc` + `msg` in the response body |
| **404** | the resource doesn't exist | the id you sent |
| **500** | a **server bug** | the traceback in the **backend terminal** |
| CORS error in the browser console | often the backend crashed or isn't running (or the origin isn't allowed) | the backend terminal first |

## 9. Test in `/docs` before blaming the frontend

http://localhost:8000/docs → "Try it out". If it works there but not in React, the problem is in the frontend or CORS. If it fails there too, the problem is in the backend.

## 10. The project lives in OneDrive

`backend/.venv` and `frontend/node_modules` contain thousands of files, and OneDrive will try to sync them all to the cloud. That makes it slow, and it can lock files (`EPERM` / `Access denied` during `npm install` or `pip install`). Options: pause OneDrive while working, or move the project outside OneDrive (for example `C:\dev\todo-fastapi`).

## 11. Notion is a copy

The Notion pages under theCode → Personal → todo-fastapi mirror these Markdown files. Edit the files in the project; edits made in Notion are not copied back.
