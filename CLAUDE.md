# todo-fastapi: project instructions

A learning project (FastAPI + React/Vite + Postgres in Docker), built phase by phase per `planning/ROADMAP.md`. The learner is new to Python/FastAPI and knows REST/Node.

## Notion sync (required)

The doc files below are mirrored to Notion under **theCode → Personal → todo-fastapi**. The repo files are the source of truth; sync goes one way, repo → Notion.

**Whenever you create or change one of these files, update its Notion page in the same session** (Notion MCP, fetch the page first, convert to Notion-flavored Markdown: `<table>` for tables, callouts for `>` notes, keep the grey "Synced from …" callout at the top):

| File | Notion page ID |
|------|----------------|
| (hub page: status, page list, layout) | `3ec00423-e96e-81e7-b90c-cc0a87a5a045` |
| `START-HERE.md` | `3ec00423-e96e-81f2-b239-cb4d6250f636` |
| `RUN.md` | `3ec00423-e96e-8125-a49e-e093aae1b005` |
| `learning/phase-01-crud-basics.md` | `3ec00423-e96e-812d-97a5-f55884f5b1c2` |
| `planning/ROADMAP.md` | `3ec00423-e96e-8165-a483-c64d68a9dc4c` |

- New phase learning file → create a new child page under the hub, add it to this table, and update the hub's status and page list.
- Phase completed → update the tracker in `ROADMAP.md`, the Roadmap page, and the hub status table.
- If the sync fails, tell the user. Don't skip it silently.

## Conventions

- Each phase delivers: code, an updated `RUN.md` if run steps change, `learning/phase-XX-*.md` (self-contained, includes the code), and an updated roadmap tracker.
- Writing `.env*` files is blocked by permissions; `config.py` has working defaults. Document env values in `RUN.md` instead.
- Test against the real Docker Postgres (`docker compose up -d`). Note that `ai-and-learning-db-1` also binds port 5432.
