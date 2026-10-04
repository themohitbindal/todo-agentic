# Phase 1: FastAPI CRUD and project layout

> **How to use this file:** it is self-contained. Paste it into ChatGPT (or any AI) and ask questions like "explain section 6 like I'm a Node developer" or "quiz me on this phase". All the code for the phase is included below.

**Learner background:** knows REST APIs (likely from Node/Express), new to Python and FastAPI.
**Phase goal:** see the FastAPI syntax once, end to end, in a folder structure that will scale in later phases.

---

## 1. TL;DR

- **FastAPI** is a Python web framework. You write normal Python functions with **type hints**, and FastAPI uses those hints to parse requests, validate data, convert types, inject dependencies, and generate API docs automatically.
- **Uvicorn** is the server that runs the app (like Node's `http` server; FastAPI itself is only the app).
- **Pydantic** models (schemas) define the JSON shape going in and out. Bad input automatically gets a **422** response.
- **SQLAlchemy** is the ORM (like Prisma/Sequelize/TypeORM). Its models define the DB tables.
- **`Depends(get_db)`** gives each request its own DB session and closes it afterwards. This is dependency injection.
- Code is split by job: `routers/` (HTTP) → `crud/` (DB work) → `models/` (tables), with `schemas/` as the API contract.

---

## 2. Stack and versions

| Layer | Tech | Version |
|-------|------|---------|
| Frontend | React + Vite | React 19, Vite 8 |
| Backend framework | FastAPI | 0.142 |
| ASGI server | Uvicorn (comes with `fastapi[standard]`) | 0.54 |
| Validation | Pydantic v2 (comes with FastAPI) | 2.13 |
| ORM | SQLAlchemy 2.x (2.0-style API) | 2.1 |
| DB driver | psycopg 3 (`postgresql+psycopg://`) | 3.3 |
| DB | Postgres in Docker | 16 |
| Python | CPython | 3.12 |

---

## 3. Big picture: what talks to what

```
┌───────────────────────┐   HTTP + JSON    ┌──────────────────────────────────────────────┐   SQL    ┌────────────┐
│ React (Vite :5173)    │ ───────────────▶ │ Uvicorn (:8000)  ── ASGI ──▶  FastAPI app    │ ───────▶ │ Postgres   │
│  src/api.js  fetch()  │ ◀─────────────── │   CORS middleware → router → path function   │ ◀─────── │ (Docker    │
└───────────────────────┘                  │        ↳ Depends(get_db) → crud → SQLAlchemy │          │  :5432)    │
                                           └──────────────────────────────────────────────┘          └────────────┘
```

**ASGI** (Asynchronous Server Gateway Interface) is the contract between a Python server (Uvicorn) and a Python app (FastAPI). In Node the server and framework are glued together; in Python they are separate pieces that speak ASGI.

---

## 4. Folder structure: what each file is for

```
todo-fastapi/
├── docker-compose.yml          # Postgres container
├── RUN.md                      # how to start everything
├── planning/ROADMAP.md         # all phases
├── learning/                   # one file like this per phase
├── backend/
│   ├── requirements.txt        # Python deps (like package.json "dependencies")
│   └── app/                    # the Python package; "app.main" = app/main.py
│       ├── __init__.py         # empty; marks the folder as a Python package
│       ├── main.py             # creates FastAPI(), adds middleware, mounts routers
│       ├── config.py           # reads env vars (DATABASE_URL, CORS_ORIGINS)
│       ├── database.py         # engine, SessionLocal, Base, get_db dependency
│       ├── models/
│       │   ├── __init__.py     # imports all models (so tables get registered)
│       │   └── todo.py         # SQLAlchemy model → "todos" table
│       ├── schemas/
│       │   ├── __init__.py
│       │   └── todo.py         # Pydantic: TodoCreate / TodoUpdate / TodoRead
│       ├── crud/
│       │   └── todo.py         # DB functions: list/get/create/update/delete
│       └── routers/
│           └── todos.py        # HTTP endpoints for /todos
└── frontend/
    └── src/
        ├── api.js              # all fetch calls to the backend
        ├── App.jsx             # UI: list, add, toggle, edit, delete
        └── main.jsx, index.css
```

### The layers and their single job

| Layer | Folder | Knows about HTTP? | Knows about DB? | Express equivalent |
|-------|--------|-------------------|-----------------|--------------------|
| Entry | `main.py` | yes | only to create tables | `app.js` / `server.js` |
| Routing / controller | `routers/` | **yes** (status codes, 404) | no, calls crud | `routes/todos.js` + controller |
| Data access | `crud/` | **no** | **yes** | service / repository / Prisma calls |
| DB tables | `models/` | no | yes | Prisma schema / Sequelize model |
| API contract | `schemas/` | describes JSON | no | Joi/Zod validators + DTO types |
| Wiring | `database.py`, `config.py` | — | — | `db.js`, `config.js` |

**Rule of thumb:** the router never writes SQL, and crud never raises HTTP errors. This separation becomes important in Phase 3.

---

## 5. Endpoints built in this phase

| Method | Path | Body | Success | Errors |
|--------|------|------|---------|--------|
| GET | `/todos` | — | 200 `TodoRead[]` | — |
| GET | `/todos/{todo_id}` | — | 200 `TodoRead` | 404, 422 (id not int) |
| POST | `/todos` | `TodoCreate` | **201** `TodoRead` | 422 |
| PATCH | `/todos/{todo_id}` | `TodoUpdate` (partial) | 200 `TodoRead` | 404, 422 |
| DELETE | `/todos/{todo_id}` | — | **204** no body | 404 |
| GET | `/health` | — | 200 `{"status":"ok"}` | — |

Example `TodoRead` JSON:

```json
{
  "id": 1,
  "title": "Learn FastAPI",
  "description": null,
  "completed": false,
  "created_at": "2026-10-01T17:25:40Z",
  "updated_at": "2026-10-01T17:25:40Z"
}
```

---

## 6. Life of one request: `POST /todos`

1. React calls `fetch("http://localhost:8000/todos", {method: "POST", body: '{"title":"Learn"}'})`.
2. The browser sees a different origin (port 5173 → 8000) and first sends an **OPTIONS preflight**. `CORSMiddleware` answers "yes, 5173 is allowed".
3. The real POST arrives at **Uvicorn**, which converts it into an ASGI call to the FastAPI `app`.
4. FastAPI's router matches `POST /todos` → `create_todo` in `routers/todos.py`.
5. FastAPI inspects the function signature `create_todo(data: TodoCreate, db: DbSession)`:
   - `data: TodoCreate` is a Pydantic model, so it reads the **JSON body** and validates it. If invalid, it stops here and returns **422** with details. The function never runs.
   - `db: DbSession` is `Annotated[Session, Depends(get_db)]`, so it calls `get_db()`, runs it up to `yield`, and passes the session in.
6. The function body calls `crud.create_todo(db, data)`, which builds a `Todo` ORM object, `add` → `commit` (SQL `INSERT`) → `refresh` (reload `id`, `created_at` from the DB).
7. The function returns the ORM object. FastAPI passes it through `response_model=TodoRead`, which reads its attributes (thanks to `from_attributes=True`), filters to only the declared fields, and serializes to JSON.
8. The status code is **201** because of `status_code=201` on the decorator.
9. After the response, FastAPI resumes `get_db()` after the `yield` → the `finally:` block runs → `db.close()`.

---

## 7. The code, file by file

### 7.1 `backend/app/main.py`: the app

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registers the tables on Base.metadata)
from app.config import CORS_ORIGINS
from app.database import Base, engine
from app.routers import todos


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on startup. Creates missing tables.
    # (Phase 3 replaces this with Alembic migrations.)
    Base.metadata.create_all(bind=engine)
    yield
    # Code after `yield` runs once on shutdown.


app = FastAPI(title="Todo API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todos.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
```

**Syntax notes**
- `app = FastAPI(...)` works like `const app = express()`. Uvicorn is told "`app.main:app`", meaning the module `app/main.py` and its variable `app`.
- `@app.get("/health")` is a **decorator**. It registers the function below it as the handler for `GET /health`, much like `app.get("/health", handler)` in Express.
- Returning a `dict` automatically becomes JSON. No `res.json()` needed.
- `lifespan` is a startup/shutdown hook. Everything before `yield` runs at startup, everything after at shutdown.
- `from app import models` looks unused, but importing it runs `models/__init__.py`, which imports `Todo`, which registers the `todos` table on `Base.metadata`. Without it, `create_all` would create nothing. (`# noqa: F401` tells linters "this unused import is on purpose".)
- `include_router` is like `app.use(router)`.

### 7.2 `backend/app/config.py`: settings

```python
import os
from dotenv import load_dotenv

load_dotenv()  # reads backend/.env into os.environ if it exists

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://todo_user:todo_pass@localhost:5432/todo_db",
)

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
]
```

- `os.getenv(name, default)` works like `process.env.NAME ?? default`.
- `[x.strip() for x in ...]` is a **list comprehension**, like `.split(",").map(x => x.trim())`.
- URL format: `postgresql+psycopg://user:pass@host:port/db`. The `+psycopg` part tells SQLAlchemy which driver to use.
- Phase 3 upgrades this to typed `pydantic-settings`.

### 7.3 `backend/app/database.py`: DB wiring and the first dependency

```python
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Every ORM model inherits from this. Base.metadata knows about all tables."""


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]
```

| Thing | What it is |
|-------|------------|
| `engine` | Owns the **connection pool** to Postgres. One per app. |
| `SessionLocal` | A *factory*. `SessionLocal()` creates a new `Session`. |
| `Session` | A unit of work: tracks objects you add/change, and sends SQL on `commit()`. One per request. |
| `Base` | Parent class for all models. `Base.metadata` = registry of all tables. |
| `get_db` | A **generator** function (has `yield`). FastAPI runs it until `yield`, injects the value, then after the response finishes the rest (`finally: close`). |
| `DbSession` | A reusable type alias. `Annotated[Session, Depends(get_db)]` means "the type is `Session`, and FastAPI should get it by calling `get_db`". |

`expire_on_commit=False` keeps object attributes readable after `commit()`, so we can return the object without extra queries.

**Why a dependency instead of a global session?** Each request gets its own isolated session, it is always closed (even on errors), and in tests you can swap it out with `app.dependency_overrides[get_db] = fake_get_db` (Phase 5).

### 7.4 `backend/app/models/todo.py`: the table (SQLAlchemy ORM)

```python
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

Resulting SQL (roughly):

```sql
CREATE TABLE todos (
  id          SERIAL PRIMARY KEY,
  title       VARCHAR(200) NOT NULL,
  description TEXT,                         -- nullable because of `str | None`
  completed   BOOLEAN NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

- `Mapped[str]` means NOT NULL; `Mapped[str | None]` means nullable. The **type hint decides nullability**.
- `default=False` is applied by Python on insert. `server_default=func.now()` is applied by Postgres (`DEFAULT now()`).
- `onupdate=func.now()` makes SQLAlchemy set `updated_at = now()` on every UPDATE.
- `str | None` is Python's union type, like TypeScript's `string | null`.

### 7.5 `backend/app/schemas/todo.py`: the API contract (Pydantic)

```python
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TodoBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None


class TodoCreate(TodoBase):
    """Body for POST /todos."""


class TodoUpdate(BaseModel):
    """Body for PATCH /todos/{id}. Every field optional."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    completed: bool | None = None


class TodoRead(TodoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime
```

**Why three schemas plus one model? (The most important idea of this phase.)**

| Class | Used for | Has `id`? | Fields required? |
|-------|----------|-----------|------------------|
| `Todo` (SQLAlchemy, `models/`) | the DB row | yes | — |
| `TodoCreate` | what the client may send on create | **no** (DB makes it) | `title` required |
| `TodoUpdate` | what the client may send on PATCH | no | all optional |
| `TodoRead` | what the API sends back | yes | all present |

If you used one class for everything, clients could send their own `id` or `created_at`, and you might accidentally leak DB-only columns (like a future `password_hash`). Separate input and output schemas are the standard FastAPI pattern.

- `Field(min_length=1, max_length=200)` adds validation. An empty title returns 422.
- `= None` makes a field optional with a default.
- `class TodoCreate(TodoBase): """..."""` is inheritance with nothing added (the docstring is the body, like `pass`).
- `from_attributes=True` lets Pydantic build a `TodoRead` from an **object** (`todo.title`), not only from a dict. That is what lets routes `return` ORM objects directly.

### 7.6 `backend/app/crud/todo.py`: DB operations

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Todo
from app.schemas import TodoCreate, TodoUpdate


def list_todos(db: Session) -> list[Todo]:
    return list(db.scalars(select(Todo).order_by(Todo.id)))


def get_todo(db: Session, todo_id: int) -> Todo | None:
    return db.get(Todo, todo_id)


def create_todo(db: Session, data: TodoCreate) -> Todo:
    todo = Todo(**data.model_dump())
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def update_todo(db: Session, todo: Todo, data: TodoUpdate) -> Todo:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo: Todo) -> None:
    db.delete(todo)
    db.commit()
```

| Code | Meaning | JS / SQL analogy |
|------|---------|------------------|
| `select(Todo).order_by(Todo.id)` | build a query | `SELECT * FROM todos ORDER BY id` |
| `db.scalars(query)` | run it, return ORM objects | `prisma.todo.findMany()` |
| `db.get(Todo, 5)` | find by primary key, or `None` | `findUnique({where:{id:5}})` |
| `data.model_dump()` | Pydantic model → dict | `{...data}` |
| `Todo(**some_dict)` | `**` unpacks a dict into keyword args | `new Todo({...dict})` |
| `db.add(obj)` | stage an INSERT | — |
| `db.commit()` | send SQL and commit the transaction | `COMMIT` |
| `db.refresh(obj)` | re-read the row (gets `id`, timestamps) | `SELECT ... WHERE id=` |
| `model_dump(exclude_unset=True)` | only the fields the client **actually sent** | — |
| `setattr(obj, "title", v)` | `obj.title = v` with a dynamic name | `obj[field] = v` |

`exclude_unset=True` is what makes PATCH partial. If the client sends `{"completed": true}`, only `completed` is updated and `title` is left alone.

### 7.7 `backend/app/routers/todos.py`: HTTP endpoints

```python
from fastapi import APIRouter, HTTPException, status

from app.crud import todo as crud
from app.database import DbSession
from app.schemas import TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


def get_todo_or_404(db: DbSession, todo_id: int):
    todo = crud.get_todo(db, todo_id)
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo


@router.get("", response_model=list[TodoRead])
def list_todos(db: DbSession):
    return crud.list_todos(db)


@router.get("/{todo_id}", response_model=TodoRead)
def read_todo(todo_id: int, db: DbSession):
    return get_todo_or_404(db, todo_id)


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(data: TodoCreate, db: DbSession):
    return crud.create_todo(db, data)


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, data: TodoUpdate, db: DbSession):
    todo = get_todo_or_404(db, todo_id)
    return crud.update_todo(db, todo, data)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: DbSession):
    todo = get_todo_or_404(db, todo_id)
    crud.delete_todo(db, todo)
```

**How FastAPI decides where each parameter comes from** (the core magic):

| Parameter looks like… | FastAPI reads it from | Example here |
|-----------------------|-----------------------|--------------|
| name appears in the path `{...}` | **path** | `todo_id: int` in `/{todo_id}` |
| simple type (`int`, `str`, `bool`) not in the path | **query string** | (none yet; Phase 2: `?completed=true`) |
| Pydantic model | **JSON body** | `data: TodoCreate` |
| `Depends(...)` / `Annotated[..., Depends(...)]` | **dependency function** | `db: DbSession` |

Type hints also **convert and validate**: `todo_id: int` turns `"5"` from the URL into `5`, and `/todos/abc` returns 422 automatically.

**Other notes**
- `APIRouter(prefix="/todos")` is like `express.Router()` mounted at `/todos`. The path `""` means `/todos` exactly. (Using `"/"` would mean `/todos/` with a trailing slash, and FastAPI would redirect.)
- `tags=["todos"]` groups the endpoints in `/docs`.
- `response_model=TodoRead` filters and validates output, and documents it. Even if the ORM object had extra fields, only `TodoRead` fields are returned.
- `raise HTTPException(404, detail=...)` returns `{"detail": "Todo not found"}` with status 404. You **raise**, not return. It works from any depth of function calls.
- `status.HTTP_201_CREATED` is just the constant `201`, more readable.
- DELETE returns nothing, so FastAPI sends 204 with an empty body.
- `from app.crud import todo as crud` imports the module and gives it an alias, so we call `crud.create_todo(...)`.

---

## 8. Validation errors: what a 422 looks like

`POST /todos` with `{"title": ""}` returns:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": { "min_length": 1 }
    }
  ]
}
```

`loc` tells you exactly where the problem is (`body` → `title`). You wrote **zero** validation code for this; it comes from the type hints plus `Field`. The React `api.js` turns this list into a readable message.

---

## 9. Free docs: `/docs`, `/redoc`, `/openapi.json`

FastAPI generates an **OpenAPI** spec from your routes, type hints, and schemas. `/docs` (Swagger UI) lets you call every endpoint from the browser. Because it is generated from code, it is never out of date. In Phase 10 we generate a TypeScript client from `/openapi.json`.

---

## 10. CORS: why the middleware is needed

The browser treats `http://localhost:5173` (React) and `http://localhost:8000` (API) as **different origins**. By default it blocks JS from reading responses from another origin unless the server sends `Access-Control-Allow-Origin`. `CORSMiddleware` adds those headers for the origins in `CORS_ORIGINS`. Swagger `/docs` works without CORS because it is served from the same origin as the API.

---

## 11. Frontend side

`frontend/src/api.js` is the only place that knows URLs:

```js
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export const listTodos  = ()         => request("/todos");
export const createTodo = (data)     => request("/todos",      { method: "POST",  body: JSON.stringify(data) });
export const updateTodo = (id, data) => request(`/todos/${id}`, { method: "PATCH", body: JSON.stringify(data) });
export const deleteTodo = (id)       => request(`/todos/${id}`, { method: "DELETE" });
```

`App.jsx` mapping: page load → `GET /todos`; the Add form → `POST`; the checkbox → `PATCH {completed}`; double-clicking a title → `PATCH {title}`; the Delete button → `DELETE`. After each call, it updates local React state with the server's response, so no refetch is needed.

---

## 12. Express → FastAPI cheat sheet

| Express / Node | FastAPI / Python |
|----------------|------------------|
| `const app = express()` | `app = FastAPI()` |
| `app.get("/x", (req, res) => ...)` | `@app.get("/x")` + `def handler(): ...` |
| `express.Router()` + `app.use("/todos", r)` | `APIRouter(prefix="/todos")` + `app.include_router(r)` |
| `req.params.id` | function param `todo_id: int` matching `{todo_id}` |
| `req.query.done` | function param `done: bool` (not in the path) |
| `req.body` + Joi/Zod validation | function param `data: SomePydanticModel` |
| `res.status(201).json(obj)` | `status_code=201` on decorator + `return obj` |
| `res.status(404).json({...})` | `raise HTTPException(404, detail=...)` |
| `app.use(cors())` | `app.add_middleware(CORSMiddleware, ...)` |
| middleware injecting `req.db` | `db: Annotated[Session, Depends(get_db)]` |
| Prisma / Sequelize | SQLAlchemy |
| `package.json` / `node_modules` | `requirements.txt` / `.venv` |
| `nodemon` | `uvicorn --reload` |
| `process.env.X` | `os.getenv("X")` |
| Swagger via extra libs | built in: `/docs` |

---

## 13. Python syntax primer for JS developers (only what this phase uses)

| Python | Meaning / JS equivalent |
|--------|-------------------------|
| `def f(x: int) -> str:` | function with type hints (like TS types, but FastAPI **uses them at runtime**) |
| `str \| None` | `string \| null` |
| `@decorator` above a function | wraps or registers the function (`app.get(path, fn)`) |
| `class A(B):` | `class A extends B` |
| `"""docstring"""` | doc comment; also counts as a class/function body |
| `None`, `True`, `False` | `null`, `true`, `false` |
| `[x for x in items]` | `items.map(x => x)` |
| `**d` in a call | spread an object into named args |
| `for k, v in d.items():` | `for (const [k, v] of Object.entries(d))` |
| `try / finally` | same as JS |
| `yield` | pause the function, hand out a value, resume later (generator) |
| `with x as y:` / `async with` | context manager (auto setup/cleanup) |
| `from a.b import c` | `import { c } from "a/b"` |
| `__init__.py` | makes a folder an importable package (like an `index.js`) |
| indentation | Python's `{ }`; it is syntax, not style |

---

## 14. Intentional limitations (fixed in later phases)

| Limitation | Why it's a problem | Fixed in |
|------------|--------------------|----------|
| `create_all()` on startup | can't change existing tables (add/rename columns) | Phase 3 (Alembic) |
| `os.getenv` config | no types, no validation | Phase 3 |
| PATCH with `{"title": null}` gives a **500** | `TodoUpdate` allows `None`, the DB column is NOT NULL | Phase 2 |
| list returns everything | no pagination/filter/sort | Phase 2 |
| errors are not uniform | 404 is `{"detail": str}`, 422 is `{"detail": [...]}` | Phase 2 |
| commit inside each crud function | can't group several operations in one transaction | Phase 4 |
| no tests | refactors are risky | Phase 5 |
| no users | everyone shares all todos | Phase 6 |
| sync `def` + sync DB driver | fine for now; threadpool limits at scale | Phase 7 |

---

## 15. Exercises (do these to really learn it)

1. In `/docs`, create 3 todos, PATCH one, DELETE one. Then check `SELECT * FROM todos;` in `psql` (see RUN.md).
2. Call `GET /todos/abc` and `POST /todos` with `{}`. Read the 422 bodies. What does `loc` tell you?
3. Add `GET /todos/count` returning `{"count": n}`. **Gotcha:** put it *above* `/{todo_id}`, otherwise FastAPI tries to parse `"count"` as an int. Why?
4. Add a query param: `def list_todos(db: DbSession, completed: bool | None = None)` and filter in crud. Try `/todos?completed=true`.
5. Add a `priority: int` field with `Field(ge=1, le=5, default=3)`. You'll need it in the model **and** the schemas, and since `create_all` won't alter an existing table, you'll have to `docker compose down -v` (feel the pain that Alembic fixes in Phase 3).
6. Remove `response_model=TodoRead` from one route and add a secret field to the model. What leaks?
7. Send `{"title": null}` with PATCH and watch it 500. Think about how you'd fix it (Phase 2 answer).

---

## 16. Questions to ask an AI about this phase

- "What does FastAPI do with the type hints of a path operation function, step by step?"
- "Explain `yield` dependencies and exactly when the code after `yield` runs."
- "Why separate SQLAlchemy models from Pydantic schemas? Give a security example."
- "What is ASGI, and how is Uvicorn different from FastAPI?"
- "What does `from_attributes=True` do internally?"
- "Why is `exclude_unset` different from `exclude_none`?"
- "What happens if I define `/todos/{id}` before `/todos/count`?"
- "Explain SQLAlchemy Session, unit of work, and identity map simply."

---

## 17. Glossary

- **Path operation**: an endpoint (path + HTTP method + function).
- **Dependency**: a function FastAPI calls for you and injects the result of (`Depends`).
- **Schema / Pydantic model**: a class that defines and validates a JSON shape.
- **ORM model**: a class mapped to a DB table (SQLAlchemy).
- **Session**: SQLAlchemy's per-request unit of work and DB conversation.
- **Engine**: SQLAlchemy's connection pool and DB entry point.
- **ASGI**: the standard interface between Python async servers and apps.
- **Uvicorn**: the ASGI server that runs FastAPI.
- **OpenAPI**: the machine-readable API spec FastAPI generates (`/openapi.json`).
- **CORS**: browser rules for cross-origin requests.
- **venv**: Python's per-project isolated package folder (like `node_modules`).
