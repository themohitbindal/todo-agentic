# How to run everything (DB → Backend → Frontend)

You need **3 terminals**, started in this order:

| # | What | Folder | Command (every time) | URL |
|---|------|--------|----------------------|-----|
| 1 | Postgres (Docker) | project root | `docker compose up -d` | `localhost:5432` |
| 2 | FastAPI backend | `backend/` | `.\.venv\Scripts\Activate.ps1` then `uvicorn app.main:app --reload` | http://localhost:8000/docs |
| 3 | React frontend | `frontend/` | `npm run dev` | http://localhost:5173 |

The first time, there are one-time setup steps for the backend (section 2A). After that, only the "every time" commands are needed.

All commands below are for **PowerShell** (the default VS Code terminal on Windows). Git Bash versions are noted where they differ.

---

## 0. Prerequisites (check once)

```powershell
docker --version     # Docker 20+  (Docker Desktop must be RUNNING, whale icon in tray)
python --version     # Python 3.12+
node --version       # Node 20+
```

---

## 1. Database — Postgres in Docker

### Start

1. Open **Docker Desktop** and wait until it says "Engine running".
2. In a terminal at the project root (`todo-fastapi/`):

```powershell
docker compose up -d
```

- `up` = create and start the services listed in `docker-compose.yml`.
- `-d` = detached (runs in background, gives you the terminal back).

3. Check it is healthy:

```powershell
docker compose ps
```

You should see `todo-postgres` with status `Up ... (healthy)`.

> **Opening Docker Desktop is not the same as starting the DB.** Docker Desktop is only the engine. The `todo-postgres` container exists and runs only after `docker compose up -d`. If `docker compose ps` shows an empty list, the DB is not running.

> **Port 5432 is shared with your other project.** The `ai-and-learning-db-1` container (from `ai-and-learning`) also uses port 5432. Only one of them can run at a time. If `docker compose up -d` fails with `port is already allocated`, stop the other one first: `docker stop ai-and-learning-db-1`

### Connection details (already set as defaults in the backend)

| Setting | Value |
|---------|-------|
| Host | `localhost` |
| Port | `5432` |
| User | `todo_user` |
| Password | `todo_pass` |
| Database | `todo_db` |

### Look inside the DB (optional, very useful for learning)

```powershell
docker exec -it todo-postgres psql -U todo_user -d todo_db
```

Inside `psql`:

```sql
\dt                     -- list tables (you'll see "todos" after the backend has started once)
\d todos                -- show columns of the todos table
SELECT * FROM todos;    -- see your data
\q                      -- quit
```

### Stop / reset

```powershell
docker compose down      # stop; data is KEPT (stored in a Docker volume)
docker compose down -v   # stop AND DELETE all data (fresh empty DB next time)
```

---

## 2. Backend — FastAPI (Python)

### What is a "virtual environment" (venv)?

In Node, every project has its own `node_modules/`. Python by default installs packages **globally** for the whole computer. A **venv** is Python's version of `node_modules/`: a folder (`backend/.venv/`) holding a private Python + private packages for this project only.

| Node | Python |
|------|--------|
| `package.json` | `requirements.txt` |
| `node_modules/` | `.venv/` |
| `npm install` | `pip install -r requirements.txt` |
| `nodemon index.js` | `uvicorn app.main:app --reload` |

"Activating" the venv just changes your current terminal so that `python`, `pip` and `uvicorn` point to the ones inside `.venv/`. You must activate it **in every new terminal** before running the backend.

### 2A. One-time setup

```powershell
cd backend

# 1. Create the virtual environment (makes the backend/.venv folder)
python -m venv .venv

# 2. Activate it
.\.venv\Scripts\Activate.ps1
```

Your prompt should now start with `(.venv)`. That means it worked.

> **If you get** `running scripts is disabled on this system`: PowerShell blocks scripts by default. Run this once, then try activating again:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

```powershell
# 3. Upgrade pip (Python's npm) and install the project's packages
python -m pip install --upgrade pip
pip install -r requirements.txt
```

```powershell
# 4. Check it worked
pip list          # should show fastapi, SQLAlchemy, psycopg, uvicorn, ...
```

**Optional — `.env` file.** The backend already defaults to the Docker DB above, so you can skip this. If you ever want to change settings, create `backend/.env` with:

```
DATABASE_URL=postgresql+psycopg://todo_user:todo_pass@localhost:5432/todo_db
CORS_ORIGINS=http://localhost:5173
```

**VS Code tip:** press `Ctrl+Shift+P` → "Python: Select Interpreter" → choose the one in `backend\.venv`. Then imports stop showing red squiggles, and new VS Code terminals auto-activate the venv.

### 2B. Every time you want to run the backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1          # Git Bash: source .venv/Scripts/activate
uvicorn app.main:app --reload
```

- `app.main:app` = "in the file `app/main.py`, use the variable named `app`".
- `--reload` = restart automatically when you save a `.py` file (like nodemon).
- Must be run **from the `backend/` folder**, otherwise Python can't find the `app` package.

You'll see `Uvicorn running on http://127.0.0.1:8000`. Open:

| URL | What |
|-----|------|
| http://localhost:8000/docs | **Swagger UI** — interactive docs, try every endpoint from the browser |
| http://localhost:8000/redoc | Same docs, different style |
| http://localhost:8000/openapi.json | The raw OpenAPI spec FastAPI generates from your code |
| http://localhost:8000/health | Health check → `{"status":"ok"}` |
| http://localhost:8000/todos | List of todos (JSON) |

Alternative command (same thing, FastAPI's own CLI): `fastapi dev app/main.py`

Stop the server: `Ctrl+C`. Leave the venv: `deactivate`.

### Quick API test from the terminal (optional)

```powershell
# create
Invoke-RestMethod -Method Post -Uri http://localhost:8000/todos -ContentType "application/json" -Body '{"title":"Learn FastAPI"}'
# list
Invoke-RestMethod http://localhost:8000/todos
```

(Or just use the "Try it out" buttons on `/docs`.)

---

## 3. Frontend — React + Vite

```powershell
cd frontend
npm install        # first time only (already done once, harmless to repeat)
npm run dev
```

Open http://localhost:5173.

The frontend calls the backend at `http://localhost:8000` (see `frontend/src/api.js`). To point it elsewhere, create `frontend/.env.local` with `VITE_API_URL=http://some-other-host:8000`.

---

## 4. Shut everything down

1. Frontend terminal: `Ctrl+C`
2. Backend terminal: `Ctrl+C`, then `deactivate`
3. Root: `docker compose down`

---

## 5. Troubleshooting

| Symptom | Cause → Fix |
|---------|-------------|
| `error during connect ... dockerDesktopLinuxEngine` | Docker Desktop isn't running → open it, wait for "Engine running". |
| `port is already allocated` (5432) on `docker compose up` | Another Postgres is running on your PC → stop it, or change `"5432:5432"` to `"5433:5432"` in `docker-compose.yml` and put `DATABASE_URL=...@localhost:5433/todo_db` in `backend/.env`. |
| Backend crashes at startup with `connection refused` / `OperationalError` | Postgres not up → `docker compose ps`, then `docker compose up -d`. |
| `uvicorn : The term 'uvicorn' is not recognized` | venv not activated in this terminal → `.\.venv\Scripts\Activate.ps1`. |
| `running scripts is disabled on this system` | See the `Set-ExecutionPolicy` fix in 2A. |
| `ModuleNotFoundError: No module named 'app'` | You ran uvicorn from the wrong folder → `cd backend` first. |
| Frontend shows `Failed to fetch` | Backend not running, or it crashed → check the backend terminal. |
| Browser console shows a **CORS** error | Frontend URL isn't in `CORS_ORIGINS` (default allows `http://localhost:5173` only). |
| `python` opens the Microsoft Store | Use `py` instead of `python` for the venv creation step: `py -m venv .venv`. |
