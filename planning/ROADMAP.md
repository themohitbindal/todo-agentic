# FastAPI Learning Roadmap — from first route to production architecture

**Project:** one Todo app that grows phase by phase.
**Stack:** React + Vite (frontend) · FastAPI (backend) · Postgres in Docker (DB).
**Rule:** every phase ends with (1) working code, (2) a learning file in `learning/` that explains that phase end to end, so you can hand it to any AI or person and they get the whole picture.

## Progress tracker

| Phase | Name | Level | Status | Learning file |
|-------|------|-------|--------|---------------|
| 1 | CRUD and project layout | Beginner | ✅ Done | `learning/phase-01-crud-basics.md` |
| 2 | Requests, validation and errors in depth | Beginner+ | ⏳ Next | `learning/phase-02-requests-validation.md` |
| 3 | Config, migrations, layered architecture | Intermediate | ⬜ | `learning/phase-03-config-migrations-layers.md` |
| 4 | Dependency injection and request lifecycle | Intermediate | ⬜ | `learning/phase-04-dependency-injection.md` |
| 5 | Testing | Intermediate | ⬜ | `learning/phase-05-testing.md` |
| 6 | Users, auth and authorization | Intermediate+ | ⬜ | `learning/phase-06-auth.md` |
| 7 | Async FastAPI | Advanced | ⬜ | `learning/phase-07-async.md` |
| 8 | Real-world features | Advanced | ⬜ | `learning/phase-08-real-world-features.md` |
| 9 | Background jobs and events | Advanced | ⬜ | `learning/phase-09-background-jobs.md` |
| 10 | Production and deployment | Advanced | ⬜ | `learning/phase-10-production.md` |
| 11 | Architecture and internals | Expert | ⬜ | `learning/phase-11-architecture-internals.md` |

Why this order: each phase only needs what came before. Testing (5) comes **before** auth (6) and async (7), so those risky refactors are protected by tests.

---

## Phase 1: CRUD and project layout ✅
**Level:** Beginner · **Goal:** see FastAPI syntax once, end to end, in a structure that scales.

**Concepts**
- `FastAPI()` app object, Uvicorn (ASGI server), `--reload`
- Path operations: `@router.get/post/patch/delete`
- `APIRouter` with `prefix` and `tags`, and `app.include_router`
- Path params (`/todos/{todo_id}`) with automatic type conversion
- Request body = Pydantic model; automatic 422 validation errors
- `response_model` and `status_code`
- `HTTPException` for 404
- Dependency injection basics: `Depends(get_db)` with `yield`
- SQLAlchemy 2.0 ORM: `DeclarativeBase`, `Mapped`, `mapped_column`, `Session`
- Separating the ORM model (DB shape) from Pydantic schemas (API shape)
- CORS middleware so React can call the API
- Lifespan startup hook (`create_all`)
- Auto docs at `/docs`

**Built:** `GET /todos`, `GET /todos/{id}`, `POST /todos`, `PATCH /todos/{id}`, `DELETE /todos/{id}`, `GET /health`, plus a React UI that does all of them.

**Layout:** `main.py` → `routers/` → `crud/` → `models/`, with `schemas/` as the API contract.

---

## Phase 2: Requests, validation and errors in depth
**Level:** Beginner+ · **Goal:** master everything about how data gets **into** and **out of** an endpoint.

**Concepts**
- How FastAPI decides where a parameter comes from: path, query, body, header, cookie
- `Query()`, `Path()`, `Body()`, `Header()` with constraints (`ge`, `le`, `pattern`, aliases)
- `Annotated[...]`, the modern way to write all of the above
- Pydantic v2 in depth: `Field`, `field_validator`, `model_validator`, custom types, `EmailStr`, enums, `Literal`, strict mode
- PUT (full replace) vs PATCH (partial), and fixing the Phase 1 bug where `{"title": null}` on PATCH causes a 500
- Pagination (`limit`/`offset`), filtering (`?completed=true`), sorting (`?sort=-created_at`), search (`?q=`)
- Response envelopes (`{items, total, limit, offset}`) using generic Pydantic models
- `response_model_exclude_none`, multiple response types, `responses={404: ...}` for docs
- Custom exception classes and `@app.exception_handler`, plus one consistent error JSON format
- Overriding the default 422 format
- Status codes done right (201 + `Location` header, 204, 409 conflict)
- OpenAPI docs: summaries, descriptions, examples, tags metadata

**Build:** filters, sorting and pagination on the list endpoint; a `priority` enum field; a `due_date` with a validator (not in the past); consistent error format; React filter bar plus pagination.

**Done when:** you can predict, without running it, what FastAPI returns for any malformed request.

---

## Phase 3: Config, migrations, layered architecture
**Level:** Intermediate · **Goal:** make the project look like a real team codebase.

**Concepts**
- `pydantic-settings`: typed `Settings` class, `.env` files, per-environment config, `@lru_cache` settings dependency
- **Alembic** migrations: `init`, `revision --autogenerate`, `upgrade`/`downgrade`, why `create_all` is not enough, data migrations
- Layers: **router** (HTTP) → **service** (business rules) → **repository** (DB access); what belongs where
- API versioning: `/api/v1/...`
- A folder structure that scales: `app/core`, `app/api/v1/routes`, `app/services`, `app/repositories`, `app/models`, `app/schemas`
- Feature-based (by domain) vs layer-based structure, with trade-offs
- Logging setup with Python's `logging`

**Build:** move to settings + Alembic (drop `create_all`); add a migration that adds a column; split crud into service + repository; version the API.

**Done when:** you can add a new DB column through a migration, and explain why each layer exists.

---

## Phase 4: Dependency injection and request lifecycle
**Level:** Intermediate · **Goal:** understand FastAPI's core superpower and what actually happens per request.

**Concepts**
- What `Depends` really does: the dependency graph, sub-dependencies, per-request caching (`use_cache`)
- `yield` dependencies: setup/teardown, exceptions inside them, and the order of cleanup
- Class-based dependencies and callable instances (`__call__`)
- Router-level and app-level dependencies (`dependencies=[...]`)
- `app.dependency_overrides` (a preview of testing)
- Middleware: writing one (request timing, request ID, logging), plus middleware vs dependency
- `Request` object, `request.state`, `app.state`
- Lifespan in depth: sharing resources (DB engine, HTTP clients) app-wide
- ASGI basics: what Uvicorn hands to FastAPI (`scope`, `receive`, `send`)
- Transactions: one transaction per request (unit of work in the dependency)

**Build:** request-ID and timing middleware; a `get_todo_or_404` dependency; a commit/rollback-per-request session dependency; a common pagination dependency class.

**Done when:** you can draw the full lifecycle of one request, from socket to DB and back.

---

## Phase 5: Testing
**Level:** Intermediate · **Goal:** a test suite that lets you refactor without fear.

**Concepts**
- `pytest` basics: fixtures, scopes, parametrize, `conftest.py`
- `TestClient` (sync) and `httpx.AsyncClient` with `ASGITransport` (async)
- A real Postgres test DB (Docker), not SQLite, and why that matters
- Per-test isolation: wrap each test in a transaction and roll back
- `dependency_overrides` to swap the DB and fake services
- Unit tests (services) vs integration tests (routes plus DB)
- Factories for test data (`factory_boy` or simple builders)
- Coverage (`pytest-cov`); what is worth testing
- Frontend: Vitest + React Testing Library basics (light)

**Build:** full test suite for todos (happy paths, validation, 404, pagination), plus a `make test`-style script.

**Done when:** `pytest` is green and coverage is above 90% on `app/`.

---

## Phase 6: Users, auth and authorization
**Level:** Intermediate+ · **Goal:** multi-user todos, done securely.

**Concepts**
- `users` table plus a one-to-many relationship (`User.todos`), foreign keys, `relationship()`, cascade
- Password hashing (argon2/bcrypt via `pwdlib` or `passlib`), never storing plain passwords
- OAuth2 Password flow: `OAuth2PasswordBearer`, `OAuth2PasswordRequestForm`
- JWT: structure, signing, expiry, access vs refresh tokens
- A `get_current_user` dependency chain
- Authorization: users only see and edit **their own** todos (403 vs 404 choice)
- Roles and scopes (admin can see all)
- Security pitfalls: timing attacks, token storage in the browser (memory vs localStorage vs httpOnly cookie), CORS with credentials
- The "Authorize" button in `/docs`
- Frontend: login/register pages, auth context, attaching the token, handling 401

**Build:** register, login, me; todos scoped per user; React auth flow.

**Done when:** two browsers with two users never see each other's todos, and tests prove it.

---

## Phase 7: Async FastAPI
**Level:** Advanced · **Goal:** understand concurrency in Python web servers, not just use `async` keywords.

**Concepts**
- Event loop, coroutines, `await`: what actually runs concurrently
- `def` vs `async def` endpoints: FastAPI runs `def` in a **threadpool**; when each one is right
- The classic bug: blocking calls inside `async def` (and how to detect them)
- Async SQLAlchemy: `create_async_engine`, `AsyncSession`, `asyncpg` driver, `selectinload` (no lazy loading in async)
- Async dependencies and an async lifespan
- Calling other APIs with `httpx.AsyncClient`, `asyncio.gather` for parallel calls
- `BackgroundTasks` (fire-and-forget after the response)
- Benchmarking sync vs async with a load tool (`wrk`/`locust`/`oha`)

**Build:** migrate the whole backend to async; add an endpoint that calls an external API concurrently; benchmark before and after.

**Done when:** you can explain why an `async def` endpoint with `time.sleep(1)` freezes the whole server.

---

## Phase 8: Real-world features
**Level:** Advanced · **Goal:** the features real apps need, each teaching a new FastAPI capability.

**Concepts and features**
- **Tags**: a many-to-many relationship (association table)
- **Search**: Postgres full-text search (`tsvector`) plus an index
- **Cursor pagination** vs offset (why offset breaks at scale)
- **File attachments**: `UploadFile`, `multipart/form-data`, size and type limits, storing files on disk/S3, `FileResponse`/`StreamingResponse`
- **WebSockets**: live updates when a todo changes in another tab
- **Caching** with Redis (cache-aside, invalidation)
- **Rate limiting** (per user/IP)
- Optimistic concurrency (`version` column → 409 on stale updates)
- Soft delete and restore
- DB indexes and `EXPLAIN ANALYZE`

**Build:** each feature above in the todo app, plus the matching React UI.

---

## Phase 9: Background jobs and events
**Level:** Advanced · **Goal:** work that should not happen inside the HTTP request.

**Concepts**
- `BackgroundTasks` limits, and when you need a real queue
- Task queues: **Celery** or **ARQ/Dramatiq** with Redis as the broker; workers as a separate process
- Scheduled jobs (due-date reminders): Celery beat / APScheduler
- Sending email (a dev SMTP catcher like Mailpit in Docker)
- Retries, idempotency keys, dead-letter handling
- Domain events and the **transactional outbox** pattern
- Server-Sent Events (SSE) for progress updates

**Build:** "remind me" emails for due todos; a CSV export job with progress shown in React.

---

## Phase 10: Production and deployment
**Level:** Advanced · **Goal:** run it like a real service.

**Concepts**
- Dockerfile for the backend (multi-stage, non-root user, slim image) and the frontend (build → nginx)
- Full-stack `docker-compose` (db, redis, api, worker, web)
- Uvicorn workers / Gunicorn plus Uvicorn workers; how many workers and why
- Reverse proxy (nginx/Caddy), HTTPS, `root_path` / proxy headers
- Structured JSON logging, correlation IDs
- Health vs readiness endpoints; graceful shutdown
- Observability: Prometheus metrics, OpenTelemetry tracing
- Security hardening: security headers, strict CORS, secrets management, dependency scanning
- CI with GitHub Actions: lint (ruff), type check (mypy/pyright), tests, build images
- Generating a TypeScript client from `openapi.json` for the frontend
- Deploying to a cloud host (Render/Fly/Railway/a VPS)

**Build:** one command (`docker compose up`) runs the whole production-like stack; CI pipeline green.

---

## Phase 11: Architecture and internals
**Level:** Expert · **Goal:** understand *why* FastAPI works, and design systems beyond it.

**Concepts**
- **FastAPI internals:** how it is built on Starlette + Pydantic; how it reads type hints with `inspect` to build the dependency graph; how OpenAPI is generated; how routing matches
- **Write a tiny framework** on raw ASGI (about 100 lines) to demystify it all
- **Clean / hexagonal architecture:** domain entities vs ORM models, ports and adapters, repository interfaces, Unit of Work
- When that is over-engineering, and how to choose
- CQRS-lite: separate read models from write models
- Modular monolith vs microservices; splitting a module out
- Performance: profiling (py-spy), N+1 queries, connection pool tuning, load testing
- Pydantic performance, `orjson`, response serialization costs

**Build:** refactor the todo domain into hexagonal style in a branch and compare it with the layered version; build the mini ASGI framework.

**Done when:** you can explain FastAPI's request handling at the level of "what happens in Starlette's router and FastAPI's `solve_dependencies`".

---

## How each phase is delivered

1. Code changes in `backend/` and `frontend/`
2. Updated `RUN.md` if any new service or command is added (Redis, worker, ...)
3. A new `learning/phase-XX-*.md` with: the architecture diagram, what changed and why, a file-by-file walkthrough with the code, syntax explained, common mistakes, exercises, and questions to ask an AI
4. This tracker updated
